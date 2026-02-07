# src/enhanced_classifier.py

from transformers import pipeline
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model once
print("Loading enhanced AI model...")
model_name = "facebook/bart-large-mnli"

try:
    logger.info("Loading model...")
    classifier = pipeline("zero-shot-classification", model=model_name)
    print("✅ Enhanced model loaded successfully.")
except Exception as e:
    logger.warning(f"Initial load failed: {e}")
    raise e

# Enhanced labels for better categorization
LABELS = [
    "restaurant review and recommendation",
    "home cooking and recipes", 
    "food discussion and nutrition",
    "cultural lifestyle and relationships",
    "music and entertainment",
    "travel and tourism",
    "fashion and beauty",
    "sports and fitness",
    "health and supplements"
]

# Restaurant/food-specific keywords for contextual validation
RESTAURANT_KEYWORDS = [
    # Restaurant-specific terms
    r'\brestaurant[es]?\b', r'\bcaf[eé]\b', r'\bbar\b', r'\bbistro\b', 
    r'\bpizzaria\b', r'\blanchonete\b', r'\bpadaria\b',
    
    # Food establishment actions
    r'\breview\b', r'\brecomend[oa]?\b', r'\bmelhor[es]?\b', r'\bfavorit[oa]s?\b',
    r'\bdelicious\b', r'\bdelici[ao]s[oa]s?\b', r'\btried\b', r'\bexperiment[ei]\b',
    r'\bcomida boa\b', r'\bvale a pena\b', r'\bse destacou\b',
    
    # Menu/dish terms with location context
    r'\bmenu\b', r'\bprato\b', r'\bdish\b', r'\bserv[ie][dr]\b',
    r'\bramin\b', r'\bpizza\b', r'\bhamburg[ou]e?r\b', r'\bsushi\b', 
    r'\bespeto\b', r'\bcurry\b', r'\bbrunch\b',
    
    # Location + food combinations
    r'\bem\s+\w+.*?(restaurante|comida|lanche|pizza|ramen)',
    r'(restaurante|comida|lanche|pizza|ramen).*?\bem\s+\w+',
]

# Patterns that indicate NON-restaurant content
EXCLUSION_PATTERNS = [
    # Song lyrics patterns
    r'(ameno|dori me|lanzirei){2,}',
    r'[\u0C00-\u0C7F\u0F00-\u0FFF\u1000-\u109F]{10,}',  # Long sequences of non-latin scripts
    
    # Relationship/cultural advice patterns  
    r'\bsomae [eé] brasileira\b',
    r'\beli[çc][ãa]o \d+\b',
    r'\bse ela (for|est[aá])\b.*?\bentendeu\b',
    r'\btu n[ãa]o pode\b',
    
    # Pure supplement/nutrition discussion (without restaurant context)
    r'\bwhey.*?prote[ií]na.*?leite em p[óo]\b',
    r'\bsuplementa[çc][ãa]o\b.*?\batleta\b',
    
    # Generic non-food content
    r'\bt-wear\b.*?\bshorts\b.*?\bskirts\b',
    r'\bthank you for watching\b',
    r'\bwalt disney world\b',
]

def _contains_restaurant_keywords(text):
    """Check if text contains restaurant-specific keywords."""
    text_lower = text.lower()
    
    # Check for exclusion patterns first
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False, "Exclusion pattern matched"
    
    # Check for restaurant keywords
    matches = []
    for pattern in RESTAURANT_KEYWORDS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            matches.append(pattern)
    
    if matches:
        return True, f"Matched keywords: {len(matches)}"
    
    return False, "No restaurant keywords found"

def is_food_related(text, confidence_threshold=0.30, include_cooking=True, include_nutrition=False):
    """
    Enhanced classification for food/restaurant content.
    
    Args:
        text: Text to classify
        confidence_threshold: Minimum confidence score (0.0-1.0)
        include_cooking: Whether to include home cooking/recipes
        include_nutrition: Whether to include nutrition/supplement discussions
    
    Returns:
        bool: True if food/restaurant related
    """
    result = classify_content(text, confidence_threshold, include_cooking, include_nutrition)
    return result["is_food_related"]

def classify_content(text, confidence_threshold=0.30, include_cooking=True, include_nutrition=False):
    """
    Perform multi-layered classification with detailed results.
    
    Args:
        text: Text to classify
        confidence_threshold: Minimum confidence score (0.0-1.0)
        include_cooking: Whether to include home cooking/recipes
        include_nutrition: Whether to include nutrition/supplement discussions
    
    Returns:
        dict: {
            "is_food_related": bool,
            "category": str,
            "confidence": float,
            "secondary_category": str,
            "secondary_confidence": float,
            "reasoning": str
        }
    """
    try:
        # Check for exclusion patterns first
        text_lower = text.lower()
        for pattern in EXCLUSION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return {
                    "is_food_related": False,
                    "category": "Other",
                    "confidence": 1.0,
                    "secondary_category": "Excluded by pattern",
                    "secondary_confidence": 0.0,
                    "reasoning": f"Matched exclusion pattern: {pattern[:50]}"
                }
        
        # Layer 1: AI Classification
        result = classifier(text[:1000], candidate_labels=LABELS)  # Limit text length
        
        top_category = result['labels'][0]
        top_confidence = result['scores'][0]
        secondary_category = result['labels'][1] if len(result['labels']) > 1 else ""
        secondary_confidence = result['scores'][1] if len(result['scores']) > 1 else 0.0
        
        # Layer 2: Confidence Thresholding
        if top_confidence < confidence_threshold:
            return {
                "is_food_related": False,
                "category": "Other",
                "confidence": top_confidence,
                "secondary_category": secondary_category,
                "secondary_confidence": secondary_confidence,
                "reasoning": f"Low confidence ({top_confidence:.2f} < {confidence_threshold})"
            }
        
        # Layer 3: Contextual Validation
        has_keywords, keyword_reason = _contains_restaurant_keywords(text)
        
        # Determine if food-related based on category
        food_categories = ["restaurant review and recommendation"]
        
        if include_cooking:
            food_categories.append("home cooking and recipes")
        
        if include_nutrition:
            food_categories.append("food discussion and nutrition")
        
        is_food = top_category in food_categories
        
        # Special handling: If classified as "food discussion" but has restaurant keywords,
        # it's likely a restaurant review that was misclassified
        if top_category == "food discussion and nutrition" and has_keywords and not include_nutrition:
            # Override: This is likely a restaurant review
            is_food = True
            reasoning_parts = [
                f"Category: {top_category} ({top_confidence:.2f})",
                "Override: Has restaurant keywords",
                keyword_reason
            ]
            reasoning = "; ".join(reasoning_parts)
            
            return {
                "is_food_related": True,
                "category": "Food",
                "confidence": top_confidence,
                "secondary_category": secondary_category,
                "secondary_confidence": secondary_confidence,
                "reasoning": reasoning,
                "ai_category": "restaurant review and recommendation (override)"
            }
        
        # Special case: If classified as restaurant but no keywords, lower confidence
        if top_category == "restaurant review and recommendation" and not has_keywords:
            reasoning = f"Classified as '{top_category}' but {keyword_reason}"
            # If confidence is borderline and no keywords, reject it
            if top_confidence < 0.6:
                return {
                    "is_food_related": False,
                    "category": "Other",
                    "confidence": top_confidence,
                    "secondary_category": secondary_category,
                    "secondary_confidence": secondary_confidence,
                    "reasoning": reasoning
                }
        
        # Build reasoning
        reasoning_parts = [f"Category: {top_category} ({top_confidence:.2f})"]
        if has_keywords:
            reasoning_parts.append(keyword_reason)
        
        reasoning = "; ".join(reasoning_parts)
        
        return {
            "is_food_related": is_food,
            "category": "Food" if is_food else "Other",
            "confidence": top_confidence,
            "secondary_category": secondary_category,
            "secondary_confidence": secondary_confidence,
            "reasoning": reasoning,
            "ai_category": top_category
        }
        
    except Exception as e:
        logger.error(f"Error classifying text: {e}")
        return {
            "is_food_related": False,
            "category": "Other",
            "confidence": 0.0,
            "secondary_category": "",
            "secondary_confidence": 0.0,
            "reasoning": f"Error: {str(e)}"
        }
