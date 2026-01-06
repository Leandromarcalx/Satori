# src/classifier.py

from transformers import pipeline

# Load model once
print("Loading AI model...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

labels = ["food", "restaurant", "travel", "fashion", "sports", "pets"]

def is_food_related(text):
    """
    Check if a text is food/restaurant related using AI.
    """
    result = classifier(text, candidate_labels=labels)
    top_labels = result['labels'][:2]  # Top 2 labels
    return "food" in top_labels or "restaurant" in top_labels
