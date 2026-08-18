# CHANGELOG

## [1.1.0] - 2026-08-18
### Fixed
- **Critical:** `llm_client.py` contained an unterminated triple-quoted string
  (an orphaned legacy `SYSTEM_PROMPT` block swallowing the class definition),
  which made the entire package unimportable (`SyntaxError`). The CLI and all
  tests were broken as of 1.0.0.
- Leading/trailing whitespace of text chunks (indentation, boundary spaces) is
  now preserved around the LLM call — previously lost via response stripping.
- Directory mode no longer re-enqueues previously generated `*_pasta-press.*`
  output files (avoided double-pressing on repeated runs).
- Removed duplicated output-path logic in `core.process_file` (now uses
  `get_output_path`) and a redundant second `reassemble` call.
- Plain-text reading now handles UTF-8 BOM (`utf-8-sig`) and falls back to
  cp1252 for legacy Windows files instead of failing.

### Changed
- **`.doc` support removed** — Pandoc has no reader for legacy binary `.doc`;
  the tool now fails with a clear message asking for `.docx` instead of
  pretending support.
- Default Ollama host is now `http://localhost:11434`; `config.json` is no
  longer tracked in git (auto-created on first run, see `config.example.json`).
- `LLMClient.process_text` now raises `LLMProcessingError` after exhausting
  retries instead of silently returning the original text. `PastaPressCore`
  keeps the original chunk, counts failures (`last_failed_chunks`), and the CLI
  reports partial failures. If **all** chunks fail (e.g. Ollama unreachable),
  no output file is written and the command exits non-zero.
- Oversized paragraphs (no blank-line delimiters) are now split at line and
  word boundaries (secondary split) so single huge paragraphs no longer exceed
  the chunk limit.
- Model auto-selection now also recognizes `qwen` model families.
- Directory mode reports how many files were actually enqueued.

### Added
- Test suite expanded from 4 to 36 tests: chunker secondary-split and lossless
  roundtrip invariants, LLM client retry/error paths (mocked at HTTP level),
  core end-to-end file processing, document parser encodings, and CLI behavior
  (queue isolation, failure exit codes, config persistence).

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
