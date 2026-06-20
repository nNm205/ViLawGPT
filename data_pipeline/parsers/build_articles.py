from repositories.document_repository import DocumentRepository
from parsers.article_parser import ArticleParser
from builders.article_corpus_builder import ArticleCorpusBuilder
from pathlib import Path 

BASE_DIR = Path(__file__).parent.parent.parent
print(BASE_DIR)

repo = DocumentRepository(BASE_DIR / "data/processed/json")
parser = ArticleParser()
builder = ArticleCorpusBuilder(parser)
corpus = {}

for doc in repo.iter_documents():
    corpus.update(builder.build_for(doc))

builder.save(corpus, BASE_DIR / "data/articles.json")
print(f"Built {len(corpus)} articles")