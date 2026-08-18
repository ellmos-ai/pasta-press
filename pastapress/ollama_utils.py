import requests
from pastapress.config import CONFIG, logger

def get_available_models(host=None):
    """Fetches a list of available models from the local Ollama instance."""
    host = host or CONFIG.get("ollama_host")
    api_url = f"{host.rstrip('/')}/api/tags"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        models = [model['name'] for model in data.get('models', [])]
        return models
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch available models from Ollama: {e}")
        return []

def configure_ollama_profile(host=None, auto_select=False):
    """Configures the Ollama profile, auto-detecting the best model or listing options."""
    host = host or CONFIG.get("ollama_host")
    models = get_available_models(host)
    
    if not models:
        logger.error("No models found on the Ollama server. Ensure Ollama is running and has models pulled.")
        return None
        
    print("Available Ollama models:")
    for i, model in enumerate(models):
        print(f"[{i + 1}] {model}")
        
    if auto_select:
        # Prioritize the most capable model we know (e.g., llama3.1 if available)
        preferred_models = ['llama3.1', 'llama3', 'mistral', 'gemma2']
        selected_model = None
        for pref in preferred_models:
            for available in models:
                if pref in available.lower():
                    selected_model = available
                    break
            if selected_model:
                break
        
        if not selected_model:
            selected_model = models[0] # Fallback to first available
            
        print(f"Auto-selected model: {selected_model}")
        return selected_model
        
    return models
