import time

from src.analysis.sentiment import MODEL_NAME, check_cache_location, load_finbert, score_texts

SAMPLES = [
    "Reliance Industries Q2 profit jumps 41% on strong O2C and Jio growth",
    "SEBI bars promoters from the market over alleged fraud",
    "Board meeting scheduled for November 5 to consider quarterly results",
    "Infosys cuts annual revenue guidance as demand weakens",
    "Bank shares rally as RBI holds rates steady",
    "Company shares plunge 12% after auditor resigns",
]

print("Model cache folder:", check_cache_location())

try:
    from huggingface_hub import HfApi

    info = HfApi().model_info(MODEL_NAME)
    card = getattr(info, "card_data", None)
    print("Licence on the model card:", getattr(card, "license", None) or "not stated")
except Exception as err:
    print("Could not read the model card:", err)

started = time.time()
tokenizer, model = load_finbert()
print(f"Model loaded in {time.time() - started:.1f} s")

results = score_texts(SAMPLES, tokenizer, model)
for text, r in zip(SAMPLES, results):
    print(f"{r['label']:<9} {r['score']:+.2f}  {text}")