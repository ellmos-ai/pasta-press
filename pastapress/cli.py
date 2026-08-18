import click
import os
from .core import PastaPressCore
from .queue_manager import QueueManager
from .config import CONFIG, logger

@click.group()
def cli():
    """PastaPress - Stylistic text refinement via local Ollama."""
    pass

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--overwrite', is_flag=True, help='Overwrite original file.')
@click.option('--output-dir', type=click.Path(), help='Custom output directory.')
@click.option('--suffix', type=str, help='Suffix for the output file (if not overwritten).')
def process(input_path, overwrite, output_dir, suffix):
    """Process a single file or add all files in a directory to the queue."""
    if os.path.isfile(input_path):
        core = PastaPressCore()
        success = core.process_file(input_path, overwrite, output_dir, suffix)
        if success:
            click.echo(f"Successfully processed: {input_path}")
        else:
            click.echo(f"Failed to process: {input_path}")
    elif os.path.isdir(input_path):
        qm = QueueManager()
        for root, _, files in os.walk(input_path):
            for file in files:
                # Basic filter for text files
                if file.endswith(('.txt', '.md', '.markdown', '.csv', '.json', '.yaml', '.yml')):
                    file_path = os.path.join(root, file)
                    qm.add({
                        "path": file_path,
                        "overwrite": overwrite,
                        "output_dir": output_dir,
                        "suffix": suffix
                    })
        click.echo(f"Added files from {input_path} to the queue.")
        click.echo("Run 'pastapress process-queue' to start processing.")

@cli.command()
def process_queue():
    """Process all files currently in the queue sequentially."""
    qm = QueueManager()
    if qm.is_empty():
        click.echo("Queue is empty. Nothing to process.")
        return
        
    core = PastaPressCore()
    while not qm.is_empty():
        item = qm.pop()
        if item:
            path = item.get("path")
            overwrite = item.get("overwrite", False)
            output_dir = item.get("output_dir")
            suffix = item.get("suffix")
            
            click.echo(f"Processing from queue: {path}")
            core.process_file(path, overwrite, output_dir, suffix)
            
    click.echo("Queue processing completed.")

@cli.command()
@click.argument('text', type=str)
@click.option('--save-as', type=click.Path(), help='Save output directly to this file path.')
def text(text, save_as):
    """Process a direct text string (useful for agent integrations)."""
    core = PastaPressCore()
    result = core.process_text_string(text)
    
    if save_as:
        with open(save_as, 'w', encoding='utf-8') as f:
            f.write(result)
        click.echo(f"Result saved to {save_as}")
    else:
        click.echo(result)

@cli.command()
@click.option('--auto', is_flag=True, help='Automatically select the best available model.')
@click.option('--model', type=str, help='Manually set a specific model.')
@click.option('--host', type=str, help='Update the Ollama host URL.')
def config(auto, model, host):
    """Configure the Ollama profile and model."""
    from .config import load_config, save_config, CONFIG
    from .ollama_utils import configure_ollama_profile, get_available_models
    
    current_config = load_config()
    updated = False
    
    if host:
        current_config['ollama_host'] = host
        updated = True
        click.echo(f"Updated Ollama host to: {host}")
        
    if auto:
        selected_model = configure_ollama_profile(host=current_config['ollama_host'], auto_select=True)
        if selected_model:
            current_config['model'] = selected_model
            updated = True
            click.echo(f"Updated model profile to: {selected_model}")
    elif model:
        # Check if the manually provided model actually exists on the host
        available_models = get_available_models(host=current_config['ollama_host'])
        if available_models and model not in available_models:
             click.echo(f"Warning: Model '{model}' was not found on the Ollama server. Available models are: {', '.join(available_models)}")
        
        current_config['model'] = model
        updated = True
        click.echo(f"Manually updated model profile to: {model}")
    else:
        # Just list current config and available models
        click.echo("Current Configuration:")
        for k, v in current_config.items():
            click.echo(f"  {k}: {v}")
            
        click.echo("\nTo change settings, use options like --model <name>, --host <url>, or --auto.")
        configure_ollama_profile(host=current_config['ollama_host'], auto_select=False)
        
    if updated:
        save_config(current_config)
        click.echo("Configuration saved.")

if __name__ == '__main__':
    cli()
