# This script generates a word search puzzle using the wordsearch module.
import argparse
import json
import logging
import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from wordsearch import generate
from wordsearch import docx_export
from wordsearch import pdf_render

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file, json format")
    parser.add_argument("-o", "--output", help="output folder")
    parser.add_argument(
        "-b",
        "--basic",
        action="store_true",
        help="only basic directions: left to right, top to bottom, diagonal from top left to bottom right",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="generate PDF output"
    )
    parser.add_argument(
        "--docx",
        action="store_true",
        help="generate DOCX output"
    )
    args = parser.parse_args()

    # get input file data
    input_file = os.path.join(os.getcwd(), args.input)
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        exit(1)

    for j, item in enumerate(data["puzzles"]):

        if {"title", "words"} <= item.keys():
            # default size
            size = 15
            if "size" in item:
                size = item["size"]

        puzzle = generate.generate_puzzle(
            item["title"],
            item["words"],
            size,
            args.basic,
            verbose=True,
        )

        if puzzle is None:
            logging.error(f"Failed to generate puzzle for {item['title']}")
            continue

        if args.output:

            if args.docx:
                # Save DOCX with grid and solution
                output_docx = (
                    f"{item['title'].lower().replace(' ', '_')}_wordsearch.docx"
                )
                output_docx = os.path.join(args.output, output_docx)
                docx_export.save_wordsearch_to_docx(
                    output_docx,
                    item["title"],
                    puzzle.grid,
                    puzzle.words,
                    puzzle.solution,
                )

            if args.pdf:
                # Get highlights for the solution
                highlights = puzzle.get_highlights()

                # Save PDF with grid and solution
                output_pdf = f"{item['title'].lower().replace(' ', '_')}_wordsearch.pdf"
                output_pdf = os.path.join(args.output, output_pdf)
                pdf_render.render_wordsearch_pdf(
                    output_pdf,
                    item["title"],
                    puzzle.grid,
                    puzzle.words,
                    highlights=highlights,
                )
