import os
import shutil
import requests
import pdfplumber
from langdetect import detect
import json
from src.config import SOURCE, DEST, LEARNING_FILE, MODE, OLLAMA_URL, PYTESSERACT_CMD, MAX_CHARS, OLLAMA_PARAMS, PRE_CLASSIFICATION_CATEGORIES, MAX_WORDS_EXTRACT

# Function to extract text from various file types
import os

# DOCX
from docx import Document

# OCR image
import pytesseract
from PIL import Image

# Excel
from openpyxl import load_workbook
pytesseract.pytesseract.tesseract_cmd = PYTESSERACT_CMD

from odf.opendocument import load
from odf.text import P

# Function to recursively extract text from ODT elements
def extract_text(element):
    text = ""

    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            text += node.data
        else:
            text += extract_text(node)

    return text

# Function to read ODT files
def read_odt(path):
    try:
        doc = load(path)
        paragraphs = doc.getElementsByType(P)

        text = "\n".join(extract_text(p) for p in paragraphs)

        return text.strip()

    except Exception as e:
        print(f"Erreur lecture ODT {path}: {e}")
        return ""
        
# Function to read content from various file types
def read_file_content(path):
    ext = os.path.splitext(path)[1].lower()

    try:
        # -------------------------
        # PDF
        # -------------------------
        if ext == ".pdf":
            text = ""

            try:
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages[:2]:  # limite pour perf
                        text += page.extract_text() or ""
            except:
                text = ""

            # fallback OCR si vide
            if not text.strip() and ext == ".pdf":
                try:
                    from pdf2image import convert_from_path
                    images = convert_from_path(path, first_page=1, last_page=2)

                    for img in images:
                        text += pytesseract.image_to_string(img)
                except:
                    pass

            return text.strip()

        # -------------------------
        # DOCX
        # -------------------------
        elif ext == ".docx":
            try:
                doc = Document(path)
                return "\n".join(p.text for p in doc.paragraphs)
            except:
                return ""
        
        # -------------------------
        # ODT
        # -------------------------
        elif ext == ".odt":
            return read_odt(path)

        # -------------------------
        # TXT / MD
        # -------------------------
        elif ext in [".txt", ".md", ".csv"]:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except:
                return ""

        # -------------------------
        # Excel
        # -------------------------
        elif ext in [".xlsx", ".xls"]:
            try:
                wb = load_workbook(path)
                text = ""

                for sheet in wb:
                    for row in sheet.iter_rows(values_only=True):
                        text += " ".join([str(cell) for cell in row if cell]) + "\n"

                return text
            except:
                return ""

        # -------------------------
        # Images (OCR)
        # -------------------------
        elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            try:
                return pytesseract.image_to_string(Image.open(path))
            except:
                return ""

        # -------------------------
        # Fallback
        # -------------------------
        else:
            return ""

    except Exception as e:
        print(f"Erreur lecture fichier {path}: {e}")
        return ""
    
# Function to learn from history (matching filename/content with past entries)
def learn_from_history(filename, content):
    if not os.path.exists(LEARNING_FILE):
        return None

    with open(LEARNING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    text = (filename + " " + (content or "")).lower()

    best_match = None
    best_score = 0

    for item in data:
        keywords = item.get("keywords", [])

        score = sum(1 for k in keywords if k in text)

        if score > best_score:
            best_score = score
            best_match = item["category"]

    return best_match if best_score > 0 else None

# Function to confirm category with user (in interactive mode) and allow correction if needed
def confirm_category(file, category, mode="auto"):
    if mode == "interactive":
        user_input = input(f"{file} → {category} (Correcting ? y/n) : ")

        if user_input.lower() == "y":
            category = input("Nouvelle catégorie : ")

        return category, (user_input.lower() == "y")

    # MODE AUTO → aucune interaction
    return category, False

# Function to extract keywords from a file (for learning)
def extract_keywords(filename, content):
    text = (filename + " " + (content or "")).lower()
    words = text.replace("_", " ").replace("-", " ").split()

    # simple filter (you can improve this later with stop words, stemming, etc.)
    keywords = [w for w in words if len(w) > 3]

    return list(set(keywords[:MAX_WORDS_EXTRACT]))  # max 10 mots

# Function to save learning in a JSON file
def save_learning(filename, category, content, corrected=False):
    data = []

    if os.path.exists(LEARNING_FILE):
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    entry = {
        "filename": filename,
        "category": category,
        "keywords": extract_keywords(filename, content),
        "corrected": corrected
    }

    data.append(entry)

    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Function to pre-classify files based on simple rules (filename keywords)
def pre_classify(filename):
    name = filename.lower()

    if any(word in name for word in ["anglais", "lva", "english", "essay"]):
        return PRE_CLASSIFICATION_CATEGORIES[1]  # Anglais

    if "math" in name:
        return PRE_CLASSIFICATION_CATEGORIES[2]  # Maths

    if "cejm" in name:
        return PRE_CLASSIFICATION_CATEGORIES[0]  # CEJM
    
    if any(word in name for word in ["info", "programmation", "reseau", "base de données", "développement", "système d'exploitation", "sécurité informatique", "architecture informatique", "intelligence artificielle", "machine learning", "data science"]):
        return PRE_CLASSIFICATION_CATEGORIES[3]  # Informatique
    
    if any(word in name for word in ["culture", "générale", "français", "dissertation", "analyse de texte", "histoire", "géographie", "philosophie", "sciences sociales", "actualité"]):
        return PRE_CLASSIFICATION_CATEGORIES[4]  # Culture Générale
    
    if any(word in name for word in ["projet", "dossier", "mission", "rapport", "présentation"]):
        return PRE_CLASSIFICATION_CATEGORIES[5]  # Projet
    
    if any(word in name for word in ["autre", "divers", "misc", "various"]):
        return PRE_CLASSIFICATION_CATEGORIES[6]  # Autre

    return PRE_CLASSIFICATION_CATEGORIES[7]  # Non classé

# Function to ask the AI to classify a file based on its name and content
def ask_ai(filename, content):
    prompt = f"""
        Tu es un système de classification de fichiers pour un étudiant en BTS SIO.

        RÈGLE IMPORTANTE :
        - Tout document en ANGLAIS ou contenant des mots anglais (essay, agree, disagree, english)
        doit être classé en "Anglais", même s’il contient des éléments d’autres catégories.

        Catégories disponibles :"""
    
    for category, desc in OLLAMA_PARAMS["category_parameters"].items():
        prompt += "\n" + "\n".join([f"""

        - {category} : {desc}"""])
    
    prompt += "\n\n".join([f"""
        Exemples :
        - "TCP/IP cours.pdf" → Informatique
        - "BTS Anglais 2023.pdf" → Anglais
        - "fonction exponentielle.pdf" → Maths
        - "cas entreprise.docx" → CEJM

        RÈGLES STRICTES :
        - Réponds avec EXACTEMENT le nom d’une catégorie
        - Une seule réponse
        - Pas de phrase
        - Pas d’explication

        Nom du fichier : {filename}
        Contenu : {content[:MAX_CHARS]}

        Réponse :
        """])

    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_PARAMS["model"],
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_PARAMS["temperature"],
            "max_tokens": OLLAMA_PARAMS["max_tokens"]
        }
    })

    return response.json()["response"].strip().lower()

# Function to organize files
def organize(mode="interactive"):
    for file in os.listdir(SOURCE):
        path = os.path.join(SOURCE, file)

        if not os.path.isfile(path):
            continue

        content = read_file_content(path)
        content = content[:MAX_CHARS]

        # 1. memory
        category = learn_from_history(file, content)

        # 2. rules
        if not category:
            category = pre_classify(file)

        # 3. language (english priority)
        lang = detect(content)
        if lang == "en":
            category = "Anglais"

        # 4. IA
        if not category:
            category = ask_ai(file, content)

        # 5. user confirmation and correction
        category, corrected = confirm_category(file, category, mode=mode)

        # 6. move file
        target_dir = os.path.join(DEST, category)
        os.makedirs(target_dir, exist_ok=True)

        shutil.move(path, os.path.join(target_dir, file))

        # 7. learning
        save_learning(
            file,
            category,
            content,
            corrected=corrected
        )

        print(f"{file} → {category}")

# Main entry point
if __name__ == "__main__":
    organize(mode=MODE)