# wordsearch-book-maker

A Python project for generating word search books.

## Features

- [x] Generate word search puzzle from list of words
- [x] Save puzzle to docx
- [x] Save puzzle to pdf
- [x] Improve formatting of main page
- [x] Fix solution page
- [ ] Improve formatting of solution page (rectangles)
- [ ] Evaluate best grid size and word number foir book
- [ ] Print collection in a book
- ...

## Installation

Clone the repository and install dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Usage

See scripts in the `scripts` folder as examples of usage.

**Important:**  
When running scripts directly, use the `-m` flag from the project root to ensure imports work correctly. For example:

```bash
python -m src.wordsearch.generate
```

```bash
python -m scripts.generate_wordsearch -h
```

To generate a wordsearch from a JSON file:

```bash
python -m scripts.generate_wordsearch input.json
```

## Project Structure

```text
data/               # Input reference files
src/wordsearch/     # Main package code
tests/              # Unit tests
docs/               # Documentation
scripts/            # Helper scripts
out/                # Output files (ignored by git)
```
