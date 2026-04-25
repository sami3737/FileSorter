# File Organizer for Course Documents

This project is an automated file organizer designed specifically for organizing course-related documents. It monitors a source directory for new files, extracts text from them (supporting formats like PDF, DOCX, XLSX, ODT, images via OCR, etc.), uses AI (via Ollama and Llama 3.1 model) to classify the content into predefined categories, and automatically moves the files to corresponding destination folders.

## Features

- **Automatic Monitoring**: Uses `watchdog` to watch the source directory for new file creations.
- **Text Extraction**: Supports extraction from PDFs, Word documents, Excel files, ODT files, images (using Tesseract OCR), and more.
- **AI Classification**: Leverages Ollama's Llama 3.1 model to analyze file content and classify into categories such as CEJM, Anglais, Maths, Informatique, Culture Générale, Projet, Autre, or Non classé.
- **Modes**: Supports "auto" mode for automatic organization and "interactive" mode for user confirmation.
- **Learning**: Maintains a learning file (`learning.json`) to improve classifications over time.
- **Configurable**: Easily adjustable categories, paths, and parameters via `config.py`.

## Prerequisites

- Python 3.x
- Ollama installed and running locally (with `llama3.1` model pulled)
- Tesseract OCR installed (path configured in `config.py`)
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone or download the project to your local machine.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Install and start Ollama:
   - Download from [ollama.ai](https://ollama.ai)
   - Pull the model: `ollama pull llama3.1`
   - Ensure Ollama is running on `http://localhost:11434`
4. Install Tesseract OCR:
   - Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - Update the path in `src/config.py` if necessary.
5. Configure the paths in `src/config.py`:
   - Set `SOURCE` to your source directory (e.g., "C:/Users/samur/OneDrive/Documents/Cours/Dépot")
   - Set `DEST` to your destination directory (e.g., "C:/Users/samur/OneDrive/Documents/Cours/Tri")
   - Adjust other parameters as needed.

## Usage

### Running the Watcher

To start the automatic file watcher:
```
python src/watcher.py
```
The watcher will monitor the `SOURCE` directory and automatically organize new files as they are added.

### Manual Organization

You can also run the organization script manually:
```
python src/script.py
```
This will process all files in the `SOURCE` directory in interactive mode (if configured).

### Modes

- **Auto Mode**: Files are classified and moved automatically without user input.
- **Interactive Mode**: The script prompts for confirmation before moving files.

Change the `MODE` in `config.py` to switch between modes.

## Configuration

Edit `src/config.py` to customize:

- **Paths**: `SOURCE`, `DEST`, `LEARNING_FILE`
- **AI Settings**: `OLLAMA_URL`, `OLLAMA_PARAMS` (model, temperature, categories, etc.)
- **OCR**: `PYTESSERACT_CMD`
- **Limits**: `MAX_CHARS`, `MAX_WORDS_EXTRACT`
- **Categories**: `PRE_CLASSIFICATION_CATEGORIES` and detailed parameters in `OLLAMA_PARAMS`

## Supported File Types

- PDF (.pdf)
- Microsoft Word (.docx)
- Microsoft Excel (.xlsx)
- OpenDocument Text (.odt)
- Images (.png, .jpg, .jpeg, etc.) - via OCR
- Other text-based files

## How It Works

1. The `watcher.py` script uses `watchdog` to detect new files in the source directory.
2. Upon detection, it calls the `organize` function from `script.py`.
3. `script.py` extracts text from the file using appropriate libraries (e.g., `pdfplumber` for PDFs, `pytesseract` for images).
4. The extracted text is sent to Ollama for classification based on the configured categories.
5. The file is moved to the appropriate subfolder in the `DEST` directory.
6. Classifications are logged in `learning.json` for potential future improvements.

## Troubleshooting

- Ensure Ollama is running and the model is available.
- Check file permissions for reading/writing in source and destination directories.
- Verify Tesseract installation and path.
- For OCR issues, ensure images are clear and in supported formats.

## Contributing

Feel free to submit issues or pull requests for improvements.

## License

This project is open-source. Please check for any applicable licenses.