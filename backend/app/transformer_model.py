from functools import lru_cache


@lru_cache(maxsize=1)
def get_zero_shot_pipeline():
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("transformers not available or failed to import: " + str(e))
    # uses a general NLI model for zero-shot classification
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def predict_zero_shot(text: str, labels=("fake", "real")):
    pipe = get_zero_shot_pipeline()
    out = pipe(text, candidate_labels=list(labels), multi_label=False)
    # out keys: labels (ordered), scores
    label = out['labels'][0]
    score = out['scores'][0]
    return label, float(score), out
