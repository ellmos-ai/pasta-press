import click
import os
from .core import PastaPressCore
from .queue_manager import QueueManager
from .config import CONFIG, logger
from .document_parser import SUPPORTED_FORMATS

STYLE_CHOICES = click.Choice(['original', 'gleichwertig', 'wissenschaftlich', 'einfach', 'kurz'])


@click.group()
def cli():
    """PastaPress - Stylistic text refinement via local Ollama."""
    pass


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--overwrite', is_flag=True, help='Overwrite original file.')
@click.option('--output-dir', type=click.Path(), help='Custom output directory.')
@click.option('--suffix', type=str, help='Suffix for the output file (if not overwritten).')
@click.option('--style', type=STYLE_CHOICES, help='Override config style level.')
@click.option('--translate', type=str, help='Target language (e.g. English) - enables translation mode.')
def process(input_path, overwrite, output_dir, suffix, style, translate):
    """Process a single file or add all files in a directory to the queue."""
    if os.path.isfile(input_path):
        core = PastaPressCore()
        success = core.process_file(input_path, overwrite, output_dir, suffix, style, translate)
        if success:
            if core.last_failed_chunks:
                click.echo(f"Processed with warnings: {input_path} "
                           f"({core.last_failed_chunks}/{core.last_total_chunks} chunks kept unmodified due to errors)")
            else:
                click.echo(f"Successfully processed: {input_path}")
        else:
            click.echo(f"Failed to process: {input_path}")
            raise SystemExit(1)
    elif os.path.isdir(input_path):
        effective_suffix = suffix if suffix else CONFIG.get("output_suffix", "_pasta-press")
        qm = QueueManager()
        added = 0
        for root, _, files in os.walk(input_path):
            for file in files:
                name, ext = os.path.splitext(file)
                if ext.lower() not in SUPPORTED_FORMATS:
                    continue
                # Skip files that are already PastaPress output — otherwise a
                # second run over the same folder would press them again.
                if effective_suffix and name.endswith(effective_suffix):
                    continue
                file_path = os.path.join(root, file)
                qm.add({
                    "path": file_path,
                    "overwrite": overwrite,
                    "output_dir": output_dir,
                    "suffix": suffix,
                    "style": style,
                    "translate": translate
                })
                added += 1
        click.echo(f"Added {added} file(s) from {input_path} to the queue.")
        if added:
            click.echo("Run 'pastapress process-queue' to start processing.")


@cli.command()
def process_queue():
    """Process all files currently in the queue sequentially."""
    qm = QueueManager()
    if qm.is_empty():
        click.echo("Queue is empty. Nothing to process.")
        return

    core = PastaPressCore()
    failures = 0
    while not qm.is_empty():
        item = qm.pop()
        if item:
            path = item.get("path")
            overwrite = item.get("overwrite", False)
            output_dir = item.get("output_dir")
            suffix = item.get("suffix")
            style = item.get("style")
            translate = item.get("translate")

            click.echo(f"Processing from queue: {path}")
            if not core.process_file(path, overwrite, output_dir, suffix, style, translate):
                failures += 1
                click.echo(f"Failed to process: {path}")

    if failures:
        click.echo(f"Queue processing completed with {failures} failure(s).")
    else:
        click.echo("Queue processing completed.")


@cli.command()
@click.argument('text', type=str)
@click.option('--save-as', type=click.Path(), help='Save output directly to this file path.')
@click.option('--style', type=STYLE_CHOICES, help='Override config style level.')
@click.option('--translate', type=str, help='Target language (e.g. English) - enables translation mode.')
def text(text, save_as, style, translate):
    """Process a direct text string (useful for agent integrations)."""
    core = PastaPressCore()
    result = core.process_text_string(text, style, translate)

    if core.last_total_chunks > 0 and core.last_failed_chunks == core.last_total_chunks:
        click.echo("Processing failed: the LLM could not be reached for any chunk.", err=True)
        raise SystemExit(1)

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
@click.option('--style', type=STYLE_CHOICES, help='Set default text refinement style.')
@click.option('--translate-mode', type=click.Choice(['on', 'off']), help='Turn translation mode on or off.')
@click.option('--lang', type=str, help='Set default target language for translation.')
@click.option('--thinking', type=click.Choice(['on', 'off']), help="Model reasoning/thinking ('off' is ~10x faster, default).")
def config(auto, model, host, style, translate_mode, lang, thinking):
    """Configure the Ollama profile and model."""
    from .config import load_config, save_config
    from .ollama_utils import configure_ollama_profile, get_available_models

    current_config = load_config()
    updated = False

    if host:
        current_config['ollama_host'] = host
        updated = True
        click.echo(f"Updated Ollama host to: {host}")

    if style:
        current_config['style'] = style
        updated = True
        click.echo(f"Updated default style to: {style}")

    if translate_mode:
        is_on = translate_mode == 'on'
        current_config['translation_mode'] = is_on
        updated = True
        click.echo(f"Updated translation_mode to: {is_on}")

    if lang:
        current_config['target_language'] = lang
        updated = True
        click.echo(f"Updated target_language to: {lang}")

    if thinking:
        current_config['disable_thinking'] = (thinking == 'off')
        updated = True
        click.echo(f"Updated thinking to: {thinking}")

    configured_host = current_config.get('ollama_host')

    if auto:
        selected_model = configure_ollama_profile(host=configured_host, auto_select=True)
        if selected_model:
            current_config['model'] = selected_model
            updated = True
            click.echo(f"Updated model profile to: {selected_model}")
    elif model:
        # Check if the manually provided model actually exists on the host
        available_models = get_available_models(host=configured_host)
        if available_models and model not in available_models:
            click.echo(f"Warning: Model '{model}' was not found on the Ollama server. "
                       f"Available models are: {', '.join(available_models)}")

        current_config['model'] = model
        updated = True
        click.echo(f"Manually updated model profile to: {model}")
    elif not updated:
        # Just list current config and available models
        click.echo("Current Configuration:")
        for k, v in current_config.items():
            click.echo(f"  {k}: {v}")

        click.echo("\nTo change settings, use options like --model <name>, --style <style>, or --translate-mode on/off.")
        configure_ollama_profile(host=configured_host, auto_select=False)

    if updated:
        save_config(current_config)
        click.echo("Configuration saved.")


if __name__ == '__main__':
    cli()
