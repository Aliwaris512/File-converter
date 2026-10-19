from __future__ import annotations

from pathlib import Path
import sys

try:
    import winreg
except ImportError:  # pragma: no cover - non-Windows runtime
    winreg = None


APP_ROOT = Path(__file__).resolve().parents[1]
APP_SCRIPT = APP_ROOT / "app.py"
APP_EXECUTABLE = Path(sys.executable).resolve()
if not getattr(sys, "frozen", False):
    pythonw = APP_EXECUTABLE.with_name("pythonw.exe")
    if pythonw.is_file():
        APP_EXECUTABLE = pythonw
APP_COMMAND = (
    f'"{APP_EXECUTABLE}"'
    if getattr(sys, "frozen", False)
    else f'"{APP_EXECUTABLE}" "{APP_SCRIPT}"'
)


def build_context_menu_command(app_command: str = APP_COMMAND) -> str:
    return f'{app_command} --explorer -- "%1"'


COMMAND = build_context_menu_command()
CONTEXT_MENU_TITLE = "Convert with LocalFile Converter"


def _require_windows() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Windows context-menu integration is only supported on Windows.")
    if winreg is None:
        raise RuntimeError("winreg is unavailable in this Python environment.")


def _write_shell_entry(shell_key: str, title: str, icon: str | None = None) -> None:
    _require_windows()
    root = winreg.HKEY_CURRENT_USER
    key_path = rf"Software\Classes\{shell_key}\shell\LocalFileConverter"
    with winreg.CreateKey(root, key_path) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, title)
        winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, title)
        winreg.SetValueEx(key, "MultiSelectModel", 0, winreg.REG_SZ, "Single")
        if icon:
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)

    with winreg.CreateKey(root, rf"{key_path}\command") as cmd_key:
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, build_context_menu_command())


def install_context_menu() -> None:
    _require_windows()
    _write_shell_entry("*", CONTEXT_MENU_TITLE, str(APP_EXECUTABLE))


def uninstall_context_menu() -> None:
    _require_windows()
    for shell_key in (
        r"Software\Classes\*\shell\LocalFileConverter",
        r"Software\Classes\Directory\Background\shell\LocalFileConverter",
        r"Software\Classes\SystemFileAssociations\image\shell\LocalFileConverter",
    ):
        try:
            winreg.DeleteKeyTree(winreg.HKEY_CURRENT_USER, shell_key)
        except FileNotFoundError:
            continue


if __name__ == "__main__":
    install_context_menu()
    print("Context menu installed.")
