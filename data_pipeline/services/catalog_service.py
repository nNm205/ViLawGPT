import json
from collections import Counter

class CatalogService:
    def __init__(self, catalog_path):
        with open(catalog_path, encoding="utf-8") as f:
            self.documents = json.load(f)

        self.index = { d["id"]: d for d in self.documents }

    def get(self, doc_id):
        return self.index.get(doc_id)

    def search(self, keyword):
        keyword = keyword.lower()
        return [d for d in self.documents if keyword in d["ten_van_ban"].lower()]

    def stats(self):
        return {
            "n_docs": len(self.documents),
            "by_type": Counter(d["loai_van_ban"] for d in self.documents),
            "by_agency": Counter(d["co_quan_ban_hanh"] for d in self.documents)
        }