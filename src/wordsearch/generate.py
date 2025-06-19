import logging
import random
import string

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


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
            (0, 1),  # horizontal
            (1, 0),  # vertical
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
        for solution in self.solution:
            print(f"\t{solution}")
        return


def generate_puzzle(title, words, size, basic, verbose=False):
    wordsearch = WordSearch(title, words, size, basic)
    try:
        wordsearch = WordSearch(title, words, size, basic)
    except ValueError as ve:
        logging.warning(f"Puzzle '{title}' skipped: {ve}")
    except Exception as e:
        logging.error(f"Unexpected error creating puzzle '{title}': {e}")

    if verbose:
        wordsearch.show_grid()

        wordsearch.show_solution()

    return wordsearch


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

    generate_puzzle(title, words, size, basic, verbose=True)
