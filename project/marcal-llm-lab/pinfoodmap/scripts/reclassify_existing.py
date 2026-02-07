# reclassify_existing.py
"""Re-classify existing CSV data with the enhanced classifier."""

import pandas as pd
from src.enhanced_classifier import classify_content
from src.translator import translate_text
import sys

def reclassify_csv(input_csv="data/processed/processed_json.csv", output_csv="data/processed/processed_json_enhanced.csv"):
    """
    Re-classify all entries in the CSV with enhanced classifier.
    
    Args:
        input_csv: Input CSV file path
        output_csv: Output CSV file path for enhanced results
    """
    print(f"Loading data from {input_csv}...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"❌ Error: File {input_csv} not found.")
        return
    
    print(f"Total rows: {len(df)}")
    print(f"\nOriginal category distribution:")
    if 'Category' in df.columns:
        print(df['Category'].value_counts())
    else:
        print("No Category column found in original data.")
    
    print("\n" + "="*80)
    print("Re-classifying with enhanced classifier...")
    print("="*80 + "\n")
    
    # Add new columns for enhanced classification
    df['Enhanced_Category'] = ''
    df['Confidence'] = 0.0
    df['AI_Category'] = ''
    df['Classification_Reasoning'] = ''
    
    changes = {
        'Food_to_Other': [],
        'Other_to_Food': [],
        'Unchanged': 0
    }
    
    for idx, row in df.iterrows():
        # Get the translated content (or use original if not available)
        text = ""
        if 'Translated Content' in df.columns and pd.notna(row['Translated Content']):
            text = str(row['Translated Content'])
        elif 'Transcription' in df.columns and pd.notna(row['Transcription']):
            text = str(row['Transcription'])
        elif 'Description' in df.columns and pd.notna(row['Description']):
            text = str(row['Description'])
        
        if not text or text == 'nan':
            df.at[idx, 'Enhanced_Category'] = 'Other'
            df.at[idx, 'Classification_Reasoning'] = 'No content available'
            continue
        
        # Classify (use default threshold of 0.30)
        result = classify_content(text)
        
        df.at[idx, 'Enhanced_Category'] = result['category']
        df.at[idx, 'Confidence'] = result['confidence']
        df.at[idx, 'AI_Category'] = result.get('ai_category', '')
        df.at[idx, 'Classification_Reasoning'] = result['reasoning']
        
        # Track changes
        old_category = row.get('Category', 'Other')
        new_category = result['category']
        
        if old_category == 'Food' and new_category == 'Other':
            changes['Food_to_Other'].append(idx)
        elif old_category == 'Other' and new_category == 'Food':
            changes['Other_to_Food'].append(idx)
        else:
            changes['Unchanged'] += 1
        
        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx + 1}/{len(df)} rows...")
    
    print(f"\n✅ Classification complete!")
    print(f"\n{'='*80}")
    print("RESULTS SUMMARY")
    print(f"{'='*80}")
    print(f"\nEnhanced category distribution:")
    print(df['Enhanced_Category'].value_counts())
    
    print(f"\n\nChanges from original classification:")
    print(f"  Food → Other: {len(changes['Food_to_Other'])} (likely false positives removed)")
    print(f"  Other → Food: {len(changes['Other_to_Food'])} (potentially missed items)")
    print(f"  Unchanged: {changes['Unchanged']}")
    
    # Save results
    df.to_csv(output_csv, index=False)
    print(f"\n✅ Saved enhanced results to: {output_csv}")
    
    # Show sample of changed items
    if changes['Food_to_Other']:
        print(f"\n{'='*80}")
        print("SAMPLE: Items changed from Food to Other (first 5)")
        print(f"{'='*80}")
        for idx in changes['Food_to_Other'][:5]:
            row = df.loc[idx]
            print(f"\n{idx+1}. Link: {row.get('Link', 'N/A')}")
            content = row.get('Translated Content', row.get('Transcription', ''))[:200]
            print(f"   Content: {content}...")
            print(f"   Confidence: {row['Confidence']:.3f}")
            print(f"   AI Category: {row['AI_Category']}")
            print(f"   Reasoning: {row['Classification_Reasoning']}")
    
    if changes['Other_to_Food']:
        print(f"\n{'='*80}")
        print("SAMPLE: Items changed from Other to Food (first 5)")
        print(f"{'='*80}")
        for idx in changes['Other_to_Food'][:5]:
            row = df.loc[idx]
            print(f"\n{idx+1}. Link: {row.get('Link', 'N/A')}")
            content = row.get('Translated Content', row.get('Transcription', ''))[:200]
            print(f"   Content: {content}...")
            print(f"   Confidence: {row['Confidence']:.3f}")
            print(f"   AI Category: {row['AI_Category']}")
            print(f"   Reasoning: {row['Classification_Reasoning']}")
    
    return df, changes

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/processed/processed_json.csv"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "data/processed/processed_json_enhanced.csv"
    
    reclassify_csv(input_file, output_file)
