from fastembed import TextEmbedding

_model = None


def embed_texts(texts: list[str]):
    global _model
    if _model is None:
        _model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
    return list(_model.embed(texts))
