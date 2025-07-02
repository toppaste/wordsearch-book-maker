from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdf_canvas


def render_wordsearch_pdf(
    output_path,
    title,
    grid,
    word_list,
    highlights=None,
    solution_output_path=None,
):
    styles = getSampleStyleSheet()

    # --- Puzzle PDF ---
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    # Title in uppercase and centered
    elements.append(Paragraph(title.upper(), styles["Title"]))
    elements.append(Spacer(1, 24))  # Increased space after title

    # Calculate grid size for spacer
    page_width, page_height = letter
    margin = 36
    grid_size = len(grid)
    available_width = (page_width - 2 * margin) * 0.8
    available_height = (page_height - 2 * margin - 100) * 0.8
    cell_size = min(available_width, available_height) / grid_size
    grid_height = cell_size * grid_size
    # Add enough space for the grid and a little extra
    elements.append(Spacer(1, grid_height + 48))

    # Prepare word list in multiple columns, uppercase
    num_columns = 3
    words_upper = [w.upper() for w in word_list]
    rows = (len(words_upper) + num_columns - 1) // num_columns
    word_table_data = []
    for i in range(rows):
        row = []
        for j in range(num_columns):
            idx = i + j * rows
            if idx < len(words_upper):
                row.append(words_upper[idx])
            else:
                row.append("")
        word_table_data.append(row)
    # Set column widths to spread the table across the page
    col_width = (page_width - 2 * margin) / num_columns
    word_table = Table(word_table_data, colWidths=[col_width]*num_columns, hAlign='CENTER')
    word_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Center text in each cell
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(word_table)

    # Custom grid drawing (fit to page, only outer border)
    def draw_grid(canvas, doc):
        page_width, page_height = letter
        margin = 36  # 0.5 inch
        grid_size = len(grid)
        available_width = (page_width - 2 * margin) * 0.8
        available_height = (page_height - 2 * margin - 100) * 0.8
        cell_size = min(available_width, available_height) / grid_size
        grid_width = cell_size * grid_size
        grid_height = cell_size * grid_size
        start_x = (page_width - grid_width) / 2
        start_y = page_height - margin - grid_height - 84  # leave space for title

        # Draw outer border
        canvas.setLineWidth(2)
        canvas.rect(start_x, start_y, grid_width, grid_height)

        # Draw letters
        canvas.setFont("Helvetica-Bold", int(cell_size * 0.6))
        for r, row in enumerate(grid):
            for c, cell_letter in enumerate(row):
                x = start_x + c * cell_size + cell_size / 2
                y = start_y + (grid_size - r - 1) * cell_size + cell_size / 2 - cell_size * 0.2
                canvas.drawCentredString(x, y, cell_letter.upper())

    doc.build(elements, onFirstPage=draw_grid)

    # --- Solution PDF ---
    if solution_output_path and highlights:
        doc_sol = SimpleDocTemplate(solution_output_path, pagesize=letter)
        elements_sol = []
        elements_sol.append(Paragraph(f"{title} - Solution", styles["Title"]))
        elements_sol.append(Spacer(1, 12))

        # Custom drawing for solution grid with highlights
        def draw_solution_grid(canvas, doc):
            grid_size = len(grid)
            cell_size = 20
            margin_x = 72
            margin_y = 500 - grid_size * cell_size

            # Draw grid letters
            for r, row in enumerate(grid):
                for c, letter in enumerate(row):
                    x = margin_x + c * cell_size
                    y = margin_y + (grid_size - r - 1) * cell_size
                    canvas.rect(x, y, cell_size, cell_size)
                    canvas.drawCentredString(
                        x + cell_size / 2, y + cell_size / 2 - 4, letter
                    )

            # Draw highlights if provided
            if highlights:
                for h in highlights:
                    start_r, start_c = h["start"]
                    dr, dc = direction_to_delta(h["direction"])
                    for i in range(h["length"]):
                        rr = start_r + dr * i
                        cc = start_c + dc * i
                        x = margin_x + cc * cell_size
                        y = margin_y + (grid_size - rr - 1) * cell_size
                        canvas.setFillColorRGB(1, 1, 0, alpha=0.3)  # Yellow highlight
                        canvas.rect(x, y, cell_size, cell_size, fill=1, stroke=0)
                canvas.setFillColor(colors.black)  # Reset color

        elements_sol.append(Spacer(1, 200))  # Reserve space for the grid

        doc_sol.build(
            elements_sol,
            onFirstPage=draw_solution_grid,
        )


def direction_to_delta(direction):
    # Map direction string to (dr, dc)
    mapping = {
        "horizontal": (0, 1),
        "horizontal_rev": (0, -1),
        "vertical": (1, 0),
        "vertical_rev": (-1, 0),
        "diagonal_down": (1, 1),
        "diagonal_up": (-1, 1),
        "diagonal_down_rev": (1, -1),
        "diagonal_up_rev": (-1, -1),
    }
    return mapping.get(direction, (0, 1))
