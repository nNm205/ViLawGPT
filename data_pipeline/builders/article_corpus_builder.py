import json
from pathlib import Path
from parsers.article_parser import ArticleParser

class ArticleCorpusBuilder:
    def __init__(self, parser: ArticleParser):
        self.parser = parser

    def build_for(self, doc) -> dict:
        corpus: dict[str, str] = {}

        for article in self.parser.parse(doc.content_html):
            article_header = f"Điều {article.dieu_id}. {article.tieu_de}"
            
            # ==========================================================================
            # Điều có khoản 
            # ==========================================================================
            if article.clauses:
                for clause in article.clauses:
                    khoan_id = clause.khoan_id if clause.khoan_id is not None else 0
                    
                    # ==========================================================================
                    # Khoản có điểm 
                    # ==========================================================================
                    if clause.points:
                      for point in clause.points:
                        diem_id = point.diem_id if point.diem_id is not None else "x"
                    
                        key = (
                          f"{doc.doc_id}_"
                          f"{article.dieu_id}_"
                          f"{khoan_id}_"
                          f"{diem_id}"
                        )

                        corpus[key] = (
                          f"{doc.header}\n"
                          f"{article_header}\n"
                          f"Khoản {khoan_id}\n"
                          f"{point.noi_dung}"
                        )

                    # ==========================================================================
                    # Khoản không có điểm 
                    # ==========================================================================
                    else:
                      key = (
                        f"{doc.doc_id}_"
                        f"{article.dieu_id}_"
                        f"{khoan_id}"
                      )

                      corpus[key] = (
                        f"{doc.header}\n"
                        f"{article_header}\n"
                        f"{clause.noi_dung}"
                      )

            # ==========================================================================
            # Điều không có khoản  
            # ==========================================================================
            else:
                key = (
                  f"{doc.doc_id}_"
                  f"{article.dieu_id}_0"
                )

                corpus[key] = (
                  f"{doc.header}\n"
                  f"{article_header}\n"
                  f"{article.noi_dung}"
                )

        return corpus

    def save(self, corpus: dict, output_path: Path):
        output_path.parent.mkdir(
          parents=True, 
          exist_ok=True
        )

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(corpus, f, ensure_ascii=False, indent=2)
