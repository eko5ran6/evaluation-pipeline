"""Metric functions for SOAP summary evaluation."""

from rouge_score import rouge_scorer

_ROUGE = None


def _get_rouge_scorer():
    global _ROUGE
    if _ROUGE is None:
        _ROUGE = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    return _ROUGE


def entity_recall(nlp, ground_truth_text: str, generated_text: str) -> float:
    """
    Fraction of biomedical entities in the reference (scispaCy) that also appear
    in the generated summary (by exact lowercased entity string).
    """
    doc_gold = nlp(ground_truth_text)
    doc_gen = nlp(generated_text)

    gold_entities = {ent.text.lower() for ent in doc_gold.ents}
    gen_entities = {ent.text.lower() for ent in doc_gen.ents}

    if not gold_entities:
        return 0.0

    matches = gold_entities & gen_entities
    return len(matches) / len(gold_entities)


def rouge_l_f1(reference: str, candidate: str) -> float:
    """ROUGE-L F-measure between reference and candidate SOAP strings."""
    if not reference.strip() or not candidate.strip():
        return 0.0
    scorer = _get_rouge_scorer()
    return scorer.score(reference, candidate)["rougeL"].fmeasure
