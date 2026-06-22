import re
from bs4 import BeautifulSoup
from models.article import Article, Clause, Point

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
        current_article = None
        current_clause = None 
        current_point = None

        for prov, text in blocks:
            # ===================================================
            # Điều 
            # ===================================================
            if prov == "prov-article":
                if current_article:
                    if current_point and current_clause:
                        current_clause["points"].append(current_point)
                        current_point = None 

                    if current_clause:
                        current_article["clauses"].append(current_clause)
                        current_clause = None 

                    articles.append(current_article)

                m = re.match(r"Điều\s+(\d+)\.?\s*(.*)", text)
                dieu_id = int(m.group(1)) if m else None 
                tieu_de = m.group(2).strip() if m else ""

                current_article = {
                    "dieu_id": dieu_id,
                    "tieu_de": tieu_de,
                    "lines": [text],
                    "clauses": []
                }
            
            # ===================================================
            # Khoản
            # ===================================================
            elif prov == "prov-clause" and current_article:
                if current_point and current_clause:
                    current_clause["points"].append(current_point)
                    current_point = None

                if current_clause:
                    current_article["clauses"].append(current_clause)
                
                m = re.match(r"(\d+)\.\s*(.*)", text)
                current_clause = {
                    "khoan_id": int(m.group(1)) if m else None,
                    "lines": [text],
                    "points": []
                }

                current_article["lines"].append(text)
            
            # ===================================================
            # Điểm 
            # ===================================================
            elif prov == "prov-item" and current_article:
                current_article["lines"].append(text)

                if current_clause:
                    current_clause["lines"].append(text)
                    
                    if current_point:
                        current_clause["points"].append(current_point)
                    
                    m = re.match(r"([a-zđ])\)\s*(.*)", text, re.IGNORECASE)
                    current_point = {
                        "diem_id": m.group(1) if m else None,
                        "lines": [text]
                    }
            
            # ===================================================
            # Điều mới 
            # ===================================================
            elif prov == "prov-content" and current_article:
                current_article["lines"].append(text)

                if current_point:
                    current_point["lines"].append(text)
                elif current_clause:
                    current_clause["lines"].append(text)


        # ===================================================
        # Flush article cuối 
        # ===================================================
        if current_article:
            if current_point and current_clause:
                current_clause["points"].append(current_point)

            if current_clause:
                current_article["clauses"].append(current_clause)
            
            articles.append(current_article)

        # ===================================================
        # Convert sang dataclass 
        # ===================================================
        result = []

        for article in articles:
            clauses = []
            
            for clause in article["clauses"]:
                points = []

                for point in clause["points"]:
                    points.append(
                        Point(
                            diem_id=point["diem_id"],
                            noi_dung="\n".join(point["lines"])
                        )
                    )

                clauses.append(
                    Clause(
                        khoan_id=clause["khoan_id"],
                        noi_dung="\n".join(clause["lines"]),
                        points=points
                    )
                )
            
            result.append(
                Article(
                    dieu_id=article["dieu_id"],
                    tieu_de=article["tieu_de"],
                    noi_dung="\n".join(article["lines"]),
                    clauses=clauses
                )
            )
        
        return result