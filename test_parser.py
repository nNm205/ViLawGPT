import sys, json
sys.path.insert(0, 'data_pipeline')
from parsers.article_parser import ArticleParser
from models.document import VbplDocument

with open('data/processed/json/12807.json', encoding='utf-8') as f:
    doc = VbplDocument.from_detail(json.load(f))

parser = ArticleParser()
articles = parser.parse(doc.content_html)

print(f"Total articles in doc 12807: {len(articles)}")

found = [a for a in articles if a.dieu_id == 2]
if found:
    a = found[0]
    print(f"\n=== Dieu {a.dieu_id} | {len(a.clauses)} khoan ===")
    for c in a.clauses:
        print(f"\n--- Khoan {c.khoan_id} ---")
        print(c.noi_dung)
else:
    print("Dieu 2 not found, available:", [a.dieu_id for a in articles[:10]])
