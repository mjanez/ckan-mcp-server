#!/usr/bin/env python3
"""Compile gettext .po files to .mo format.

Uses msgfmt if available, otherwise falls back to pure Python implementation.
"""

import subprocess
import sys
from pathlib import Path


def compile_with_msgfmt(po_file, mo_file):
    """Compile .po file using GNU msgfmt command.

    Args:
        po_file: Path to source .po file
        mo_file: Path to destination .mo file

    Returns:
        True if compilation succeeded
    """
    subprocess.run(
        ["msgfmt", "-o", str(mo_file), str(po_file)],
        capture_output=True,
        text=True,
        check=True
    )
    return True


def compile_with_python(po_file, mo_file):
    """Compile .po file using pure Python fallback.

    Args:
        po_file: Path to source .po file
        mo_file: Path to destination .mo file

    Returns:
        True if compilation succeeded, False otherwise

    Note:
        Requires polib package to be installed
    """
    try:
        import polib
        po = polib.pofile(str(po_file))
        po.save_as_mofile(str(mo_file))
        return True
    except ImportError:
        print("Pure Python fallback requires: pip install polib")
        return False
    except (IOError, OSError) as e:
        print(f"  Python compilation error: {e}")
        return False


def compile_translations():
    """Compile all .po files in locales directory to .mo format.

    Returns:
        Exit code: 0 if all files compiled successfully, 1 otherwise
    """
    i18n_dir = Path(__file__).parent
    locales_dir = i18n_dir / "locales"

    if not locales_dir.exists():
        print(f"Error: {locales_dir} does not exist")
        return 1

    po_files = list(locales_dir.glob("*/LC_MESSAGES/*.po"))

    if not po_files:
        print("No .po files found")
        return 1

    print(f"Found {len(po_files)} .po files to compile")
    print("=" * 60)

    try:
        subprocess.run(["msgfmt", "--version"], capture_output=True, check=True)
        use_msgfmt = True
        print(" Using GNU msgfmt (faster)\n")
    except (subprocess.CalledProcessError, FileNotFoundError):
        use_msgfmt = False
        print("GNU msgfmt not found, using Python fallback")
        print("   For better performance: sudo apt-get install gettext\n")

    success_count = 0
    for po_file in po_files:
        mo_file = po_file.with_suffix(".mo")
        rel_path = po_file.relative_to(i18n_dir)
        print(f"Compiling: {rel_path}")

        try:
            if use_msgfmt:
                success = compile_with_msgfmt(po_file, mo_file)
            else:
                success = compile_with_python(po_file, mo_file)

            if success:
                print(f"    Created: {mo_file.relative_to(i18n_dir)}\n")
                success_count += 1
            else:
                print("Failed to compile\n")
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Error: {e}\n")

    print("=" * 60)
    print(f"Compilation complete: {success_count}/{len(po_files)} successful")

    if success_count < len(po_files):
        print("\nTip: Install GNU gettext for reliable compilation:")
        print("   Ubuntu/Debian: sudo apt-get install gettext")
        print("   macOS: brew install gettext")

    return 0 if success_count == len(po_files) else 1


if __name__ == "__main__":
    sys.exit(compile_translations())
