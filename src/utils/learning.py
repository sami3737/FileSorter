# Function to learn from history (matching filename/content with past entries)
import json
import os

from config import LEARNING_FILE
from script import extract_keywords


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

# Function to save learning in a JSON file
def save_learning(filename, category, content, subcategory=None, corrected=False):
    data = []

    if os.path.exists(LEARNING_FILE):
        with open(LEARNING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    entry = {
        "filename": filename,
        "category": category,
        "subcategory": subcategory,
        "keywords": extract_keywords(filename, content),
        "corrected": corrected
    }

    data.append(entry)

    with open(LEARNING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

