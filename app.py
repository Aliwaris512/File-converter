from __future__ import annotations

import argparse
import sys

from services.conversion_service import ConversionService
from ui.popup import ConversionPopup
from windows.context_menu import install_context_menu, uninstall_context_menu


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LocalFile Converter")
    parser.add_argument("files", nargs="*", default=[], help="One or more file paths to convert")
    parser.add_argument("--explorer", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--install-context-menu", action="store_true", help="Register the Windows Explorer context-menu command")
    parser.add_argument("--uninstall-context-menu", action="store_true", help="Remove the Windows Explorer context-menu command")
    parser.add_argument("--check-dependencies", action="store_true", help="Validate the local conversion dependencies for the supplied files")
    parser.add_argument("--convert", action="store_true", help="Convert supplied files without opening the popup")
    parser.add_argument("--output-format", help="Target output format for dependency checks or direct conversion")
    parser.add_argument("--quality", type=int, default=90, help="Quality setting used for image conversions when --convert is used")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    if args.install_context_menu:
        install_context_menu()
        print("Context menu installed.")
        return 0
    if args.uninstall_context_menu:
        uninstall_context_menu()
        print("Context menu removed.")
        return 0
    if args.explorer:
        if len(args.files) != 1:
            app = ConversionPopup(launch_error="Explorer did not provide exactly one selected file.")
            app.run()
            return 2
        app = ConversionPopup(file_paths=args.files)
        app.run()
        return 0
    if args.check_dependencies:
        if not args.files:
            print("No files supplied to check.")
            return 1
        failed = False
        for file_path in args.files:
            output_format = args.output_format
            if output_format is None:
                supported = ConversionService.get_supported_formats(file_path)
                if not supported:
                    unavailable = ConversionService.get_unavailable_format_messages(file_path)
                    if unavailable:
                        print(f"{file_path}: " + " ".join(unavailable))
                    else:
                        print(f"{file_path}: unsupported file type for local conversion.")
                    failed = True
                    continue
                output_format = supported[0]
            try:
                ConversionService.validate_conversion(file_path, output_format)
            except (RuntimeError, FileNotFoundError, ValueError) as exc:
                print(f"{file_path}: {exc}")
                failed = True
            else:
                print(f"{file_path}: dependencies ready for {output_format} conversion.")
        return 1 if failed else 0
    if args.convert:
        if not args.files:
            print("No files supplied to convert.")
            return 1
        if not args.output_format:
            output_format = ConversionService.get_supported_formats(args.files[0])
            if not output_format:
                unavailable = ConversionService.get_unavailable_format_messages(args.files[0])
                if unavailable:
                    print(f"{args.files[0]}: " + " ".join(unavailable))
                else:
                    print(f"{args.files[0]}: unsupported file type for local conversion.")
                return 1
            selected_format = output_format[0]
        else:
            selected_format = args.output_format.upper()

        try:
            for file_path in args.files:
                output_path = ConversionService.convert_file(file_path, selected_format, quality=args.quality)
                print(f"Converted: {file_path} -> {output_path}")
        except (RuntimeError, FileNotFoundError, ValueError) as exc:
            print(f"Conversion failed: {exc}", file=sys.stderr)
            return 1
        return 0

    app = ConversionPopup(file_paths=args.files if args.files else None)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
