import logging
import os
import random
import string
from enum import Enum, auto

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


class Direction(Enum):
    HORIZONTAL_LEFT_TO_RIGHT = auto()
    HORIZONTAL_RIGHT_TO_LEFT = auto()
    VERTICAL_UP_TO_DOWN = auto()
    VERTICAL_DOWN_TO_UP = auto()
    DIAGONAL_UP_LEFT_TO_DOWN_RIGHT = auto()
    DIAGONAL_DOWN_RIGHT_TO_UP_LEFT = auto()
    DIAGONAL_UP_RIGHT_TO_DOWN_LEFT = auto()
    DIAGONAL_DOWN_LEFT_TO_UP_RIGHT = auto()
    UNKNOWN = auto()

def parse_solution_entry(word, pos_str):
    row, col, dr, dc = map(int, pos_str.split(","))
    # Map direction
    if dr == 0 and dc == 1:
        direction = Direction.HORIZONTAL_LEFT_TO_RIGHT
    elif dr == 0 and dc == -1:
        direction = Direction.HORIZONTAL_RIGHT_TO_LEFT
    elif dr == 1 and dc == 0:
        direction = Direction.VERTICAL_UP_TO_DOWN
    elif dr == -1 and dc == 0:
        direction = Direction.VERTICAL_DOWN_TO_UP
    elif dr == 1 and dc == 1:
        direction = Direction.DIAGONAL_UP_LEFT_TO_DOWN_RIGHT
    elif dr == -1 and dc == -1:
        direction = Direction.DIAGONAL_DOWN_RIGHT_TO_UP_LEFT
    elif dr == 1 and dc == -1:
        direction = Direction.DIAGONAL_UP_RIGHT_TO_DOWN_LEFT
    elif dr == -1 and dc == 1:
        direction = Direction.DIAGONAL_DOWN_LEFT_TO_UP_RIGHT
    else:
        direction = Direction.UNKNOWN
    return {
        "word": word,
        "start": (col, row),
        "direction": direction.name.lower(),
        "length": len(word),
    }


class WordSearch(object):
    def __init__(self, title, words, size, basic=True):
        self.title = title
        self.words = words
        self.size = size
        self.failed_words = []
        self.solution = []

        self.grid = self.create_grid()

        # Sort words by length (longest first)
        sorted_words = sorted(words, key=lambda w: -len(w.replace(" ", "")))

        # [TO-DO]: add a check for not alphebetical characters, e.g. "-" ...
        for word in sorted_words:
            word_clean = word.upper().replace(" ", "")
            placed = False
            if basic:
                placed = self.place_word_in_grid_basic(word_clean)
            else:
                placed = self.place_word_in_grid_advanced(word_clean)
            if not placed:
                # logging.warning(f"Could not place the word '{word}' in puzzle '{self.title}'.")
                self.failed_words.append(word)

        self.fill_empty_spaces(self.grid)

    def create_grid(self):
        # Create empty grid
        return [[" " for _ in range(self.size)] for _ in range(self.size)]

    def place_word_in_grid_basic(self, word):
        directions = [
            (1, 0),  # horizontal
            (0, 1),  # vertical
            (1, 1),  # diagonal
        ]
        return self._find_best_position(word, directions)

    def place_word_in_grid_advanced(self, word):
        directions = [
            (0, 1),  # horizontal left->right
            (0, -1),  # horizontal right->left
            (1, 0),  # vertical top->bottom
            (-1, 0),  # vertical bottom->top
            (1, 1),  # diagonal down-right
            (-1, -1),  # diagonal up-left
            (1, -1),  # diagonal down-left
            (-1, 1),  # diagonal up-right
        ]
        return self._find_best_position(word, directions)

    def _find_best_position(self, word, directions):
        best_positions = []
        max_overlap = -1
        word_length = len(word)

        for dr, dc in directions:
            for row in range(self.size):
                for col in range(self.size):
                    # Check if word fits
                    end_row = row + dr * (word_length - 1)
                    end_col = col + dc * (word_length - 1)
                    if not (0 <= end_row < self.size and 0 <= end_col < self.size):
                        continue

                    overlap = 0
                    fits = True
                    for i in range(word_length):
                        r = row + dr * i
                        c = col + dc * i
                        cell = self.grid[r][c]
                        if cell == " " or cell == word[i]:
                            if cell == word[i]:
                                overlap += 1
                        else:
                            fits = False
                            break
                    if fits:
                        if overlap > max_overlap:
                            best_positions = [(row, col, dr, dc)]
                            max_overlap = overlap
                        elif overlap == max_overlap:
                            best_positions.append((row, col, dr, dc))

        if best_positions:
            # Randomly choose among best positions
            row, col, dr, dc = random.choice(best_positions)
            solution = {word: f"{row},{col},{dr},{dc}"}
            self.solution.append(solution)
            for i in range(word_length):
                r = row + dr * i
                c = col + dc * i
                self.grid[r][c] = word[i]
            return True
        else:
            return False

    def fill_empty_spaces(self, grid):
        # write a random letters in the empty positions
        for row in range(self.size):
            for col in range(self.size):
                if grid[row][col] == " ":
                    grid[row][col] = random.choice(string.ascii_uppercase)

        return

    def show_grid(self, show_failed_words=True):
        print(f"\nGrid:")
        print(f"\t{self.title} - {self.size}x{self.size}")
        for row in self.grid:
            print("\t" + " ".join(row))

        if show_failed_words and self.failed_words:
            print("\nFailed words:")
            for word in self.failed_words:
                print(f"\t{word}")

        return

    def show_solution(self):
        print("\nSolution:")
        highlights = self.get_highlights()
        for entry in highlights:
            word = entry["word"]
            start = entry["start"]
            direction = entry["direction"]
            length = entry["length"]
            arrow = direction_to_arrow(direction)
            print(f"\tWord: {word}, Start: {start}, Direction: {arrow}, Length: {length}")
        return

    def get_highlights(self):
        """Return solution highlights in the expected format for PDF rendering."""
        highlights = []
        for entry in self.solution:
            for word, pos_str in entry.items():
                highlights.append(parse_solution_entry(word, pos_str))
        return highlights


def generate_puzzle(title, words, size, basic, export_docx=False, verbose=False):
    try:
        wordsearch = WordSearch(title, words, size, basic)
    except ValueError as ve:
        logging.warning(f"Puzzle '{title}' skipped: {ve}")
    except Exception as e:
        logging.error(f"Unexpected error creating puzzle '{title}': {e}")

    if verbose:
        wordsearch.show_grid()
        wordsearch.show_solution()
        print()  # Add an empty line after the grid and solution

    return wordsearch


def direction_to_arrow(direction):
    arrows = {
        "horizontal_left_to_right": "\u2192",   # →
        "horizontal_right_to_left": "\u2190",   # ←
        "vertical_up_to_down": "\u2193",        # ↓
        "vertical_down_to_up": "\u2191",        # ↑
        "diagonal_up_left_to_down_right": "\u2198",  # ↘
        "diagonal_down_right_to_up_left": "\u2196",  # ↖
        "diagonal_up_right_to_down_left": "\u2199",  # ↙
        "diagonal_down_left_to_up_right": "\u2197",  # ↗
        "horizontal": "\u2192",
        "horizontal_rev": "\u2190",
        "vertical": "\u2193",
        "vertical_rev": "\u2191",
        "diagonal_down": "\u2198",
        "diagonal_up": "\u2197",
        "diagonal_down_rev": "\u2199",
        "diagonal_up_rev": "\u2196",
    }
    return arrows.get(direction, "?")


if __name__ == "__main__":

    title = "Fruits"
    words = [
        "Apple",
        "banana",
        "CHERRY",
        "strawberry",
        "grape",
        "yellow watermellon",
        "Jack Fruit",
    ]
    size = 12
    basic = True

    generate_puzzle(title, words, size, basic=False, verbose=True)
