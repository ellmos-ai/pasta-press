# PastaPress

Ein Kommandozeilen-Tool und Python-Modul zur stilistischen Textveredelung via lokaler Ollama-Instanz (Mac Studio).

## Funktionen
- Verarbeitet Textdateien absatzweise ohne den Kontext zu verlieren.
- Zwingt das LLM per System-Prompt, den Text in eigenen Worten zu verbessern, ohne Inhalte zu verfälschen.
- Unterstützung für Datei-Queues (Batch-Verarbeitung).
- Konfigurierbar über \config.json\ und CLI-Parameter.

## Installation
\\\ash
pip install -r requirements.txt
\\\

## Nutzung

\\\ash
python -m pastapress.cli process my_document.txt
\\\

