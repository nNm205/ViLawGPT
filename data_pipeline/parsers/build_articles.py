from repositories.document_repository import DocumentRepository
from parsers.article_parser import ArticleParser
from builders.article_corpus_builder import ArticleCorpusBuilder

repo = DocumentRepository("data/processed/json")
parser = ArticleParser()
builder = ArticleCorpusBuilder(parser)
corpus = {}

for doc in repo.iter_documents():
    corpus.update(builder.build_for(doc))

builder.save(corpus, "data/articles.json")
print(f"Built {len(corpus)} articles")