<p align="center">
  <img src="docs/assets/banner.jpg" alt="PastaPress Banner" width="800">
</p>

# PastaPress

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/version-1.2.2-blue.svg" alt="Version 1.2.2"></a>
  <a href=".github/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-passing-brightgreen.svg" alt="CI"></a>
  <a href="tests/"><img src="https://img.shields.io/badge/tests-47%20passed%20%7C%20100%25-success.svg" alt="Tests"></a>
  <a href="SECURITY.md"><img src="https://img.shields.io/badge/datenschutz-Zero%20Egress-success.svg" alt="Zero Egress"></a>
  <a href="SECURITY.md"><img src="https://img.shields.io/badge/sicherheit-48h%20SLA-blue.svg" alt="48h SLA"></a>
</p>

**PastaPress** ist ein Kommandozeilen-Tool und Python-Modul zur stilistischen Textveredelung via lokaler Ollama-Instanz (z. B. auf dem Mac Studio). Es drückt rohen, holprigen Text durch eine KI-„Presse“ und liefert sauberen, professionellen Text zurück – mit dem Ziel, Bedeutung, Informationen und Struktur zu bewahren.

*Lies diese Dokumentation auf [Englisch (English)](README.md).*

## 💡 Einsatzzwecke

- **Statistische Textwatermark-Signale durch Paraphrasierung auf vergleichbarem Niveau reduzieren – bei fortbestehender KI-Offenlegung.** Der Standardstil `gleichwertig` formuliert auf vergleichbarem Bedeutungs-, Informations- und Sprachniveau um. Dadurch können statistische Muster in Token- und Formulierungswahl reduziert werden; PastaPress ist jedoch kein Detektor und garantiert weder den vollständigen Erhalt jedes Details noch die vollständige Entfernung aller statistischen Signale. Der tatsächliche KI-Anteil ist weiterhin überall offenzulegen, wo dies erwartet wird, etwa in wissenschaftlichen Artikeln.
- **Rohe Notizen zu lesbarer Prosa veredeln** – Meeting-Notizen, Entwürfe und schnelle Gedankenstützen werden flüssiger; der Prompt weist das Modell an, Informationen und Struktur so vollständig wie möglich zu bewahren.
- **Unter möglichst weitgehender Strukturerhaltung übersetzen** – PastaPress bewahrt technische Chunk-Grenzen; innerhalb des übersetzten Textes soll das Modell Markdown und Listen erhalten.
- **Ganze Ordner im Batch pressen** — Verzeichnis in die Queue, laufen lassen, Originale bleiben erhalten.

PastaPress sucht oder entfernt **keine** wörtlichen oder unsichtbaren
Unicode-Zeichen, eingebetteten Marker-Zeichenketten, C2PA-Daten, EXIF-/XMP-Felder
oder sonstigen Datei-/Container-Metadaten. LLM-Paraphrasierung ist generativ;
wichtige Ausgaben müssen daher mit dem Ausgangstext abgeglichen werden.
Pflichten zur KI-Offenlegung bleiben unberührt.

## 🌟 Funktionen
- **Chunk-basierte Verarbeitung:** Verarbeitet Textdateien Absatz für Absatz, um Kontext-Limits des LLMs zu umgehen. Überlange Absätze werden zusätzlich an Zeilen- und Wortgrenzen aufgeteilt.
- **Deterministische Chunk-Rekonstruktion:** Die ursprünglichen Trennzeichen zwischen Chunks und deren Rand-Leerraum werden exakt wieder zusammengesetzt. Modellgenerierter Text innerhalb eines Chunks kann Fakten oder Formatierungen dennoch verändern; dies ist keine Garantie verlustfreier Inhalte.
- **Format-Support:** Unterstützt `.txt`, `.md`, `.json`, `.csv`, `.yaml`, `.tex` nativ. Auto-Konvertierung von Binärformaten wie `.docx`, `.odt` und `.rtf` zu sauberem Markdown via `pypandoc`. (Das alte Binärformat `.doc` wird nicht unterstützt — bitte zuerst nach `.docx` konvertieren.)
- **Stil-Kontrolle:** Passe den Veredelungsstil dynamisch an (`gleichwertig`, `wissenschaftlich`, `einfach`, `kurz` oder `original`). Der Standardstil `gleichwertig` zielt bei veränderter Formulierung auf ein vergleichbares Bedeutungs-, Informations- und Sprachniveau.
- **Übersetzungs-Modus:** Optionale On-the-Fly-Übersetzung in jede beliebige Zielsprache mit der Anweisung an das Modell, Formatierungen möglichst beizubehalten.
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
Thinking-fähigen Modellen wie qwen3.x; Projekttests zeigten bei kleinen Modellen
holprigere Formulierungen, eine Garantie vollständigen Informationserhalts wird
jedoch nicht gegeben). Wer maximale Sprachqualität statt Tempo möchte, schaltet
es wieder ein:
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
