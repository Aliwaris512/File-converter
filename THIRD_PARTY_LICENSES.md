# Third-party licenses and attributions

This project includes or depends on the following third-party packages.

## Python packages

### Pillow
- License: MIT License
- Project: https://python-pillow.org/
- Usage: image decoding and encoding for PNG, JPEG, WEBP, and related formats.

### PyMuPDF
- License: AGPL-3.0-or-later for some usages; check the exact distribution model and license terms for your deployment.
- Project: https://pymupdf.readthedocs.io/
- Usage: local PDF parsing and page extraction.

### ReportLab
- License: BSD-style license
- Project: https://reportlab.com/
- Usage: creating PDF documents from text content.

### python-docx
- License: MIT License
- Project: https://python-docx.readthedocs.io/
- Usage: used by the local PDF-to-Word conversion engine.

### pdf2docx
- License: AGPL-3.0-or-later; confirm current terms before redistribution.
- Project: https://github.com/ArtifexSoftware/pdf2docx
- Usage: reconstructing text, paragraphs, images, and layout elements from PDFs as DOCX.

### openpyxl
- License: MIT License
- Project: https://openpyxl.readthedocs.io/
- Usage: local XLSX/CSV conversion.

### PyInstaller
- License: GNU General Public License v2.0 or a commercial license
- Project: https://pyinstaller.org/
- Usage: executable packaging for Windows distribution.

### pytest
- License: MIT License
- Project: https://pytest.org/
- Usage: automated testing.

## Operating-system dependencies

### FFmpeg
- License: LGPL/GPL depending on build configuration and codec enablement
- Project: https://www.ffmpeg.org/
- Usage: local audio and video conversion engine.
- Important: confirm the exact FFmpeg build you distribute complies with your licensing and redistribution plan.

### LibreOffice (not bundled in this project)
- License: LGPL/MPL-based stack with separate distribution terms depending on the installer and usage model
- Project: https://www.libreoffice.org/
- Usage: optional local engine used for DOC/DOCX/PPTX/HTML to PDF conversions.

This project follows an offline-first design and does not depend on cloud conversion services or telemetry. Before redistributing a built installer, verify all third-party components, their licenses, and the packaging terms of your deployment target.
