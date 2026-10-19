from __future__ import annotations

import sys
from types import SimpleNamespace

import app


def test_install_context_menu_flag_calls_windows_registration(monkeypatch) -> None:
    called = []
    monkeypatch.setattr(app, "install_context_menu", lambda: called.append("install"))
    monkeypatch.setattr(
        app,
        "parse_args",
        lambda: SimpleNamespace(install_context_menu=True, uninstall_context_menu=False, check_dependencies=False, explorer=False, output_format=None, files=[]),
    )

    result = app.main()

    assert result == 0
    assert called == ["install"]


def test_uninstall_context_menu_flag_calls_windows_cleanup(monkeypatch) -> None:
    called = []
    monkeypatch.setattr(app, "uninstall_context_menu", lambda: called.append("remove"))
    monkeypatch.setattr(
        app,
        "parse_args",
        lambda: SimpleNamespace(install_context_menu=False, uninstall_context_menu=True, check_dependencies=False, explorer=False, output_format=None, files=[]),
    )

    result = app.main()

    assert result == 0
    assert called == ["remove"]


def test_check_dependencies_flag_reports_status(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        app,
        "parse_args",
        lambda: SimpleNamespace(install_context_menu=False, uninstall_context_menu=False, check_dependencies=True, explorer=False, convert=False, output_format="PNG", quality=90, files=["sample.png"]),
    )
    monkeypatch.setattr(app, "ConversionService", type("Svc", (), {"get_supported_formats": staticmethod(lambda *_: ["PNG"]), "validate_conversion": staticmethod(lambda *_args, **_kwargs: None)}))

    result = app.main()

    captured = capsys.readouterr()

    assert result == 0
    assert "dependencies ready" in captured.out


def test_convert_flag_uses_cli_conversion(monkeypatch, capsys) -> None:
    calls = []

    monkeypatch.setattr(
        app,
        "parse_args",
        lambda: SimpleNamespace(install_context_menu=False, uninstall_context_menu=False, check_dependencies=False, explorer=False, convert=True, output_format="PNG", quality=80, files=["sample.png"]),
    )

    monkeypatch.setattr(app, "ConversionService", type("Svc", (), {"get_supported_formats": staticmethod(lambda *_: ["PNG"]), "convert_file": staticmethod(lambda path, fmt, quality=90, **kwargs: calls.append((path, fmt, quality)) or "converted.png") }))

    result = app.main()

    captured = capsys.readouterr()

    assert result == 0
    assert calls == [("sample.png", "PNG", 80)]
    assert "Converted:" in captured.out


def test_file_path_argument_is_passed_to_popup_without_reselection(monkeypatch, tmp_path) -> None:
    selected_path = str(tmp_path / "Quarterly report ü.docx")
    opened = []

    class Popup:
        def __init__(self, file_paths=None, launch_error=None):
            opened.append((file_paths, launch_error))

        def run(self):
            return None

    monkeypatch.setattr(app, "ConversionPopup", Popup)
    monkeypatch.setattr(sys, "argv", ["app.py", selected_path])

    result = app.main()

    assert result == 0
    assert opened == [([selected_path], None)]


def test_explorer_argument_parser_preserves_a_quoted_path() -> None:
    selected_path = r"C:\Reports\Annual report ü.docx"

    parsed = app.parse_args(["--explorer", "--", selected_path])

    assert parsed.explorer is True
    assert parsed.files == [selected_path]


def test_launch_without_path_keeps_manual_picker_available(monkeypatch) -> None:
    opened = []

    class Popup:
        def __init__(self, file_paths=None, launch_error=None):
            opened.append((file_paths, launch_error))

        def run(self):
            return None

    monkeypatch.setattr(app, "ConversionPopup", Popup)
    monkeypatch.setattr(sys, "argv", ["app.py"])

    result = app.main()

    assert result == 0
    assert opened == [(None, None)]


def test_explorer_launch_without_path_shows_clear_error(monkeypatch) -> None:
    opened = []

    class Popup:
        def __init__(self, file_paths=None, launch_error=None):
            opened.append((file_paths, launch_error))

        def run(self):
            return None

    monkeypatch.setattr(app, "ConversionPopup", Popup)
    monkeypatch.setattr(sys, "argv", ["app.py", "--explorer"])

    result = app.main()

    assert result == 2
    assert opened == [(None, "Explorer did not provide exactly one selected file.")]
