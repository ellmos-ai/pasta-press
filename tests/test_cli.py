import json
import os
from click.testing import CliRunner
from pastapress.cli import cli
from pastapress.config import CONFIG


def test_process_single_file(tmp_path, mock_ollama_echo):
    runner = CliRunner()
    f = tmp_path / "note.txt"
    f.write_text("Ein kleiner Text.", encoding="utf-8")

    result = runner.invoke(cli, ["process", str(f)])

    assert result.exit_code == 0
    assert "Successfully processed" in result.output
    assert (tmp_path / "note_pasta-press.txt").exists()


def test_process_single_file_llm_down_exits_nonzero(tmp_path, mock_ollama_down):
    runner = CliRunner()
    f = tmp_path / "note.txt"
    f.write_text("Ein kleiner Text.", encoding="utf-8")

    result = runner.invoke(cli, ["process", str(f)])

    assert result.exit_code == 1
    assert "Failed to process" in result.output
    assert not (tmp_path / "note_pasta-press.txt").exists()


def test_process_directory_enqueues_and_skips_output_files(tmp_path, monkeypatch):
    runner = CliRunner()
    queue_file = tmp_path / "queue.json"
    monkeypatch.setitem(CONFIG, "queue_file", str(queue_file))

    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("A", encoding="utf-8")
    (src / "b.md").write_text("B", encoding="utf-8")
    (src / "a_pasta-press.txt").write_text("already pressed", encoding="utf-8")
    (src / "ignored.exe").write_text("x", encoding="utf-8")
    (src / "old.doc").write_text("legacy", encoding="utf-8")

    result = runner.invoke(cli, ["process", str(src)])

    assert result.exit_code == 0
    assert "Added 2 file(s)" in result.output

    queued = json.loads(queue_file.read_text(encoding="utf-8"))
    queued_paths = {os.path.basename(item["path"]) for item in queued}
    assert queued_paths == {"a.txt", "b.md"}


def test_process_queue_empty(tmp_path, monkeypatch):
    runner = CliRunner()
    monkeypatch.setitem(CONFIG, "queue_file", str(tmp_path / "queue.json"))

    result = runner.invoke(cli, ["process-queue"])
    assert result.exit_code == 0
    assert "Queue is empty" in result.output


def test_process_queue_processes_items(tmp_path, monkeypatch, mock_ollama_echo):
    runner = CliRunner()
    queue_file = tmp_path / "queue.json"
    monkeypatch.setitem(CONFIG, "queue_file", str(queue_file))

    f = tmp_path / "queued.txt"
    f.write_text("Inhalt.", encoding="utf-8")
    queue_file.write_text(json.dumps([{"path": str(f)}]), encoding="utf-8")

    result = runner.invoke(cli, ["process-queue"])

    assert result.exit_code == 0
    assert "Queue processing completed." in result.output
    assert (tmp_path / "queued_pasta-press.txt").exists()
    # Queue must be drained afterwards.
    assert json.loads(queue_file.read_text(encoding="utf-8")) == []


def test_text_command_save_as(tmp_path, mock_ollama_echo):
    runner = CliRunner()
    out = tmp_path / "out.txt"

    result = runner.invoke(cli, ["text", "Bitte veredeln.", "--save-as", str(out)])

    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8") == "Bitte veredeln."


def test_text_command_llm_down_exits_nonzero(mock_ollama_down):
    runner = CliRunner()
    result = runner.invoke(cli, ["text", "Bitte veredeln."])
    assert result.exit_code == 1


def test_config_listing_makes_no_network_call(monkeypatch, tmp_path):
    """The plain `config` listing must not hit the network in tests."""
    calls = []
    monkeypatch.setattr("pastapress.ollama_utils.configure_ollama_profile",
                        lambda host=None, auto_select=False: calls.append(host) or [])
    # Keep the real config.json untouched.
    monkeypatch.setattr("pastapress.config.CONFIG_FILE", str(tmp_path / "config.json"))

    runner = CliRunner()
    result = runner.invoke(cli, ["config"])

    assert result.exit_code == 0
    assert "Current Configuration:" in result.output
    assert len(calls) == 1


def test_config_set_style_persists(monkeypatch, tmp_path):
    config_file = tmp_path / "config.json"
    monkeypatch.setattr("pastapress.config.CONFIG_FILE", str(config_file))

    runner = CliRunner()
    result = runner.invoke(cli, ["config", "--style", "kurz"])

    assert result.exit_code == 0
    assert "Configuration saved." in result.output
    saved = json.loads(config_file.read_text(encoding="utf-8"))
    assert saved["style"] == "kurz"
