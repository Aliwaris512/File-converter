# LocalFile Converter

LocalFile Converter is an offline-first Windows desktop converter. Files stay on the local machine; the app does not upload files, use cloud conversion APIs, or download engines during conversion.

## Supported conversions

Formats are listed only when the required local Python dependency or engine is available.

- **Images:** PNG, JPEG, WebP, BMP, TIFF, GIF, and ICO input/output where Pillow supports the image. Transparent pixels are retained for formats that support alpha; JPEG flattens them using the configurable background color.
- **Documents to PDF:** TXT with ReportLab; DOC, DOCX, PPTX, and HTML with LibreOffice in headless mode.
- **PDF:** export pages to PNG/JPEG, convert to DOCX with `pdf2docx`, merge selected PDFs, split to one PDF per page, extract a page range, rotate pages by 90 degrees, and structurally compress/optimize.
- **Spreadsheets:** XLSX to CSV (active worksheet) and CSV to XLSX.
- **Audio/video:** the existing FFmpeg converter remains a local optional engine; its formats are shown only when FFmpeg is detected.

PDF-to-DOCX uses `pdf2docx` to reconstruct document layout elements; it is not a text-only export or a file rename. Scanned/image-only PDFs require OCR, which is not bundled. Complex layouts, columns, tables, fonts, and graphics may not convert perfectly. PDF optimization uses PyMuPDF structural cleanup/deflate and does not promise a smaller file or downsample embedded images.

## Install Python dependencies

From PowerShell:

```powershell
cd "C:\Users\aliwa\Desktop\FileConverter"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For DOC/DOCX/PPTX/HTML-to-PDF conversions, separately install LibreOffice and ensure `soffice.exe` is on `PATH` or installed in the standard Program Files location. LibreOffice is not installed or updated automatically by this app. Restart the app after installing it.

## Run the app

Open the popup without a selected file:

```powershell
cd "C:\Users\aliwa\Desktop\FileConverter"
.\.venv\Scripts\python.exe .\app.py
```

This manual launch provides a **Select files** button. When a file is passed from Explorer, its path is preselected and that file-picker button is not shown.

Open the popup for a specific file:

```powershell
.\.venv\Scripts\python.exe .\app.py "C:\path with spaces\report.docx"
```

The conversion creates a new output name beside the input (or a new output directory for page exports/splits). Existing outputs are preserved; the converter chooses a numbered name instead.

## Windows Explorer integration

Register the per-user context menu using the project virtual environment:

```powershell
cd "C:\Users\aliwa\Desktop\FileConverter"
.\scripts\install_context_menu.ps1
```

Or call the registration CLI directly:

```powershell
.\.venv\Scripts\python.exe .\app.py --install-context-menu
```

Right-click a file and choose **Convert with LocalFile Converter**. The registry command is quoted and passes Explorer's selected path as one argument to the popup, including spaces and Unicode filenames. To inspect the registered command:

```powershell
Get-Item -LiteralPath 'Registry::HKEY_CURRENT_USER\Software\Classes\*\shell\LocalFileConverter\command'
```

Remove the registration:

```powershell
.\scripts\uninstall_context_menu.ps1
```

The context menu is registered for a single selected file at a time. To merge PDFs, open the app without a path and deliberately select multiple PDF files.

## CLI utilities

Check whether dependencies are ready:

```powershell
.\.venv\Scripts\python.exe .\app.py --check-dependencies "C:\path\to\report.docx" --output-format PDF
```

Convert without showing the popup:

```powershell
.\.venv\Scripts\python.exe .\app.py "C:\path\to\photo.png" --output-format JPEG --convert
```

## Build and install

Build the Windows executable:

```powershell
cd "C:\Users\aliwa\Desktop\FileConverter"
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath .\dist --workpath .\build .\pyinstaller.spec
```

The sample Inno Setup script uses the build output at `dist\LocalFileConverter`, installs the app, and registers the per-user context menu.

## Tests

```powershell
cd "C:\Users\aliwa\Desktop\FileConverter"
.\.venv\Scripts\python.exe -m pytest -q
```

The DOCX-to-PDF integration test is skipped when LibreOffice is not installed. The Windows shell-command test executes the registry command template with a simulated Explorer `%1` substitution and a path containing spaces, Unicode, and shell metacharacters.
