import os

MODEL_NAME = "ProsusAI/finbert"


def check_cache_location():
    home = os.environ.get("HF_HOME", "")
    if not home.upper().startswith("D:"):
        raise RuntimeError(
            "HF_HOME is not set to a folder on D:. Run the setx step, restart "
            "VS Code, and check with: echo $env:HF_HOME"
        )
    return home


def probs_to_result(probs):
    label = max(probs, key=probs.get)
    return {
        "label": label,
        "p_positive": probs["positive"],
        "p_negative": probs["negative"],
        "p_neutral": probs["neutral"],
        "score": probs["positive"] - probs["negative"],
    }


def load_finbert():
    check_cache_location()
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def score_texts(texts, tokenizer, model, batch_size=16):
    import torch

    labels = [model.config.id2label[i].lower() for i in range(model.config.num_labels)]
    results = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        encoded = tokenizer(
            batch, padding=True, truncation=True, max_length=128, return_tensors="pt"
        )
        with torch.no_grad():
            logits = model(**encoded).logits
        for row in torch.softmax(logits, dim=1).tolist():
            results.append(probs_to_result(dict(zip(labels, row))))
    return results