import json
from pathlib import Path
from parsers.article_parser import ArticleParser

class ArticleCorpusBuilder:
    def __init__(self, parser: ArticleParser):
        self.parser = parser

    def build_for(self, doc):
        corpus = {}

        for article in self.parser.parse(doc.content_html):
            key = f"{doc.doc_id}_{article.dieu_id}"
            corpus[key] = f"{doc.header}\n{article.noi_dung}"

        return corpus

    def save(self, corpus: dict, output_path: str):
        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(corpus, f, ensure_ascii=False, indent=2)