from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdf_canvas
import math


def render_wordsearch_pdf(
    output_path,
    title,
    grid,
    word_list,
    highlights=None,
    solution_output_path=None,
    highlight_style="rect",  # Add this parameter: "rect" or "fill"
):
    styles = getSampleStyleSheet()

    small_title_style = ParagraphStyle(
        name='SmallTitle',
        parent=styles['Title'],
        fontSize=int(styles['Title'].fontSize * 0.8)
    )

    page_margin = 36 # 0.5 inch margin
    # cell_margin = 12  # 0.2 inch margin for table cells

    # --- Puzzle PDF ---
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    # Title in uppercase and centered
    elements.append(Paragraph(title.upper(), styles["Title"]))
    elements.append(Spacer(1, 24))  # Increased space after title

    # Calculate grid size for spacer
    page_width, page_height = letter
    grid_size = len(grid)
    available_width = (page_width - 2 * page_margin) * 0.8
    available_height = (page_height - 2 * page_margin - 100) * 0.8
    cell_size = min(available_width, available_height) / grid_size
    grid_height = cell_size * grid_size
    # Add enough space for the grid and a little extra
    elements.append(Spacer(1, grid_height + 40))

    # Prepare word list in multiple columns, uppercase
    num_columns = 4
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
    col_width = (page_width - 4 * page_margin) / num_columns
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
        grid_size = len(grid)
        available_width = (page_width - 2 * page_margin) * 0.8
        available_height = (page_height - 2 * page_margin) * 0.8
        cell_size = min(available_width, available_height) / grid_size
        grid_width = cell_size * grid_size
        grid_height = cell_size * grid_size
        grid_gap_y = 84  # delta from the top of the page to the grid
        start_x = (page_width - grid_width) / 2
        start_y = page_height - page_margin - grid_gap_y  # leave space for title

        # Draw outer border
        canvas.setLineWidth(2)
        canvas.rect(start_x, start_y - grid_height, grid_width, grid_height)

        # Draw letters
        canvas.setFont("Helvetica-Bold", int(cell_size * 0.6))
        for r, row in enumerate(grid):
            for c, cell_letter in enumerate(row):
                x = start_x + c * cell_size + cell_size / 2
                #y = start_y + (grid_size - r - 1) * cell_size + cell_size / 2 - cell_size * 0.2
                y = start_y - r * cell_size - cell_size / 2  - cell_size * 0.2 # Adjust y for centering
                canvas.drawCentredString(x, y, cell_letter.upper())

                # debug code: draw cell borders to check highlight positions
                # canvas.setStrokeColorRGB(0, 0, 0)  # Black
                # canvas.setLineWidth(0.5)
                # canvas.rect(start_x + c * cell_size, start_y - r * cell_size - cell_size, cell_size, cell_size, stroke=1, fill=0)  # Draw cell border


    doc.build(elements, onFirstPage=draw_grid)

    # --- Solution PDF ---
    if solution_output_path and highlights:
        doc_sol = SimpleDocTemplate(solution_output_path, pagesize=letter)
        elements_sol = []
        # Smaller title
        small_title_style = ParagraphStyle(
            name='SmallTitle',
            parent=styles['Title'],
            fontSize=int(styles['Title'].fontSize * 0.8)
        )
        elements_sol.append(Paragraph(f"{title.upper()} - Solution", small_title_style))
        elements_sol.append(Spacer(1, 18))

        # Custom drawing for solution grid with highlights
        def draw_solution_grid(canvas, doc):
            page_width, page_height = letter
            page_margin = 36
            grid_size = len(grid)
            # Calculate available space and cell size
            available_width = (page_width - 2 * page_margin) * 0.45
            available_height = (page_height - 2 * page_margin - 100) * 0.45
            cell_size = min(available_width, available_height) / grid_size
            grid_width = cell_size * grid_size
            grid_height = cell_size * grid_size

            grid_gap_y = 72  # delta from the top of the page to the grid
            start_x = (page_width - grid_width) / 2
            start_y = page_height - page_margin - grid_gap_y  # Top of the grid

            # Draw only the outer border
            canvas.setLineWidth(1.5)
            canvas.rect(start_x, start_y - grid_height, grid_width, grid_height)

            # Draw letters (no cell borders)
            canvas.setFont("Helvetica-Bold", int(cell_size * 0.6))
            for r, row in enumerate(grid):
                for c, cell_letter in enumerate(row):
                    x = start_x + c * cell_size + cell_size / 2
                    y = start_y - r * cell_size - cell_size / 2  - cell_size * 0.2 # Adjust y for centering
                    canvas.drawCentredString(x, y, cell_letter.upper())
                    
                    # debug code: draw cell borders to check highlight positions
                    # canvas.setStrokeColorRGB(0, 0, 0)  # Black
                    # canvas.setLineWidth(0.5)
                    # canvas.rect(start_x + c * cell_size, start_y - r * cell_size - cell_size, cell_size, cell_size, stroke=1, fill=0)  # Draw cell border


            # Draw highlights if provided
            if highlights:
                for h in highlights:
                    start_c, start_r = h["start"]
                    dc, dr = direction_to_delta(h["direction"])
                    length = h["length"]

                    # Calculate the rectangle's start and end positions
                    end_r = start_r + dr * (length - 1)
                    end_c = start_c + dc * (length - 1)

                    # Find top-left and bottom-right corners (regardless of direction)
                    min_r = min(start_r, end_r)
                    max_r = max(start_r, end_r)
                    min_c = min(start_c, end_c)
                    max_c = max(start_c, end_c)

                    x = start_x + min_c * cell_size
                    y = start_y - min_r * cell_size
                    # width = (abs(max_c - min_c) + 1) * cell_size
                    # height = (abs(max_r - min_r) + 1) * cell_size

                    if highlight_style == "fill":
                        # Yellow highlight fill for each letter (legacy)
                        for i in range(length):
                            rr = start_r + dr * i
                            cc = start_c + dc * i
                            lx = start_x + cc * cell_size
                            ly = start_y - rr * cell_size - cell_size
                            canvas.setFillColorRGB(1, 1, 0, alpha=0.3)
                            canvas.rect(lx, ly, cell_size, cell_size, fill=1, stroke=0)
                    elif highlight_style == "rect":
                        rect_width_factor = 0.6
                        # Compute rectangle parameters
                        if dr == 0:  # Horizontal
                            rect_width = cell_size * length
                            rect_height = cell_size * rect_width_factor
                            angle = 0
                        elif dc == 0:  # Vertical
                            rect_width = cell_size * rect_width_factor
                            rect_height = cell_size * length
                            angle = 0
                        else:  # Diagonal
                            rect_width = (cell_size * length * 1.42) - (cell_size * (1 - rect_width_factor))
                            rect_height = cell_size * rect_width_factor
                            # Angle in degrees: atan2(dr, dc)
                            angle = math.degrees(math.atan2(dr, dc))

                        # Center of the rectangle (middle of the word)
                        mid_r = start_r + dr * (length - 1) / 2
                        mid_c = start_c + dc * (length - 1) / 2
                        center_x = start_x + (mid_c + 0.5) * cell_size
                        center_y = start_y - (mid_r + 0.5) * cell_size

                        # Draw rotated rounded rectangle
                        canvas.saveState()
                        canvas.translate(center_x, center_y)
                        canvas.rotate(-angle)  # Negative because PDF y-axis is down
                        canvas.setStrokeColorRGB(1, 0.6, 0)
                        canvas.setLineWidth(1.5)
                        radius = cell_size * 0.35
                        canvas.roundRect(-rect_width/2, -rect_height/2, rect_width, rect_height, radius, fill=0, stroke=1)
                        canvas.restoreState()

            # elements_sol.append(Spacer(1, grid_height + 24))  # Space after grid if needed

            # Draw a horizontal line at the bottom of the grid
            #canvas.setLineWidth(1)
            #canvas.line(page_margin, start_y - grid_height - page_margin, page_width - page_margin, start_y - grid_height - page_margin)

        doc_sol.build(
            elements_sol,
            onFirstPage=draw_solution_grid,
        )


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
    if highlights:
        for h in highlights:
            rect_width_factor = 0.6
            start_c, start_r = h["start"]
            dc, dr = direction_to_delta(h["direction"])
            length = h["length"]
            # Compute rectangle parameters (horizontal/vertical/diagonal)
            if dr == 0:  # Horizontal
                rect_width = cell_size * length
                rect_height = cell_size * rect_width_factor
                angle = 0
            elif dc == 0:  # Vertical
                rect_width = cell_size * rect_width_factor
                rect_height = cell_size * length
                angle = 0
            else:  # Diagonal
                rect_width = (cell_size * length * 1.42) - (cell_size * (1-rect_width_factor))
                rect_height = cell_size * rect_width_factor
                import math
                angle = math.degrees(math.atan2(dr, dc))
            # Center of the rectangle (middle of the word)
            mid_r = start_r + dr * (length - 1) / 2
            mid_c = start_c + dc * (length - 1) / 2
            center_x = pos_x + (mid_c + 0.5) * cell_size
            center_y = pos_y + (len(grid) - (mid_r + 0.5)) * cell_size
            # Draw rotated rounded rectangle
            canvas.saveState()
            canvas.translate(center_x, center_y)
            canvas.rotate(-angle)
            canvas.setStrokeColorRGB(1, 0.6, 0)
            canvas.setLineWidth(1.5)
            radius = cell_size * 0.35
            canvas.roundRect(-rect_width/2, -rect_height/2, rect_width, rect_height, radius, fill=0, stroke=1)
            canvas.restoreState()


def direction_to_delta(direction):
    # Map direction string to (dr, dc)
    mapping = {
        "horizontal_left_to_right":       (  1,  0 ),  # →
        "horizontal_right_to_left":       ( -1,  0 ),  # ←
        "vertical_up_to_down":            (  0,  1 ),  # ↓
        "vertical_down_to_up":            (  0, -1 ),  # ↑
        "diagonal_up_left_to_down_right": (  1,  1 ),  # ↘
        "diagonal_down_right_to_up_left": ( -1, -1 ),  # ↖
        "diagonal_up_right_to_down_left": ( -1,  1 ),  # ↙
        "diagonal_down_left_to_up_right": (  1, -1 ),  # ↗
    }
    return mapping.get(direction, (0, 1))
