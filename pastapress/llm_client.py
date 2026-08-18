import requests
import time
from .config import CONFIG, logger


class LLMProcessingError(Exception):
    """Raised when the LLM could not process a chunk after all retries."""
    pass


class LLMClient:
    def __init__(self, host=None, model=None):
        self.host = host or CONFIG.get("ollama_host")
        self.model = model or CONFIG.get("model")
        self.api_url = f"{self.host.rstrip('/')}/api/chat"

    def process_text(self, text, style=None, target_language=None, retries=3):
        """
        Sends a single text chunk to the LLM and returns the refined text.

        Raises LLMProcessingError if all retries fail, so the caller can
        decide what to do (e.g. keep the original chunk and count the failure).
        """
        if not text.strip():
            return text

        if style is None:
            style = CONFIG.get("style", "gleichwertig")

        is_translation = False
        target_lang_str = ""

        if target_language:
            is_translation = True
            target_lang_str = target_language
        elif CONFIG.get("translation_mode", False):
            is_translation = True
            target_lang_str = CONFIG.get("target_language", "English")

        # Determine stylistic instructions
        if style == "wissenschaftlich":
            style_instruction = "Formuliere den Text auf ein gehobenes, wissenschaftliches und akademisches Niveau um."
        elif style == "einfach":
            style_instruction = "Formuliere den Text in leichter, sehr einfach verständlicher Sprache um (Leichte Sprache)."
        elif style == "kurz":
            style_instruction = "Kürze den Text prägnant und knackig, ohne jedoch wichtige Fakten wegzulassen."
        elif style == "original":
            style_instruction = "Behalte den aktuellen Stil, Tonfall und die Länge exakt bei. Nimm keine stilistischen Verbesserungen vor."
        else:  # gleichwertig
            style_instruction = "Paraphrasiere den Text auf gleichwertigem Niveau, um den Stil flüssiger und natürlicher zu machen."

        translation_instruction = ""
        if is_translation:
            translation_instruction = f"\nZusätzliche Anweisung: Übersetze den gesamten Text in folgende Sprache: {target_lang_str}."

        system_prompt = f"""Du bist ein KI-Assistent für Textverarbeitung.
{style_instruction}{translation_instruction}

TOP RULES / OBERSTE REGELN:
1. Kein Fakt, kein inhaltlicher Punkt und keine Nuance darf weggelassen, verändert oder verfälscht werden.
2. Der Inhalt muss exakt der gleiche bleiben, nur die Ausdrucksweise soll entsprechend der Vorgabe angepasst werden.
3. Behalte das Textformat, Markdown und Listen EXAKT bei.
4. Gib AUSSCHLIESSLICH den verbesserten Text zurück. KEINE Einleitungen, KEINE Bestätigungen, KEINE Erklärungen.
5. Wenn der Text schon perfekt ist, gib ihn einfach unverändert zurück.
"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "stream": False
        }

        last_error = None
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
                last_error = e
                logger.warning(f"Error during LLM processing (Attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)

        raise LLMProcessingError(f"LLM processing failed after {retries} attempts: {last_error}")
