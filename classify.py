import os
import json
import logging
from transformers import pipeline
from tqdm import tqdm  # Import tqdm for progress bars

# Set up logging to a file named 'classify.log'
logging.basicConfig(
    filename='classify.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Path to the JSON file containing scraped articles
JSON_FILE = "articles.json"

# Define candidate subcategories for real estate articles.
CANDIDATE_LABELS = [
    "Residential Real Estate",
    "Commercial Real Estate",
    "Real Estate Market Trends",
    "Real Estate Finance",
    "Real Estate Legal",
    "Real Estate Technology",
    "Real Estate Investment"
]

def load_articles(json_file):
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            articles = json.load(f)
        logging.info("Loaded %d articles from %s.", len(articles), json_file)
        return articles
    else:
        logging.info("No articles file found at %s. Exiting.", json_file)
        return []

def classify_articles(articles, classifier):
    num_classified = 0
    # Wrap the articles loop with tqdm for a progress bar
    for article in tqdm(articles, desc="Classifying articles"):
        # If an article already has classifications, skip it.
        if "classifications" in article:
            logging.info("Article already classified: %s", article.get("url", "No URL"))
            continue

        text = article.get("content", "")
        if not text:
            article["classifications"] = {}
            logging.info("No content found for article: %s", article.get("url", "No URL"))
            continue

        logging.info("Classifying article: %s", article.get("url", "No URL"))
        result = classifier(text, candidate_labels=CANDIDATE_LABELS, multi_label=True)
        classifications = {label: score for label, score in zip(result["labels"], result["scores"])}
        article["classifications"] = classifications
        logging.info("Assigned classifications: %s", classifications)
        num_classified += 1

    logging.info("Classified %d new articles.", num_classified)
    return articles

def save_articles(articles, json_file):
    with open(json_file, "w") as f:
        json.dump(articles, f, indent=4)
    logging.info("Saved updated articles to %s.", json_file)

def main():
    logging.info("Starting classification process.")
    articles = load_articles(JSON_FILE)
    if not articles:
        logging.error("No articles loaded. Exiting classification process.")
        return

    logging.info("Loading Hugging Face zero-shot classification pipeline.")
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", multi_label=True)

    articles = classify_articles(articles, classifier)
    save_articles(articles, JSON_FILE)
    logging.info("Classification process completed.")

if __name__ == "__main__":
    main()
