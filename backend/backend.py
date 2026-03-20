import json
import spacy
import scispacy
from pathlib import Path

# Load the medical model
nlp = spacy.load("en_core_sci_sm")

def flatten_jarvis(data):
    """Converts JarvisMD nested dictionary/lists into a single string for NLP."""
    text_parts = []
    for section in ['subjective', 'objective', 'assessment', 'plan']:
        content = data.get(section, "")
        if isinstance(content, dict):
            # If it's a dict (like subjective), join all its values
            for val in content.values():
                if isinstance(val, list): text_parts.extend(val)
                else: text_parts.append(str(val))
        elif isinstance(content, list):
            text_parts.extend(content)
        else:
            text_parts.append(str(content))
    return " ".join(text_parts)

def biomedical_eval(ground_truth, generated_summary):
    doc_gold = nlp(ground_truth)
    doc_gen = nlp(generated_summary)
    
    gold_entities = {ent.text.lower() for ent in doc_gold.ents}
    gen_entities = {ent.text.lower() for ent in doc_gen.ents}
    
    if not gold_entities: return 0
    
    matches = gold_entities.intersection(gen_entities)
    return len(matches) / len(gold_entities)

# --- DATA FETCHING & LOOPING ---

# 1. Load the files
base_path = Path(__file__).parent.parent / "datasets"
with open(base_path / "Groundtruth_Summary.json", "r") as f:
    gt_list = json.load(f)
with open(base_path / "JarvisMD_Summary.json", "r") as f:
    jarvis_list = json.load(f)

# 2. Create a lookup for JarvisMD by case_id
jarvis_lookup = {item['case_id']: item for item in jarvis_list}

# 3. Loop and Compare
print(f"{'Case ID':<10} | {'Medical Recall Score'}")
print("-" * 35)

for gt_item in gt_list:
    cid = gt_item['case_id']
    
    if cid in jarvis_lookup:
        # Prepare Groundtruth string (combining S, O, A, P fields)
        gt_text = f"{gt_item['subjective']} {gt_item['objective']} {gt_item['assessment']} {gt_item['plan']}"
        
        # Prepare JarvisMD string (flattening the nested structure)
        jarvis_text = flatten_jarvis(jarvis_lookup[cid])
        
        # Run Eval
        score = biomedical_eval(gt_text, jarvis_text)
        print(f"{cid:<10} | {score:.2%}")
    else:
        print(f"{cid:<10} | Match not found in JarvisMD file")