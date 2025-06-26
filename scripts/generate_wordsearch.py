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
    args = parser.parse_args()

    # [TO DO]: handle output folder
    # output folder
    #    if args.output is None:
    #        args.output = os.path.join(
    #            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    #            "test",
    #            "output",
    #        )
    #    if not os.path.exists(args.output):
    #        try:
    #            os.makedirs(args.output)
    #        except Exception as e:
    #            logging.error(f"Failed to create output directory: {e}")
    #            exit(1)

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
        # Save DOCX with grid and solution
        output_docx = f"{item['title'].lower().replace(' ', '_')}_wordsearch.docx"
        if args.output:
            output_docx = os.path.join(args.output, output_docx)
            # Assuming generate_puzzle returns a WordSearch object with .grid, .words, and .solution attributes
            docx_export.save_wordsearch_to_docx(
                output_docx,
                item["title"],
                puzzle.grid,
                puzzle.words,
                puzzle.solution
            )
