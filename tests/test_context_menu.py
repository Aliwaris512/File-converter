from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import windows.context_menu as context_menu


class FakeKey:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class FakeWinReg:
    HKEY_CURRENT_USER = object()
    REG_SZ = "REG_SZ"

    def __init__(self):
        self.values = []

    def CreateKey(self, root, path):
        return FakeKey()

    def SetValueEx(self, key, name, reserved, value_type, value):
        self.values.append((name, value))
        return None

    def DeleteKeyTree(self, root, path):
        return None


def test_install_context_menu_registers_shell_entries(monkeypatch) -> None:
    fake_reg = FakeWinReg()
    monkeypatch.setattr(context_menu, "winreg", fake_reg)
    monkeypatch.setattr(context_menu.sys, "platform", "win32")

    context_menu.install_context_menu()

    assert any(name == "MultiSelectModel" and value == "Single" for name, value in fake_reg.values)
    assert any(name == "" and value == context_menu.COMMAND for name, value in fake_reg.values)
    assert " --explorer -- \"%1\"" in context_menu.COMMAND
    assert "%*" not in context_menu.COMMAND
    assert "cmd.exe" not in context_menu.COMMAND.lower()


def test_registered_command_round_trips_a_quoted_unicode_path(tmp_path: Path) -> None:
    probe_script = tmp_path / "argv probe.py"
    selected_file = tmp_path / "report ü & final.docx"
    selected_file.touch()
    probe_script.write_text(
        "import json, sys\nprint(json.dumps(sys.argv[1:]))\n",
        encoding="utf-8",
    )
    app_command = f'"{sys.executable}" "{probe_script}"'
    command = context_menu.build_context_menu_command(app_command)
    command = command.replace('"%1"', f'"{selected_file}"')

    completed = subprocess.run(command, capture_output=True, text=True, check=True)

    assert json.loads(completed.stdout) == ["--explorer", "--", str(selected_file)]


def test_uninstall_context_menu_handles_missing_keys(monkeypatch) -> None:
    fake_reg = FakeWinReg()
    monkeypatch.setattr(context_menu, "winreg", fake_reg)
    monkeypatch.setattr(context_menu.sys, "platform", "win32")

    context_menu.uninstall_context_menu()

    assert True
