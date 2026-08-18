# CHANGELOG

## [1.0.0] - 2026-08-18
### Added
- Core LLM text refinement logic via `TextChunker` and `LLMClient`.
- Seamless chunking preserving text structure and formatting delimiters.
- Support for `gleichwertig`, `wissenschaftlich`, `einfach`, `kurz`, and `original` text styles.
- Translation mode functionality.
- Queue manager for batch directory processing.
- `pypandoc` integration for automatic `.docx`, `.odt`, `.rtf`, `.doc` to `.md` parsing.
- CLI application using `click` (`process`, `process-queue`, `text`, `config`).
- Auto-detection of available Ollama models.
- Bilingual documentation and GitHub repository setup.
