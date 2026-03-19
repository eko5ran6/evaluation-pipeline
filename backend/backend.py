import spacy
import scispacy
from scispacy.abbreviation import AbbreviationDetector
from scispacy.linking import EntityLinker

# Load the medical model (locally, no API key needed!)
nlp = spacy.load("en_core_sci_sm")

def biomedical_eval(ground_truth, generated_summary):
    # Process both texts
    doc_gold = nlp(ground_truth)
    doc_gen = nlp(generated_summary)
    
    # 1. Extract Medical Entities (Drugs, Diseases, etc.)
    gold_entities = {ent.text.lower() for ent in doc_gold.ents}
    gen_entities = {ent.text.lower() for ent in doc_gen.ents}
    
    # 2. Calculate "Medical Recall" 
    # (How many of the true medical facts did the summary catch?)
    if not gold_entities: return 0
    
    matches = gold_entities.intersection(gen_entities)
    recall_score = len(matches) / len(gold_entities)
    
    return {
        "medical_recall": recall_score,
        "matched_entities": list(matches),
        "missed_entities": list(gold_entities - gen_entities)
    }

# Example usage
print(biomedical_eval("Patient prescribed Lisinopril for hypertension.", "Patient has high blood pressure."))