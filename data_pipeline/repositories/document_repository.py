import json
from pathlib import Path
from models.document import VbplDocument

class DocumentRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load(self, doc_id: str):
        path = self.data_dir / f"{doc_id}.json"

        if not path.exists():
            return None

        with open(path, encoding="utf-8") as f:
            return VbplDocument.from_detail(json.load(f))

    def iter_documents(self):
        for file in self.data_dir.glob("*.json"):
            with open(file, encoding="utf-8") as f:
                yield VbplDocument.from_detail(json.load(f))