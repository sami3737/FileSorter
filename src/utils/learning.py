# Function to learn from history (matching filename/content with past entries)
import json
import os

from ..config import LEARNING_FILE, MAX_WORDS_EXTRACT


def extract_keywords(filename, content):
    """Extract a stable list of keywords used by the local learning history."""
    text = (filename + " " + (content or "")).lower()
    words = text.replace("_", " ").replace("-", " ").split()
    keywords = [word for word in words if len(word) > 3]
    return list(dict.fromkeys(keywords))[:MAX_WORDS_EXTRACT]


def load_learning_data():
    if not os.path.exists(LEARNING_FILE):
        return []

    try:
        with open(LEARNING_FILE, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as error:
        print(f"Erreur de lecture de {LEARNING_FILE} : {error}")
        return []


def learn_from_history(filename, content):
    data = load_learning_data()

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

# Function to save learning in a JSON file
def save_learning(filename, category, content, subcategory=None, corrected=False):
    data = load_learning_data()

    entry = {
        "filename": filename,
        "category": category,
        "subcategory": subcategory,
        "keywords": extract_keywords(filename, content),
        "corrected": corrected
    }

    data.append(entry)

    os.makedirs(os.path.dirname(LEARNING_FILE), exist_ok=True)
    try:
        with open(LEARNING_FILE, "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, indent=4, ensure_ascii=False)
    except OSError as error:
        print(f"Erreur d'écriture de {LEARNING_FILE} : {error}")

