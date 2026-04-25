import os
import shutil
from config import SOURCE, DEST, MODE, OLLAMA_URL, MAX_CHARS, OLLAMA_PARAMS, PRE_CLASSIFICATION_CATEGORIES, MAX_WORDS_EXTRACT, SUBCATEGORIES
from langdetect import detect
import requests
from utils import file_reader
from utils import learning
   
# Function to confirm category with user (in interactive mode) and allow correction if needed
def confirm_category(file, category, subcategory=None, mode="auto"):
    if mode == "interactive":
        subcat_str = f" / {subcategory}" if subcategory else ""
        user_input = input(f"{file} → {category}{subcat_str} (Correcting ? y/n) : ")

        if user_input.lower() == "y":
            category = input("New category : ")
            subcategory = None  # Reset subcategory when category changes

        return category, subcategory, (user_input.lower() == "y")

    # MODE AUTO → aucune interaction
    return category, subcategory, False

# Function to extract keywords from a file (for learning)
def extract_keywords(filename, content):
    text = (filename + " " + (content or "")).lower()
    words = text.replace("_", " ").replace("-", " ").split()

    # simple filter (you can improve this later with stop words, stemming, etc.)
    keywords = [w for w in words if len(w) > 3]

    return list(set(keywords[:MAX_WORDS_EXTRACT]))  # max 10 mots

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

# Function to detect subcategory based on filename and content
def detect_subcategory(filename, content, main_category):
    if main_category not in SUBCATEGORIES:
        return None
    
    text = (filename + " " + (content or "")).lower()
    
    subcategory_patterns = {
        "Informatique": {
            "U3": ["u3", "programmation", "initiation", "algorithm", "python", "javascript", "html", "css", "variable", "boucle", "fonction"],
            "U5": ["u5", "base de données", "sql", "mysql", "mariadb", "requête", "table", "modèle", "merise"],
            "U7": ["u7", "cybersécurité", "sécurité", "firewall", "vpn", "chiffrement", "authentification", "ssl", "tls"]
        },
        "CEJM": {
            "1ère année": ["1ère", "1ere", "première", "annee 1", "année 1"],
            "2è année": ["2è", "2e", "deuxième", "annee 2", "année 2"]
        },
        "Culture Générale": {
            "Restitution": ["restitution", "synthèse", "résumé"],
            "Support de cours": ["cours", "support", "td", "tp", "exercice"]
        },
        "Projet": {
            "Projets BTS": ["projet", "bts", "dossier", "mission"]
        }
    }
    
    if main_category in subcategory_patterns:
        for subcat, keywords in subcategory_patterns[main_category].items():
            if any(keyword in text for keyword in keywords):
                return subcat
    
    return None

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

        content = file_reader.read_file_content(path)
        content = content[:MAX_CHARS]

        # 1. memory
        category = learning.learn_from_history(file, content)

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

        # 5. detect subcategory
        subcategory = detect_subcategory(file, content, category)
        
        # 6. user confirmation and correction
        category, subcategory, corrected = confirm_category(file, category, subcategory, mode=mode)
        
        # 6.5. re-detect subcategory if category was corrected
        if corrected and category:
            subcategory = detect_subcategory(file, content, category)
        
        # 7. move file
        if subcategory:
            target_dir = os.path.join(DEST, category, subcategory)
        else:
            target_dir = os.path.join(DEST, category)
        os.makedirs(target_dir, exist_ok=True)

        shutil.move(path, os.path.join(target_dir, file))

        # 8. learning
        learning.save_learning(
            file,
            category,
            content,
            subcategory,
            corrected=corrected
        )

        print(f"{file} → {category}" + (f" / {subcategory}" if subcategory else ""))

# Main entry point
if __name__ == "__main__":
    organize(mode=MODE)