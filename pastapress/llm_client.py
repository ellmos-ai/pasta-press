import requests
import time
from .config import CONFIG, logger

SYSTEM_PROMPT = """You are a professional editor and copywriter. / Du bist ein professioneller Lektor und Texter.
Your task is to stylistically improve the following text, make it more fluent, and rewrite it in your own words. / Deine Aufgabe ist es, den folgenden Text stilistisch zu verbessern, flüssiger zu machen und in eigenen Worten neu zu formulieren.

TOP RULES / OBERSTE REGELN:
1. Do NOT omit or alter any content, nuances, or facts. / Du darfst KEINEN inhaltlichen Punkt, keine Nuance und keinen Fakt weglassen oder verfälschen.
2. The content must remain exactly the same, only the expression should become more professional and readable. / Der Inhalt muss exakt derselbe bleiben, nur die Ausdrucksweise soll professioneller und besser lesbar werden.
3. Keep the original formatting exactly (e.g., Markdown formatting, lists, headings). / Behalte das ursprüngliche Dateiformat (z.B. Markdown-Formatierungen, Listen, Überschriften) exakt bei.
4. Output ONLY the improved text, without introductory or concluding remarks. / Gib AUSSCHLIESSLICH den verbesserten Text zurück, ohne einleitende oder abschließende Bemerkungen.
5. If the text is already perfect, return it unchanged. / Wenn der Text bereits perfekt ist, gib ihn einfach unverändert zurück.
"""

class LLMClient:
    def __init__(self, host=None, model=None):
        self.host = host or CONFIG.get("ollama_host")
        self.model = model or CONFIG.get("model")
        self.api_url = f"{self.host.rstrip('/')}/api/chat"

    def process_text(self, text, retries=3):
        if not text.strip():
            return text
            
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            "stream": False
        }
        
        for attempt in range(retries):
            try:
                logger.debug(f"Sending request to {self.api_url} (Model: {self.model}, Attempt {attempt + 1})")
                response = requests.post(self.api_url, json=payload, timeout=600)
                response.raise_for_status()
                
                result = response.json()
                if "message" in result and "content" in result["message"]:
                    processed_text = result["message"]["content"].strip()
                    if not processed_text:
                        raise ValueError("Received empty response from model.")
                    return processed_text
                else:
                    raise ValueError(f"Unexpected response format: {result}")
                    
            except Exception as e:
                logger.warning(f"Error during LLM processing (Attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("Max retries reached. Returning original text.")
                    return text
