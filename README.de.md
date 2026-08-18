<p align="center">
  <img src="docs/assets/banner.jpg" alt="PastaPress Banner" width="800">
</p>

# PastaPress

**PastaPress** ist ein leistungsstarkes Kommandozeilen-Tool und Python-Modul zur stilistischen Textveredelung via lokaler Ollama-Instanz (z. B. auf dem Mac Studio). Es drückt rohen, holprigen Text durch eine KI-"Presse" und liefert sauberen, professionellen Text zurück, ohne die Kernfakten oder die Struktur zu verändern.

*Lies diese Dokumentation auf [Englisch (English)](README.md).*

## 💡 Einsatzzwecke

- **Texte von ungewollten KI-typischen Markierungen befreien — und den KI-Anteil selbst ausweisen.** Texte werden zunehmend anhand oberflächlicher „KI-Marker" (verräterische Formulierungsmuster und Artefakte) vorverurteilt, unabhängig von ihrer inhaltlichen Substanz. PastaPress schreibt Text durch eine *lokale* Presse neu, sodass er wieder für seinen Inhalt steht — das ehrliche Gegenstück dazu: Den tatsächlichen KI-Anteil weist *man selbst* offen aus, z. B. in der AI-Disclosure eines Wissenschaftsartikels. Transparenz durch Deklaration statt Vorurteil durch Muster.
- **Rohe Notizen zu lesbarer Prosa veredeln** — Meeting-Notizen, Entwürfe und schnelle Gedankenstützen werden flüssig, während jeder Fakt, jede Liste und jede Überschrift erhalten bleibt.
- **Übersetzen ohne Strukturbruch** — Markdown, Listen und Trennzeichen überleben die Reise in jede Zielsprache.
- **Ganze Ordner im Batch pressen** — Verzeichnis in die Queue, laufen lassen, Originale bleiben erhalten.

## 🌟 Funktionen
- **Chunk-basierte Verarbeitung:** Verarbeitet Textdateien Absatz für Absatz, um Kontext-Limits des LLMs zu umgehen. Überlange Absätze werden zusätzlich an Zeilen- und Wortgrenzen aufgeteilt.
- **Fehlerfreie Rekonstruktion:** Trennzeichen (Delimiters), Einrückungen und Markdown-Formatierungen bleiben exakt erhalten.
- **Format-Support:** Unterstützt `.txt`, `.md`, `.json`, `.csv`, `.yaml`, `.tex` nativ. Auto-Konvertierung von Binärformaten wie `.docx`, `.odt` und `.rtf` zu sauberem Markdown via `pypandoc`. (Das alte Binärformat `.doc` wird nicht unterstützt — bitte zuerst nach `.docx` konvertieren.)
- **Stil-Kontrolle:** Passe den Veredelungs-Stil dynamisch an (`gleichwertig`, `wissenschaftlich`, `einfach`, `kurz` oder `original`).
- **Übersetzungs-Modus:** Optionale On-the-Fly-Übersetzung in jede beliebige Zielsprache unter Beibehaltung der Struktur.
- **Queue-System:** Batch-Verarbeitung ganzer Ordner nacheinander über eine persistente `queue.json`.

## 🚀 Installation

Stelle sicher, dass Python 3.12+ installiert ist.

```bash
git clone https://github.com/ellmos-ai/pasta-press.git
cd pasta-press
pip install -r requirements.txt
```
*(Hinweis: Für die Verarbeitung von `.docx` oder `.odt` lädt das Tool bei Bedarf Pandoc automatisch im Hintergrund herunter.)*

## ⚙️ Konfiguration

Konfiguriere deinen lokalen Ollama-Host und das Standard-Modell (Standard: `http://localhost:11434`; die Einstellungen liegen in einer lokalen, nicht versionierten `config.json` — siehe `config.example.json`):
```bash
python -m pastapress config --auto  # Sucht automatisch das beste Modell auf dem Host
# ODER
python -m pastapress config --model qwen3.6:35b-mlx --host http://mein-ollama-server:11434
```

Setze deine Standard-Stile und Übersetzungspräferenzen:
```bash
python -m pastapress config --style wissenschaftlich
python -m pastapress config --translate-mode on --lang "Spanisch"
```

Das Modell-Thinking/Reasoning ist standardmäßig deaktiviert (~10–80× schneller bei
Thinking-fähigen Modellen wie qwen3.x; der Inhalt bleibt erhalten, kleine Modelle
formulieren aber ggf. etwas holpriger). Wer maximale Sprachqualität statt Tempo
möchte, schaltet es wieder ein:
```bash
python -m pastapress config --thinking on
```

## 🛠️ Nutzung

### Einzelne Datei verarbeiten
```bash
python -m pastapress process mein_dokument.txt
```
*Das Ergebnis wird standardmäßig als `mein_dokument_pasta-press.txt` gespeichert.*

### Stile und Sprache pro Datei überschreiben
```bash
python -m pastapress process entwurf.docx --style original --translate English
```

### Einen Ordner verarbeiten (Batch / Queue)
```bash
python -m pastapress process ./mein_ordner
python -m pastapress process-queue
```

### Rohtext verarbeiten (Für Agenten-Integrationen)
```bash
python -m pastapress text "Das is ein echt mieser Text der hilfe braucht."
```

## 🔒 Datenschutz & Sicherheit
- **Lokale Verarbeitung:** Alle Daten werden zu 100 % lokal über den konfigurierten Ollama-Host verarbeitet (Standard: `http://localhost:11434`).
- **Keine Telemetrie:** Es werden keine Daten an Cloud-Anbieter oder Drittanbieter-APIs gesendet.
- **Smart Filtering:** (Geplant - siehe `ROADMAP.md`) Zukünftige Versionen bieten striktes Code-Filtering, damit sensible Tags/Code-Snippets erst gar nicht an das LLM gesendet werden.

## 📄 Lizenz & Herkunft

MIT-Lizenz — gilt für Code, Prompts und Dokumentation dieses Repositories
(siehe `LICENSE`). Abhängigkeiten (`requests`, `click`, `pypandoc`) werden via
pip installiert und behalten ihre eigenen Lizenzen.

Dieses Tool wurde KI-gestützt im ellmos-ai-Ökosystem entwickelt und wird mit
menschlichem Review gepflegt. Zu Zweckbestimmung und EU-AI-Act-Einordnung
siehe `docs/ai-act-note.md`.
