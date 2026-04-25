import os
import shutil
import requests
import pdfplumber
from langdetect import detect
import json
from config import SOURCE, DEST, LEARNING_FILE, MODE, OLLAMA_URL, PYTESSERACT_CMD, MAX_CHARS

# Fonction pour lire le contenu d’un fichier (PDF pour l’instant)
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

def extract_text(element):
    text = ""

    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE:
            text += node.data
        else:
            text += extract_text(node)

    return text


def read_odt(path):
    try:
        doc = load(path)
        paragraphs = doc.getElementsByType(P)

        text = "\n".join(extract_text(p) for p in paragraphs)

        return text.strip()

    except Exception as e:
        print(f"Erreur lecture ODT {path}: {e}")
        return ""
        
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
    
# Fonction pour apprendre de l’historique des classifications
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

# Fonction pour confirmer ou corriger la catégorie proposée à l’utilisateur
def confirm_category(file, category, mode="auto"):
    if mode == "interactive":
        user_input = input(f"{file} → {category} (corriger ? y/n) : ")

        if user_input.lower() == "y":
            category = input("Nouvelle catégorie : ")

        return category, (user_input.lower() == "y")

    # MODE AUTO → aucune interaction
    return category, False

# Fonction pour extraire des mots-clés d’un fichier (pour l’apprentissage)
def extract_keywords(filename, content):
    text = (filename + " " + (content or "")).lower()
    words = text.replace("_", " ").replace("-", " ").split()

    # filtre simple (tu pourras améliorer après)
    keywords = [w for w in words if len(w) > 3]

    return list(set(keywords[:10]))  # max 10 mots

# Fonction pour sauvegarder l’apprentissage dans un fichier JSON
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

# Fonction de pré-classification basée sur des règles simples
def pre_classify(filename):
    name = filename.lower()

    if any(word in name for word in ["anglais", "lva", "english", "essay"]):
        return "Anglais"

    if "math" in name:
        return "Maths"

    if "cejm" in name:
        return "CEJM"

    return None
    
# Fonction pour demander à l’IA de classer un fichier en fonction de son nom et de son contenu
def ask_ai(filename, content):
    prompt = f"""
        Tu es un système de classification de fichiers pour un étudiant en BTS SIO.

        RÈGLE IMPORTANTE :
        - Tout document en ANGLAIS ou contenant des mots anglais (essay, agree, disagree, english)
        doit être classé en "Anglais", même s’il contient des éléments d’autres catégories.

        Catégories disponibles :

        - CEJM : droit, économie, management, entreprise, gestion, marketing, communication, ressources humaines, finance, comptabilité, économie d'entreprise
        - Anglais : langue anglaise, LVA, TOEIC, exercices anglais, vocabulaire anglais, grammaire anglaise, compréhension écrite anglaise, expression écrite anglaise
        - Maths : calculs, fonctions, statistiques, algorithmes mathématiques, géométrie, trigonométrie
        - Informatique : programmation, réseau, base de données, développement, systèmes d'exploitation, sécurité informatique, architecture informatique, intelligence artificielle, machine learning, data science
        - Culture Générale : français, dissertation, analyse de texte, histoire, géographie, philosophie, sciences sociales, actualités, culture générale
        - Projet : projets scolaires, dossiers de projet, missions en entreprise, mission en école, rapport de stage, présentation de projet
        - Autre : fichier qui ne correspond à aucune catégorie, ou qui contient des éléments de plusieurs catégories, ou dont le contenu est trop vague pour être classé
        - Non classé : si tu n'es vraiment pas sûr, ou si le fichier est vide, ou si tu ne peux pas extraire de contenu, ou si le nom du fichier ne donne aucun indice, ou si le fichier est dans un format que tu ne peux pas lire

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
        Contenu : {content[:800]}

        Réponse :
        """

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    })

    return response.json()["response"].strip().lower()

# Fonction principale pour organiser les fichiers
def organize(mode="interactive"):
    for file in os.listdir(SOURCE):
        path = os.path.join(SOURCE, file)

        if not os.path.isfile(path):
            continue

        content = read_file_content(path)
        content = content[:MAX_CHARS]

        # 1. mémoire
        category = learn_from_history(file, content)

        # 2. règles simples
        if not category:
            category = pre_classify(file)

        # 3. langue (anglais prioritaire)
        lang = detect(content)
        if lang == "en":
            category = "Anglais"

        # 4. IA
        if not category:
            category = ask_ai(file, content)

        # 5. correction utilisateur
        category, corrected = confirm_category(file, category, mode=mode)

        # 6. déplacement
        target_dir = os.path.join(DEST, category)
        os.makedirs(target_dir, exist_ok=True)

        shutil.move(path, os.path.join(target_dir, file))

        # 7. apprentissage
        save_learning(
            file,
            category,
            content,
            corrected=corrected
        )

        print(f"{file} → {category}")

# Lancement de l’organisation
if __name__ == "__main__":
    organize(mode=MODE)