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
            clause_number = metadata.get("clause_number", 0)

            # -------------------------------------------------
            # Relevant docs: deduplicate theo so_hieu
            # -------------------------------------------------
            if so_hieu and so_hieu not in docs:
                docs[so_hieu] = f"{so_hieu}|{document_title}"

            # -------------------------------------------------
            # Relevant articles: deduplicate theo (so_hieu, dieu, khoan)
            # Format:
            #   Khoản > 0  → "{so_hieu}|{title}|Điều {dieu}, Khoản {khoan}"
            #   Khoản == 0 → "{so_hieu}|{title}|Điều {dieu}"
            # -------------------------------------------------
            article_key = (so_hieu, article_number, clause_number)

            if so_hieu and article_number and article_key not in articles:
                if clause_number and clause_number > 0:
                    label = f"Điều {article_number}, Khoản {clause_number}"
                else:
                    label = f"Điều {article_number}"

                articles[article_key] = f"{so_hieu}|{document_title}|{label}"

        return (
            list(docs.values()),
            list(articles.values()),
        )
