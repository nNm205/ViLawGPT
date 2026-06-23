import json
from pathlib import Path 

BASE_DIR = Path(__file__).parent.parent
RESULTS_PATH = BASE_DIR / "outputs/results.json"

with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    results = json.load(f)

missing_question_ids = []
for result in results:
    if len(result["relevant_docs"]) == 0:
        missing_question_ids.append(result["id"])

print(missing_question_ids)
