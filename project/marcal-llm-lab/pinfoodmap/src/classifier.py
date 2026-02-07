# src/classifier.py

from transformers import pipeline
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model once
print("Loading AI model...")
model_name = "facebook/bart-large-mnli"

try:
    # Load model (transformers usually checks cache first)
    logger.info("Loading model...")
    classifier = pipeline("zero-shot-classification", model=model_name)
    print("✅ Model loaded successfully.")
except Exception as e:
    logger.warning(f"Initial load failed: {e}")
    # Retry logic or just fail gracefully
    raise e

labels = ["food", "restaurant", "travel", "fashion", "sports", "pets"]

def is_food_related(text):
    """
    Check if a text is food/restaurant related using AI.
    """
    try:
        result = classifier(text, candidate_labels=labels)
        top_labels = result['labels'][:2]  # Top 2 labels
        return "food" in top_labels or "restaurant" in top_labels
    except Exception as e:
        logger.error(f"Error classifying text: {e}")
        return False
