# File Organizer for Course Documents

This project is an automated file organizer designed specifically for organizing course-related documents. It monitors a source directory for new files, extracts text from them (supporting formats like PDF, DOCX, XLSX, ODT, images via OCR, etc.), uses AI (via Ollama and Llama 3.1 model) to classify the content into predefined categories and subcategories, and automatically moves the files to corresponding destination folders.

## Features

- **Automatic Monitoring**: Uses `watchdog` to watch the source directory for new file creations.
- **Text Extraction**: Supports extraction from PDFs, Word documents, Excel files, ODT files, images (using Tesseract OCR), and more.
- **AI Classification**: Leverages Ollama's Llama 3.1 model to analyze file content and classify into categories such as CEJM, Anglais, Maths, Informatique, Culture Générale, Projet, Autre, or Non classé.
- **Subcategory System**: Automatically detects subcategories based on file content and name (e.g., `Informatique/U5`, `CEJM/1ère année`).
- **Modes**: Supports "auto" mode for automatic organization and "interactive" mode for user confirmation and correction.
- **Learning**: Maintains a learning file (`learning.json`) to improve classifications over time based on past corrections.
- **Configurable**: Easily adjustable categories, subcategories, paths, and parameters via `config.py`.

## Prerequisites

- Python 3.10 or later
- Ollama installed and running locally (with `llama3.1` model pulled)
- Tesseract OCR installed (path configured in `config.py`)
- Poppler installed and available in `PATH` for OCR fallback on scanned PDFs
- Required Python packages (see `requirements.txt`)

## Windows Installation with a Virtual Environment

1. Clone or download the project, then open PowerShell in the project root.
2. Create the virtual environment:

   ```powershell
   python -m venv .venv
   ```

3. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, you can use the virtual environment without changing the execution policy:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   In that case, prefix the launch commands with `.\.venv\Scripts\python.exe` as well.

4. Install the Python dependencies after activation:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. Install and start Ollama:
   - Download from [ollama.ai](https://ollama.ai)
   - Pull the model: `ollama pull llama3.1`
   - Ensure Ollama is running on `http://localhost:11434`
6. Install Tesseract OCR:
   - Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - Update the path in `config.py` if necessary.
7. Install Poppler for scanned PDF OCR:
   - Download a Windows build of Poppler.
   - Add its `Library/bin` or `bin` directory to `PATH`.
   - Verify the installation with `pdftoppm -h`.
8. Configure the paths in `src/config.py` if necessary:
   - `SOURCE` defaults to `data/Dépot`.
   - `DEST` defaults to `data/Tri`.
   - `LEARNING_FILE` defaults to `data/learning.json`.
   - Adjust other parameters as needed.

To leave the virtual environment, run:

```powershell
deactivate
```

## Usage

### Running the Watcher

To start the automatic file watcher:

```
python -m src.watcher
```

The watcher will monitor the `SOURCE` directory and automatically organize new files as they are added.

### Manual Organization

You can also run the organization script manually:

```
python -m src.script
```

This will process all files in the `SOURCE` directory according to the configured mode.

### Modes

- **Auto Mode**: Files are classified and moved automatically without user input.
- **Interactive Mode**: The script prompts for confirmation before moving each file.

Change the `MODE` in `config.py` to switch between modes (`"auto"` or `"interactive"`).

## Interactive Mode — Confirming and Correcting Classifications

In interactive mode, the script will display the detected category (and subcategory if applicable) and ask for confirmation:

```
Authentification et contrôle d'accès.pdf → Informatique / U7 (Corriger ? o/N) :
```

- Type `n` or press Enter to accept the suggestion and move the file.
- Type `o` to correct the classification. The script also accepts `oui`, `y`, and `yes`.

```
Nouvelle catégorie (catégorie ou catégorie/sous-catégorie) : Informatique/U5
```

### Category and Subcategory Input Format

When correcting a classification, enter the category name exactly as defined in `config.py`. To specify a subcategory, use a `/` separator:

```
Informatique/U5
Informatique/U7
CEJM/1ère année
Culture Générale/Restitution
Projet/Projets BTS
```

If you only enter a main category without a subcategory (e.g., `Anglais`), the script will attempt to detect a subcategory automatically based on the file content. If none is found, the file is placed directly in the main category folder.

## Categories and Subcategories

The following categories and subcategories are available:

| Category           | Subcategories                 |
| ------------------ | ----------------------------- |
| Informatique       | U3, U5, U7                    |
| CEJM               | 1ère année, 2è année          |
| Culture Générale   | Restitution, Support de cours |
| Projet             | Projets BTS                   |
| Anglais            | *(none)*                    |
| Maths              | *(none)*                    |
| Autre              | *(none)*                    |
| Non classé        | *(none)*                    |

Categories and subcategories can be added or modified in `config.py` under `SUBCATEGORIES` and `PRE_CLASSIFICATION_CATEGORIES`.

## Destination Folder Structure

Files are organized in the `DEST` directory as follows:

```
Tri/
├── Anglais/
│   └── Business Phone Calls Students 01.pdf
├── Informatique/
│   ├── U3/
│   │   └── intro-python.pdf
│   ├── U5/
│   │   └── Travailler-en-Mode-Projet.pdf
│   └── U7/
│       └── Authentification et contrôle d'accès.pdf
├── CEJM/
│   ├── 1ère année/
│   │   └── cours-droit-entreprise.pdf
│   └── 2è année/
│       └── marketing-mix.pdf
├── Culture Générale/
│   ├── Restitution/
│   │   └── synthese-philo.docx
│   └── Support de cours/
│       └── td-francais.pdf
└── Projet/
    └── Projets BTS/
        └── dossier-mission.pdf
```

## Configuration

Edit `config.py` to customize:

- **Paths**: `SOURCE`, `DEST`, `LEARNING_FILE` (project-relative by default)
- **AI Settings**: `OLLAMA_URL`, `OLLAMA_PARAMS` (model, temperature, categories, etc.)
- **OCR**: `PYTESSERACT_CMD`
- **Limits**: `MAX_CHARS`, `MAX_WORDS_EXTRACT`, `PDF_PAGE_LIMIT`
- **Categories**: `PRE_CLASSIFICATION_CATEGORIES` and detailed descriptions in `OLLAMA_PARAMS["category_parameters"]`
- **Subcategories**: `SUBCATEGORIES` — a dictionary mapping each main category to its list of subcategories

## Supported File Types

FileSorter currently supports 11 extensions:

- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- Microsoft Excel (`.xlsx`)
- OpenDocument Text (`.odt`)
- Plain text / Markdown / CSV (`.txt`, `.md`, `.csv`)
- Images (`.png`, `.jpg`, `.jpeg`, `.bmp`) — via Tesseract OCR

## How It Works

1. `watcher.py` uses `watchdog` to detect new files in the source directory.
2. Upon detection, it calls the `organize` function from `script.py`.
3. `script.py` extracts text from the file using the appropriate library (e.g., `pdfplumber` for PDFs, `pytesseract` for images).
4. Classification is attempted in the following order:
   1. **Learning history** — checks `learning.json` for similar past files.
   2. **Pre-classification rules** — applies simple keyword matching on the filename.
   3. **Language detection** — files detected as English are classified as `Anglais`.
   4. **AI classification** — sends filename and content to Ollama if no category was found.
5. A **subcategory** is detected automatically based on keywords found in the filename and content.
6. In interactive mode, the user can confirm or correct the result.
7. The file is moved to `DEST/<category>/` or `DEST/<category>/<subcategory>/`.
8. The result is saved to `learning.json` to improve future classifications.

## Troubleshooting

- Ensure Ollama is running and the model is available (`ollama list`).
- Check file permissions for reading/writing in source and destination directories.
- Verify Tesseract installation and that `PYTESSERACT_CMD` points to the correct executable.
- For OCR issues, ensure images are clear and in supported formats.
- If subcategory detection is incorrect, correct it in interactive mode — the correction is saved to `learning.json` and will be used for future similar files.
- Run commands from the project root with `python -m src.script` or `python -m src.watcher`.
- Do not run the manual script and the watcher at the same time.
- If scanned PDF OCR fails on Windows, check that `pdftoppm -h` works and that Poppler is present in `PATH`.

## Contributing

Feel free to submit issues or pull requests for improvements.

## License

No license has been selected yet. Add a `LICENSE` file before presenting the repository as freely reusable open-source software.
