from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model():
    """
    Load the local embedding model.
    """
    model = SentenceTransformer(MODEL_NAME)

    return model


def create_embedding(model, text: str):
    """
    Convert text into an embedding vector.
    """
    embedding = model.encode(text)

    return embedding


if __name__ == "__main__":

    model = load_embedding_model()

    sentence_1 = "What is the vision of Ekta Trust?"

    sentence_2 = (
        "Create a casteless and atrocity free society "
        "where people can live with dignity and self respect."
    )

    sentence_3 = (
        "What documents are required for an education loan?"
    )

    embedding_1 = create_embedding(model, sentence_1)
    embedding_2 = create_embedding(model, sentence_2)
    embedding_3 = create_embedding(model, sentence_3)

    similarity_1_2 = model.similarity(
        embedding_1,
        embedding_2
    )

    similarity_1_3 = model.similarity(
        embedding_1,
        embedding_3
    )

    print("\nQUESTION:")
    print(sentence_1)

    print("\nVISION TEXT:")
    print(sentence_2)

    print("\nLOAN TEXT:")
    print(sentence_3)

    print("\nSIMILARITY:")

    print(
        "Question ↔ Vision:",
        similarity_1_2.item()
    )

    print(
        "Question ↔ Loan:",
        similarity_1_3.item()
    )