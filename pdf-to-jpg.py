import fitz  # PyMuPDF  (only dependency)
import argparse
import sys
from pathlib import Path
from tqdm import tqdm  # progress bar  (pip install tqdm)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _render_pages(pdf_document: fitz.Document, matrix: fitz.Matrix, label: str = "") -> list:
    """Render every page and return a list of fitz RGB Pixmaps."""
    pixmaps = []
    desc = f"Rendering {label}" if label else "Rendering pages"
    for page in tqdm(pdf_document, desc=desc, unit="page", leave=True):
        pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
        pixmaps.append(pix)
    return pixmaps


def _stack_pixmaps(pixmaps: list) -> fitz.Pixmap:
    """
    Stack a list of fitz Pixmaps vertically into one combined Pixmap.

    Uses PyMuPDF's writable samples_mv memoryview (available since PyMuPDF 1.18).
    Pages narrower than the widest page are left-aligned on a white background.
    """
    max_width    = max(p.width  for p in pixmaps)
    total_height = sum(p.height for p in pixmaps)
    n = 3  # RGB channels (no alpha)

    # Create an empty RGB pixmap and fill it white
    combined = fitz.Pixmap(
        fitz.csRGB,
        fitz.IRect(0, 0, max_width, total_height),
        False,  # no alpha
    )
    combined.set_rect(combined.irect, (255, 255, 255))

    # Write each page's rows into the combined buffer via a writable memoryview
    mv = combined.samples_mv          # writable memoryview (PyMuPDF >= 1.18)
    y_offset = 0
    for pix in pixmaps:
        src = pix.samples             # bytes: row-major RGB
        for row in range(pix.height):
            dst_pos = (y_offset + row) * max_width * n
            src_pos = row * pix.width * n
            mv[dst_pos : dst_pos + pix.width * n] = src[src_pos : src_pos + pix.width * n]
        y_offset += pix.height

    return combined


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def pdf_to_jpg(
    pdf_path: str,
    output_folder: str = None,
    output_name: str = None,
    per_page: bool = False,
    dpi: int = 150,
    quality: int = 95,
    _label: str = "",
) -> None:
    """
    Convert a PDF to JPG image(s).

    Default (per_page=False):
        All pages are merged into ONE vertically-stacked JPG.
        e.g.  report.pdf  →  report/report.jpg

    Per-page mode (-p):
        Each page is saved as its own JPG.
        e.g.  report.pdf  →  report/report_1.jpg, report_2.jpg, …

    Args:
        pdf_path (str):      Path to the input PDF file.
        output_folder (str): Output directory.
                             Defaults to <pdf_dir>/<pdf_stem>/.
        output_name (str):   Base name for output files (no extension).
                             Defaults to the PDF filename stem.
        per_page (bool):     Save one file per page instead of combining.
        dpi (int):           Render resolution in DPI (default: 150).
        quality (int):       JPEG quality 1–100 (default: 95).
        _label (str):        Internal — short label shown in progress bar (used by batch mode).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if output_folder is None:
        output_folder = pdf_path.parent / pdf_path.stem

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    if output_name is None:
        output_name = pdf_path.stem

    zoom   = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    pdf_document = None
    try:
        pdf_document = fitz.open(str(pdf_path))
        total   = len(pdf_document)
        print(f"\n'{pdf_path.name}'  —  {total} page(s), {dpi} DPI")
        pixmaps = _render_pages(pdf_document, matrix, label=_label or pdf_path.name)
    finally:
        if pdf_document is not None:
            pdf_document.close()

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    if per_page:
        # One file per page  →  <name>_1.jpg, <name>_2.jpg, …
        for i, pix in enumerate(pixmaps):
            output_file = output_folder / f"{output_name}_{i + 1}.jpg"
            pix.save(str(output_file), jpg_quality=quality)
            print(f"  Saved: {output_file}")
        print(f"Done. {total} file(s) saved to '{output_folder}'.")
    else:
        # All pages combined into one file  →  <name>.jpg
        combined    = _stack_pixmaps(pixmaps)
        output_file = output_folder / f"{output_name}.jpg"
        combined.save(str(output_file), jpg_quality=quality)
        print(f"  Saved: {output_file}")
        print(f"Done. All {total} page(s) combined into '{output_file}'.")


# ---------------------------------------------------------------------------
# Batch mode
# ---------------------------------------------------------------------------

def batch_convert(
    folder: str,
    output_folder: str = None,
    per_page: bool = False,
    dpi: int = 150,
    quality: int = 95,
) -> None:
    """
    Convert all PDF files in a folder to JPG image(s), one at a time.

    Each PDF is fully processed and freed from memory before the next one
    starts — memory usage stays flat regardless of folder size.

    Args:
        folder (str):        Path to the folder containing PDF files.
        output_folder (str): Root output directory.
                             Defaults to a subfolder next to each PDF.
        per_page (bool):     Save one JPG per page instead of combining.
        dpi (int):           Render resolution in DPI (default: 150).
        quality (int):       JPEG quality 1–100 (default: 95).
    """
    folder     = Path(folder)
    pdf_files  = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{folder}'.")
        return

    total_files = len(pdf_files)
    print(f"Batch mode — {total_files} PDF file(s) found in '{folder}'.\n")

    # Outer progress bar — one tick per file
    for pdf_file in tqdm(pdf_files, desc="Overall progress", unit="file", position=0):
        out = str(Path(output_folder) / pdf_file.stem) if output_folder else None
        pdf_to_jpg(
            str(pdf_file),
            out,
            None,       # output_name — defaults to PDF stem
            per_page,
            dpi,
            quality,
            _label=pdf_file.name,
        )

    print(f"\nBatch complete. {total_files} PDF(s) converted.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Convert PDF pages to JPG image(s).  Requires: PyMuPDF + tqdm\n"
            "  pip install pymupdf tqdm\n\n"
            "Pass a FILE to convert one PDF.\n"
            "Pass a FOLDER to batch-convert all PDFs inside it."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  # Single file — all pages combined into one JPG\n"
            "  python pdf-to-jpg.py report.pdf\n"
            "             → report/report.jpg\n\n"
            "  # Single file — one JPG per page\n"
            "  python pdf-to-jpg.py report.pdf -p\n"
            "             → report/report_1.jpg, report_2.jpg, …\n\n"
            "  # Single file — custom name and settings\n"
            "  python pdf-to-jpg.py report.pdf -p --name invoice --dpi 200 --quality 85\n\n"
            "  # Batch — convert all PDFs in a folder\n"
            "  python pdf-to-jpg.py ./invoices/\n"
            "             → invoices/jan/jan.jpg, invoices/feb/feb.jpg, …\n\n"
            "  # Batch — all PDFs in folder, per-page, custom output dir\n"
            "  python pdf-to-jpg.py ./invoices/ ./output/ -p --dpi 200"
        ),
    )
    parser.add_argument(
        "input",
        help="Path to a PDF file  OR  a folder containing PDF files (batch mode)",
    )
    parser.add_argument(
        "output_folder",
        nargs="?",
        default=None,
        help="Directory to save output image(s)  (default: next to each PDF)",
    )
    parser.add_argument(
        "-p", "--per-page",
        dest="per_page",
        action="store_true",
        help="Save one JPG per page instead of combining all pages into one file",
    )
    parser.add_argument(
        "--name",
        dest="output_name",
        default=None,
        metavar="NAME",
        help="Base name for output file(s), no extension  (single-file mode only)",
    )
    parser.add_argument("--dpi",     type=int, default=150, help="Render resolution in DPI  (default: 150)")
    parser.add_argument("--quality", type=int, default=95,  help="JPEG quality 1–100  (default: 95)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args       = parser.parse_args()
    input_path = Path(args.input)

    if input_path.is_dir():
        # ── Batch mode ──────────────────────────────────────────────────────
        if args.output_name:
            print("Warning: --name is ignored in batch mode.")
        batch_convert(
            str(input_path),
            args.output_folder,
            args.per_page,
            args.dpi,
            args.quality,
        )
    else:
        # ── Single file mode ─────────────────────────────────────────────────
        pdf_to_jpg(
            str(input_path),
            args.output_folder,
            args.output_name,
            args.per_page,
            args.dpi,
            args.quality,
        )
