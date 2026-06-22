from __future__ import annotations

class CitationBuilder:
    def build(self, chunks: list[dict]) -> tuple[list[str], list[str]]:
        docs: dict[str, str] = {}
        articles: dict[tuple, str] = {}

        for chunk in chunks:
            metadata = chunk.get("metadata", {})

            so_hieu = metadata.get("so_hieu", "")
            document_title = metadata.get("document_title", "")
            article_number = metadata.get("article_number", "")

            # ============================================
            # Relevant docs
            # ============================================

            if so_hieu and so_hieu not in docs:
                docs[so_hieu] = f"{so_hieu}|{document_title}"

            # ============================================
            # Relevant articles
            # ============================================

            article_key = (so_hieu, article_number)
            if so_hieu and article_number and article_key not in articles:
                articles[article_key] = f"{so_hieu}|{document_title}|Điều {article_number}"

        return (
            list(docs.values()),
            list(articles.values()),
        )