from transformers import pipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load NER model
# using a multilingual model that works well with Portuguese
# alternative: "Babelscape/wikineural-multilingual-ner"
model_name = "Babelscape/wikineural-multilingual-ner" 

print(f"Loading NER model ({model_name})...")
try:
    # Use aggregation_strategy="simple" instead of grouped_entities (deprecated)
    ner_pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple")
    print("✅ NER Model loaded successfully.")
except Exception as e:
    logger.warning(f"Could not load specific NER model: {e}")
    print("Falling back to default NER model...")
    ner_pipeline = pipeline("ner", aggregation_strategy="simple")

def extract_entities(text):
    """
    Extracts Locations (LOC) and Organizations (ORG - potentially restaurants) from text.
    Returns a dictionary with lists of found entities.
    """
    try:
        results = ner_pipeline(text)
        
        locations = []
        organizations = []
        
        for entity in results:
            if entity['entity_group'] == 'LOC':
                locations.append(entity['word'])
            elif entity['entity_group'] == 'ORG':
                organizations.append(entity['word'])
            elif entity['entity_group'] == 'PER':
                pass # Ignore persons for this use case
                
        # Deduplicate
        locations = list(set(locations))
        organizations = list(set(organizations))
        
        return {
            "locations": locations,
            "organizations": organizations
        }
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return {"locations": [], "organizations": []}
