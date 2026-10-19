from __future__ import annotations

import os
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from services.conversion_service import ConversionService


class ConversionPopup:
    def __init__(self, file_paths: str | list[str] | None = None, launch_error: str | None = None):
        self.root = tk.Tk()
        self.root.title("LocalFile Converter")
        self.root.geometry("640x600")
        self.root.minsize(560, 500)
        self._configure_theme()
        self.file_paths = self._resolve_file_paths(file_paths)
        self.launch_error = launch_error
        if self.launch_error is None:
            missing_paths = [path for path in self.file_paths if not Path(path).is_file()]
            if missing_paths:
                self.launch_error = "Selected file does not exist or is not a file:\n" + "\n".join(missing_paths)
        self.file_path = self.file_paths[0] if self.file_paths else None
        self.selected_output = tk.StringVar(value="")
        self._format_values: dict[str, str] = {}
        self.background_color = tk.StringVar(value="white")
        self.quality = tk.IntVar(value=90)
        self.page_range = tk.StringVar(value="")
        self.output_path = None
        self.output_paths: list[str] = []
        self._build_ui()

    def _configure_theme(self) -> None:
        self.colors = {
            "background": "#0b1020",
            "surface": "#121b2e",
            "field": "#0d1526",
            "border": "#293955",
            "text": "#edf4ff",
            "muted": "#9cacc4",
            "accent": "#68e5d5",
            "accent_hover": "#91f2e4",
            "success": "#79e0b4",
            "error": "#ff8294",
            "warning": "#ffd67f",
        }
        self.root.configure(bg=self.colors["background"])
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["background"])
        style.configure(
            "TLabel",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "App.TFrame",
            background=self.colors["background"],
        )
        style.configure(
            "App.TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI Semibold", 20),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["background"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Glass.TLabelframe",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "Glass.TLabelframe.Label",
            background=self.colors["surface"],
            foreground=self.colors["accent"],
            font=("Segoe UI Semibold", 9),
        )
        style.configure(
            "Card.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Muted.Card.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Success.App.TLabel",
            background=self.colors["background"],
            foreground=self.colors["success"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Error.App.TLabel",
            background=self.colors["background"],
            foreground=self.colors["error"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Warning.App.TLabel",
            background=self.colors["background"],
            foreground=self.colors["warning"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "TCombobox",
            fieldbackground=self.colors["field"],
            background=self.colors["surface"],
            foreground=self.colors["text"],
            arrowcolor=self.colors["accent"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            padding=(10, 8),
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.colors["field"])],
            foreground=[("readonly", self.colors["text"])],
            selectbackground=[("readonly", self.colors["field"])],
            selectforeground=[("readonly", self.colors["text"])],
        )
        style.configure(
            "TEntry",
            fieldbackground=self.colors["field"],
            foreground=self.colors["text"],
            insertcolor=self.colors["text"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            padding=(9, 7),
        )
        style.configure(
            "TScale",
            background=self.colors["surface"],
            troughcolor=self.colors["field"],
            sliderthickness=14,
        )
        style.configure(
            "Accent.TButton",
            background=self.colors["accent"],
            foreground="#071521",
            bordercolor=self.colors["accent"],
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"],
            padding=(18, 9),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "Accent.TButton",
            background=[("disabled", self.colors["border"]), ("active", self.colors["accent_hover"])],
            foreground=[("disabled", self.colors["muted"]), ("active", "#071521")],
        )
        style.configure(
            "Quiet.TButton",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            lightcolor=self.colors["border"],
            darkcolor=self.colors["border"],
            padding=(13, 8),
        )
        style.map(
            "Quiet.TButton",
            background=[("active", "#1b2941")],
            foreground=[("active", self.colors["accent_hover"])],
        )

    def _resolve_file_paths(self, file_paths: str | list[str] | None) -> list[str]:
        if not file_paths:
            return []
        if isinstance(file_paths, str):
            return [file_paths]
        return [str(path) for path in file_paths]

    def _build_ui(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        main = ttk.Frame(self.root, padding=24, style="App.TFrame")
        self.main = main
        main.grid(row=0, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)

        title = ttk.Label(
            main,
            text="Convert file" if len(self.file_paths) <= 1 else "Convert files",
            style="Title.TLabel",
        )
        title.grid(row=0, column=0, sticky="w", pady=(0, 2))
        subtitle = ttk.Label(
            main,
            text="Private, local conversions — your files stay on this device.",
            style="Subtitle.TLabel",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 18))

        file_info = ttk.LabelFrame(
            main,
            text="  SELECTED FILE  " if len(self.file_paths) <= 1 else "  SELECTED FILES  ",
            style="Glass.TLabelframe",
            padding=(14, 10),
        )
        file_info.grid(row=2, column=0, sticky="ew")
        file_info.columnconfigure(1, weight=1)

        if not self.file_paths:
            file_text = "No file selected"
        elif len(self.file_paths) == 1:
            file_text = self.file_paths[0]
        else:
            file_text = "\n".join(Path(path).name for path in self.file_paths[:4])
            if len(self.file_paths) > 4:
                file_text += f"\n+ {len(self.file_paths) - 4} more"
        self.file_label = ttk.Label(file_info, text=file_text, wraplength=520, style="Card.TLabel")
        self.file_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=2, pady=(2, 6))

        if self.file_paths:
            if len(self.file_paths) == 1:
                file = Path(self.file_paths[0])
                size = file.stat().st_size if file.exists() else 0
                info_text = f"Type: {file.suffix.upper() or 'Unknown'}   Size: {size} bytes"
            else:
                info_text = f"Count: {len(self.file_paths)} files   Common mode: batch conversion"
            ttk.Label(file_info, text=info_text, style="Muted.Card.TLabel").grid(row=1, column=0, sticky="w", padx=2, pady=(0, 2))

        format_frame = ttk.LabelFrame(
            main,
            text="  OUTPUT FORMAT  ",
            style="Glass.TLabelframe",
            padding=(14, 8),
        )
        format_frame.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        format_frame.columnconfigure(0, weight=1)

        self.format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.selected_output,
            state="readonly",
            values=self._display_formats(),
        )
        self.format_combo.grid(row=0, column=0, sticky="ew", padx=2, pady=5)

        settings_frame = ttk.LabelFrame(
            main,
            text="  SETTINGS  ",
            style="Glass.TLabelframe",
            padding=(14, 10),
        )
        settings_frame.grid(row=4, column=0, sticky="ew", pady=(14, 0))
        settings_frame.columnconfigure(1, weight=1)

        self.quality_caption = ttk.Label(settings_frame, text="Image quality", style="Card.TLabel")
        self.quality_caption.grid(row=0, column=0, sticky="w", padx=2, pady=(5, 6))
        self.quality_scale = ttk.Scale(settings_frame, from_=1, to=100, variable=self.quality, orient="horizontal")
        self.quality_scale.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        self.quality_label = ttk.Label(settings_frame, text=f"{self.quality.get()}%", style="Muted.Card.TLabel")
        self.quality_label.grid(row=0, column=2, sticky="w", padx=(0, 2), pady=(5, 6))
        self.background_caption = ttk.Label(settings_frame, text="JPEG background", style="Card.TLabel")
        self.background_caption.grid(row=1, column=0, sticky="w", padx=2, pady=6)
        self.background_entry = ttk.Entry(settings_frame, textvariable=self.background_color)
        self.background_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 2), pady=6)
        self.pages_caption = ttk.Label(settings_frame, text="PDF pages", style="Card.TLabel")
        self.pages_caption.grid(row=2, column=0, sticky="w", padx=2, pady=(6, 10))
        self.pages_entry = ttk.Entry(settings_frame, textvariable=self.page_range)
        self.pages_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 2), pady=(6, 10))
        self.pages_hint = ttk.Label(settings_frame, text="Range example: 1-3,5; blank uses all pages.", style="Muted.Card.TLabel")
        self.pages_hint.grid(row=3, column=0, columnspan=3, sticky="w", padx=2, pady=(0, 8))
        self.format_combo.bind("<<ComboboxSelected>>", lambda *_: self._format_changed())

        self.quality.trace_add("write", lambda *_: self._update_quality_label())

        self.convert_button = ttk.Button(main, text="Convert", style="Accent.TButton", command=self.convert)

        self.status_var = tk.StringVar(value="")
        self.status = ttk.Label(main, textvariable=self.status_var, style="Success.App.TLabel", wraplength=540)
        self.status.grid(row=6, column=0, sticky="w", pady=(14, 0))

        self.error_var = tk.StringVar(value="")
        self.error_label = ttk.Label(main, textvariable=self.error_var, style="Error.App.TLabel", wraplength=540)
        self.error_label.grid(row=7, column=0, sticky="w", pady=(7, 0))

        self.notice_var = tk.StringVar(value="")
        self.notice_label = ttk.Label(main, textvariable=self.notice_var, style="Warning.App.TLabel", wraplength=540)
        self.notice_label.grid(row=8, column=0, sticky="w", pady=(6, 0))

        self.select_button = ttk.Button(main, text="Select files", style="Quiet.TButton", command=self._select_files)
        if not self.file_paths and not self.launch_error:
            self.select_button.grid(row=5, column=0, sticky="w", pady=(18, 0))

        if not self.file_paths:
            self.status_var.set("No file selected. Use Select files to choose a file.")
            self.convert_button.state(["disabled"])

        if self.format_combo["values"]:
            self.format_combo.current(0)
            self._update_settings_visibility()
            self._show_dependency_warning()
        elif self.launch_error:
            self.error_var.set(self.launch_error)
            self.status_var.set("Unable to open the selected file.")
            self.convert_button.state(["disabled"])
        elif self.file_paths:
            unavailable = [
                message
                for file_path in self.file_paths
                for message in ConversionService.get_unavailable_format_messages(file_path)
            ]
            if unavailable:
                self.error_var.set("\n".join(unavailable))
                self.status_var.set("Required local conversion engines are missing.")
            else:
                self.status_var.set("This file type is not supported yet.")
            self.convert_button.state(["disabled"])

        if self.file_paths:
            self.convert_button.grid(row=5, column=0, sticky="e", pady=(18, 0))
        else:
            self.convert_button.grid(row=5, column=0, sticky="e", pady=(18, 0))
        if self.launch_error:
            self.error_var.set(self.launch_error)
            self.status_var.set("Unable to open the selected file.")
        self._update_settings_visibility()
        self._refresh_unavailable_notice()

    def _update_quality_label(self) -> None:
        self.quality_label.configure(text=f"{self.quality.get()}%")

    def _available_formats(self) -> list[str]:
        if not self.file_paths:
            return []
        return ConversionService.get_common_formats(self.file_paths)

    def _format_label(self, output_format: str) -> str:
        if output_format == "PDF_MERGE":
            return "Merge selected PDFs"
        if not self.file_paths:
            return output_format
        return ConversionService.get_format_label(self.file_paths[0], output_format)

    def _display_formats(self) -> list[str]:
        formats = self._available_formats()
        self._format_values = {self._format_label(fmt): fmt for fmt in formats}
        return list(self._format_values)

    def _selected_format(self) -> str:
        selected = self.selected_output.get()
        return self._format_values.get(selected, selected)

    def _update_settings_visibility(self) -> None:
        output_format = self._selected_format()
        is_pdf = bool(self.file_paths) and Path(self.file_paths[0]).suffix.lower() == ".pdf"
        is_image = bool(self.file_paths) and Path(self.file_paths[0]).suffix.lower() in {
            ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff", ".ico"
        }
        show_quality = is_image and output_format in {"JPEG", "WEBP"}
        show_background = is_image and output_format == "JPEG"
        show_pages = is_pdf and output_format in {"PNG", "JPEG", "PDF_EXTRACT"}

        for widget, visible in (
            (self.quality_caption, show_quality),
            (self.quality_scale, show_quality),
            (self.quality_label, show_quality),
            (self.background_caption, show_background),
            (self.background_entry, show_background),
            (self.pages_caption, show_pages),
            (self.pages_entry, show_pages),
            (self.pages_hint, show_pages),
        ):
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    def _format_changed(self) -> None:
        self._update_settings_visibility()
        self._show_dependency_warning()

    def _refresh_unavailable_notice(self) -> None:
        messages = []
        for file_path in self.file_paths:
            for message in ConversionService.get_unavailable_format_messages(file_path):
                if message not in messages:
                    messages.append(message)
        if self._available_formats() and messages:
            self.notice_var.set("Some conversion options need additional local engines: " + " ".join(messages))
        else:
            self.notice_var.set("")

    def _select_files(self) -> None:
        selected = filedialog.askopenfilenames(title="Select files to convert")
        if not selected:
            return
        self.file_paths = list(selected)
        self.file_path = self.file_paths[0]
        self.launch_error = None
        self.status_var.set("")
        self.error_var.set("")
        self.file_label.configure(text="\n".join(Path(path).name for path in self.file_paths[:4]) + (f"\n+ {len(self.file_paths) - 4} more" if len(self.file_paths) > 4 else ""))
        if len(self.file_paths) == 1:
            file = Path(self.file_paths[0])
            size = file.stat().st_size if file.exists() else 0
            self.file_label.configure(text=str(file))
            for child in self.file_label.master.winfo_children():
                if isinstance(child, ttk.Label) and child is not self.file_label:
                    child.destroy()
            ttk.Label(self.file_label.master, text=f"Type: {file.suffix.upper() or 'Unknown'}   Size: {size} bytes").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))
        else:
            for child in self.file_label.master.winfo_children():
                if isinstance(child, ttk.Label) and child is not self.file_label:
                    child.destroy()
            ttk.Label(self.file_label.master, text=f"Count: {len(self.file_paths)} files   Common mode: batch conversion").grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))
        self.convert_button.state(["!disabled"])
        self.select_button.grid_remove()
        display_formats = self._display_formats()
        self.format_combo.configure(values=display_formats)
        if self.format_combo["values"]:
            self.format_combo.current(0)
            self.selected_output.set(display_formats[0])
            self._update_settings_visibility()
            self._show_dependency_warning()
        else:
            self.status_var.set(
                "Selected files do not share a supported output format."
                if len(self.file_paths) > 1
                else "This file type is not supported yet."
            )
            self.convert_button.state(["disabled"])
        self._refresh_unavailable_notice()

    def _show_dependency_warning(self) -> None:
        if not self.file_paths:
            return

        selected_format = self._selected_format()
        if not selected_format:
            return

        try:
            for file_path in self.file_paths:
                ConversionService.validate_conversion(file_path, selected_format)
        except (RuntimeError, FileNotFoundError, ValueError) as exc:
            self.error_var.set(str(exc))
            self.status_var.set("Dependency check failed.")
            self.convert_button.state(["disabled"])
            return

        self.error_var.set("")
        self.convert_button.state(["!disabled"])
        if not self.status_var.get() or self.status_var.get().startswith("Converted") or self.status_var.get() == "Conversion failed.":
            self.status_var.set("Ready to convert.")

    def convert(self) -> None:
        if not self.file_paths:
            self.status_var.set("No file selected.")
            return

        selected_format = self._selected_format()
        if not selected_format:
            self.status_var.set("Please select an output format.")
            return

        try:
            self.error_var.set("")
            self.status_var.set("Converting locally...")
            self.root.update_idletasks()
            if len(self.file_paths) == 1:
                self.output_path = ConversionService.convert_file(
                    self.file_paths[0],
                    selected_format,
                    quality=self.quality.get(),
                    background_color=self.background_color.get(),
                    page_range=self.page_range.get(),
                )
                self.status_var.set(f"Converted successfully: {Path(self.output_path).name}")
            else:
                outputs = ConversionService.batch_convert_files(
                    self.file_paths,
                    selected_format,
                    quality=self.quality.get(),
                    background_color=self.background_color.get(),
                    page_range=self.page_range.get(),
                )
                self.output_paths = outputs
                self.status_var.set(f"Converted {len(outputs)} files successfully.")
                if outputs:
                    self.output_path = outputs[0]
            self.convert_button.configure(text="Convert again")
            for child in self.main.winfo_children():
                if isinstance(child, ttk.Button) and child["text"] == "Open output folder":
                    child.destroy()
            if self.output_path:
                open_button = ttk.Button(
                    self.main,
                    text="Open output folder",
                    style="Quiet.TButton",
                    command=lambda: self._open_output_folder(),
                )
                open_button.grid(row=9, column=0, sticky="e", pady=(12, 0))
        except Exception as exc:  # pragma: no cover - UI failure path
            self.error_var.set(str(exc))
            self.status_var.set("Conversion failed.")
            self.convert_button.state(["!disabled"])

    def _open_output_folder(self) -> None:
        if not self.output_path:
            return
        folder = str(Path(self.output_path).parent)
        if os.name == "nt":
            os.startfile(folder)
        else:
            subprocess.Popen(["open", folder])

    def run(self) -> None:
        self.root.mainloop()
