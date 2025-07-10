import os
from src.wordsearch import pdf_render

def test_render_wordsearch_pdf(tmp_path):
    # Minimal grid and word list
    grid = [
        ["A", "B", "C", "D", "E", "F"],
        ["G", "H", "I", "J", "K", "L"],
        ["M", "N", "O", "P", "Q", "R"],
        ["S", "T", "U", "V", "W", "X"],
        ["Q", "R", "S", "T", "U", "V"],
        ["W", "X", "Y", "Z", "A", "B"],
    ]
    words = [
        "ABC", "BAZ", "AGM", "BVX",
        "AHO", "FKP", "WRU", "BUV"
    ]
    highlights = [
        {"word": "ABC", "start": (0, 0), "direction": "horizontal_left_to_right", "length": 3},
        {"word": "BAZ", "start": (5, 5), "direction": "horizontal_right_to_left", "length": 3},
        {"word": "AGM", "start": (0, 0), "direction": "vertical_up_to_down", "length": 3},
        {"word": "BVX", "start": (5, 5), "direction": "vertical_down_to_up", "length": 3},
        {"word": "AHO", "start": (0, 0), "direction": "diagonal_up_left_to_down_right", "length": 3},
        {"word": "FKP", "start": (5, 0), "direction": "diagonal_up_right_to_down_left", "length": 3},
        {"word": "WRU", "start": (0, 5), "direction": "diagonal_down_left_to_up_right", "length": 3},
        {"word": "BUV", "start": (5, 5), "direction": "diagonal_down_right_to_up_left", "length": 3},
    ]

    output_pdf = tmp_path / "test_wordsearch.pdf"
    solution_pdf = tmp_path / "test_wordsearch_solution.pdf"

    try:
        pdf_render.render_wordsearch_pdf(
            str(output_pdf),
            "Test Puzzle",
            grid,
            words,
            highlights=highlights,
            solution_output_path=str(solution_pdf),
            highlight_style="rect"
        )
    except Exception as e:
        print(f"Error during PDF generation: {e}")
        raise

    assert output_pdf.exists()
    assert solution_pdf.exists()

    # Uncomment the following lines to see the generated files
    # print(f"Puzzle PDF: {output_pdf}")
    # print(f"Solution PDF: {solution_pdf}")