# Contributing to PastaPress

Thank you for contributing to PastaPress! Since this is a core module in the `.AI/.MODULES` system, please follow these guidelines:

1. **Keep it local:** Do not integrate any external cloud APIs. This tool runs strictly on local Ollama instances.
2. **Lossless processing:** Any new chunking or parsing logic MUST ensure that the original delimiters, tags, or unsupported syntax can be flawlessly reconstructed. Do not drop data.
3. **Write tests:** If you add new parsers or chunkers, write `pytest` unit tests in the `tests/` directory.
4. **Agent compatibility:** Ensure that `cli.py` output remains parseable by agent workflows. Avoid adding unnecessary interactive prompts unless bypassed via flags.

## Development Setup
1. Clone the repo
2. Run `pip install -r requirements.txt`
3. Set `PYTHONPATH=.`
4. Run tests with `pytest tests/ -v`
