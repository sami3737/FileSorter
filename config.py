SOURCE = "C:/Users/samur/OneDrive/Documents/Cours/Dépot"
DEST = "C:/Users/samur/OneDrive/Documents/Cours/Tri"
LEARNING_FILE = "learning.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODE = "interactive"  # ou "interactive"
PYTESSERACT_CMD = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
MAX_CHARS = 1500,
PRE_CLASSIFICATION_CATEGORIES = ["CEJM", "Anglais", "Maths", "Informatique", "Culture Générale", "Projet", "Autre", "Non classé"]
OLLAMA_PARAMS = {
    "temperature": 0.7,
    "model": "llama3.1",
    "max_tokens": 1500,
    "category": ["CEJM", "Anglais", "Maths", "Informatique", "Culture Générale", "Projet", "Autre", "Non classé"],
    "category_parameters": {
        "CEJM": "droit, économie, management, entreprise, gestion, marketing, communication, ressources humaines, finance, comptabilité, économie d'entreprise",
        "Anglais": "langue anglaise, LVA, TOEIC, exercices anglais, vocabulaire anglais, grammaire anglaise, compréhension écrite anglaise, expression écrite anglaise",
        "Maths": "calculs, fonctions, statistiques, algorithmes mathématiques, géométrie, trigonométrie",
        "Informatique": "programmation, réseau, base de données, développement, systèmes d'exploitation, sécurité informatique, architecture informatique, intelligence artificielle, machine learning, data science",
        "Culture Générale": "français, dissertation, analyse de texte, histoire, géographie, philosophie, sciences sociales, actualités, culture générale",
        "Projet": "projets scolaires, dossiers de projet, missions en entreprise, mission en école, rapport de stage, présentation de projet",
        "Autre": "fichier qui ne correspond à aucune catégorie, ou qui contient des éléments de plusieurs catégories, ou dont le contenu est trop vague pour être classé",
        "Non classé": "si tu n'es vraiment pas sûr, ou si le fichier est vide, ou si tu ne peux pas extraire de contenu, ou si le nom du fichier ne donne aucun indice, ou si le fichier est dans un format que tu ne peux pas lire"
    }
}