import re
from bs4 import BeautifulSoup
from models.article import Article

class ArticleParser:
    @staticmethod
    def _norm(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()

    def parse(self, html: str) -> list[Article]:
        soup = BeautifulSoup(html or "", "html.parser")
        blocks = []

        for p in soup.find_all("p"):
            prov = next((c for c in (p.get("class") or []) if c.startswith("prov-")), None)
            text = self._norm(p.get_text())

            if prov and text:
                blocks.append((prov, text))

        articles = []
        current = None

        for prov, text in blocks:
            if prov == "prov-article":
                if current:
                    articles.append(current)

                m = re.match(r"Điều\s+(\d+)", text)
                current = {
                    "dieu_id": int(m.group(1)) if m else None,
                    "lines": [text]
                }

            elif current:
                current["lines"].append(text)

        if current:
            articles.append(current)

        return [
            Article(a["dieu_id"], "\n".join(a["lines"]))
            for a in articles
        ]