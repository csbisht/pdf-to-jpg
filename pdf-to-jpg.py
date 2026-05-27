import fitz  # PyMuPDF  (only dependency)
import argparse
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _render_pages(pdf_document: fitz.Document, matrix: fitz.Matrix) -> list:
    """Render every page and return a list of fitz RGB Pixmaps."""
    pixmaps = []
    for page in pdf_document:
        pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csRGB, alpha=False)
        pixmaps.append(pix)
    return pixmaps


def _stack_pixmaps(pixmaps: list) -> fitz.Pixmap:
    """
    Stack a list of fitz Pixmaps vertically into one combined Pixmap.

    Uses PyMuPDF's writable samples_mv memoryview (available since PyMuPDF 1.18).
    Pages narrower than the widest page are left-aligned on a white background.
    """
    max_width   = max(p.width  for p in pixmaps)
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
        total    = len(pdf_document)
        pixmaps  = _render_pages(pdf_document, matrix)
    finally:
        if pdf_document is not None:
            pdf_document.close()

    print(f"'{pdf_path}'  —  {total} page(s), {dpi} DPI")

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
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to JPG image(s).  Requires: PyMuPDF (pip install pymupdf)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python3 pdf_2_jpg.py report.pdf\n"
            "             → report/report.jpg          (all pages combined into one file)\n\n"
            "  python3 pdf_2_jpg.py report.pdf -p\n"
            "             → report/report_1.jpg, report_2.jpg, …\n\n"
            "  python3 pdf_2_jpg.py report.pdf -p --name invoice\n"
            "             → report/invoice_1.jpg, invoice_2.jpg, …\n\n"
            "  python3 pdf_2_jpg.py report.pdf out_dir -p --dpi 200 --quality 85"
        ),
    )
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument(
        "output_folder",
        nargs="?",
        default=None,
        help="Directory to save output image(s)  (default: <pdf_stem>/)",
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
        help="Base name for output files, no extension  (default: PDF filename stem)",
    )
    parser.add_argument("--dpi",     type=int, default=150, help="Render resolution in DPI  (default: 150)")
    parser.add_argument("--quality", type=int, default=95,  help="JPEG quality 1–100  (default: 95)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    pdf_to_jpg(
        args.pdf_path,
        args.output_folder,
        args.output_name,
        args.per_page,
        args.dpi,
        args.quality,
    )
