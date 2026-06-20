from __future__ import annotations

class CitationBuilder:
    def build(self, chunks: list[dict]) -> tuple[list[str], list[str]]:
        docs = set()
        articles = set()

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            so_hieu = metadata.get("so_hieu", "")
            document_title = metadata.get("document_title", "")
            article_number = metadata.get("article_number", "")

            if so_hieu and document_title:
                docs.add(f"{so_hieu}|{document_title}")

            if so_hieu and document_title and article_number:
                articles.add(f"{so_hieu}|{document_title}|Điều {article_number}")

        return (sorted(docs), sorted(articles))