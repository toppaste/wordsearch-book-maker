import argparse
import json
import os
import tempfile
from PyPDF2 import PdfMerger
from src.wordsearch import generate
from src.wordsearch.pdf_render import render_wordsearch_pdf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file, json format")
    parser.add_argument("-o", "--output", help="output folder", required=True)
    args = parser.parse_args()

    # Read input data
    with open(args.input, "r") as f:
        data = json.load(f)

    puzzle_name = os.path.splitext(os.path.basename(args.input))[0]
    args.output = os.path.join(args.output, f"{puzzle_name}_book.pdf")
    puzzles = []
    solutions = []

    # Generate puzzles and solutions
    for item in data["puzzles"]:
        size = item.get("size", 15)
        puzzle = generate.generate_puzzle(
            item["title"],
            item["words"],
            size,
            basic=False,
            verbose=False,
        )
        if puzzle is None:
            continue
        puzzles.append((item["title"], puzzle.grid, puzzle.words))
        solutions.append((item["title"], puzzle.grid, puzzle.get_highlights()))

    # Use a temp directory for intermediate PDFs
    with tempfile.TemporaryDirectory() as tmpdir:
        merger = PdfMerger()
        # --- Puzzles: one per page ---
        for idx, (title, grid, words) in enumerate(puzzles):
            puzzle_pdf = os.path.join(tmpdir, f"puzzle_{idx}.pdf")
            render_wordsearch_pdf(
                puzzle_pdf,
                title,
                grid,
                words,
                highlights=None,
                solution_output_path=None,
                highlight_style="rect",
            )
            merger.append(puzzle_pdf)

        # --- Solutions: 4 per page ---
        # Group solutions in chunks of 4
        for i in range(0, len(solutions), 4):
            chunk = solutions[i : i + 4]
            solution_pdf = os.path.join(tmpdir, f"solution_{i//4}.pdf")
            create_solution_page(chunk, solution_pdf)
            merger.append(solution_pdf)

        # Write the merged PDF
        merger.write(args.output)
        merger.close()  # <--- Add this line!
        print(f"Book PDF generated: {args.output}")


def create_solution_page(solutions_chunk, output_pdf):
    """
    Draws up to 4 solution grids on a single page and saves as PDF.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    page_width, page_height = letter
    margin = 36
    grid_area = (page_width - 2 * margin) / 2  # 2 columns
    grid_positions = [
        (margin, page_height / 2 + margin / 2),  # Top-left
        (page_width / 2 + margin / 2, page_height / 2 + margin / 2),  # Top-right
        (margin, margin),  # Bottom-left
        (page_width / 2 + margin / 2, margin),  # Bottom-right
    ]

    c = canvas.Canvas(output_pdf, pagesize=letter)
    for idx, (title, grid, highlights) in enumerate(solutions_chunk):
        grid_size = len(grid)
        cell_size = grid_area / grid_size
        pos_x, pos_y = grid_positions[idx]
        # Import the solution grid drawing logic from your pdf_render
        from src.wordsearch.pdf_render import draw_solution_grid_for_book

        draw_solution_grid_for_book(c, pos_x, pos_y, grid, highlights, cell_size, title)
    c.showPage()
    c.save()


# You need to add this helper in src/wordsearch/pdf_render.py:
# (If not present, add this function to draw a solution grid at a given position and size)
"""
def draw_solution_grid_for_book(canvas, pos_x, pos_y, grid, highlights, cell_size, title):
    # Draw title
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawCentredString(pos_x + (len(grid) * cell_size) / 2, pos_y + len(grid) * cell_size + 14, title + " - Solution")
    # Draw outer border
    canvas.setLineWidth(1.5)
    canvas.rect(pos_x, pos_y, len(grid) * cell_size, len(grid) * cell_size)
    # Draw letters
    canvas.setFont("Helvetica-Bold", int(cell_size * 0.6))
    for r, row in enumerate(grid):
        for c, cell_letter in enumerate(row):
            x = pos_x + c * cell_size + cell_size / 2
            y = pos_y + (len(grid) - r - 1) * cell_size + cell_size / 2 - cell_size * 0.2
            canvas.drawCentredString(x, y, cell_letter.upper())
    # Draw highlights (rectangles)
    # ... (reuse your highlight drawing code, using pos_x/pos_y as origin and cell_size)
"""

if __name__ == "__main__":
    main()
