import json
from pathlib import Path
from tqdm import tqdm
from app.rag.rag_pipeline import RAGPipeline
from app.core.logger import setup_logger

# =====================================================
# LOGGING
# =====================================================

logger = setup_logger(__name__)

# =====================================================
# PATHS
# =====================================================

BASE_DIR = Path(__file__).parent.parent.parent
INPUT_FILE = BASE_DIR / "law_datasets/competition_questions.json"
OUTPUT_FILE = BASE_DIR / "outputs/results.json"

# =====================================================
# MAIN
# =====================================================

def main():
    logger.info("Loading questions...")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    logger.info("Loaded %s questions", len(questions))

    pipeline = RAGPipeline()
    results = []

    for item in tqdm(questions, desc="Generating answers"):
        try:
            result = pipeline.ask(
                question_id=item["id"],
                question=item["question"]
            )
            results.append(result)
        except Exception:
            logger.exception("Failed question_id=%s", item["id"])
            results.append({
                "id": item["id"],
                "question": item["question"],
                "answer": "",
                "relevant_docs": [],
                "relevant_articles": []
            })

        # checkpoint mỗi 50 câu
        if len(results) % 50 == 0:
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info("Checkpoint saved (%s/%s)", len(results), len(questions))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info("Finished. Saved %s results", len(results))

if __name__ == "__main__":
    main()