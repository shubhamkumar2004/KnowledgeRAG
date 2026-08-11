from pathlib import Path


RAW_DATA_DIR = Path("data/raw")


def load_documents():
    """
    Load all .txt files from data/raw.
    """

    documents = []

    for file_path in RAW_DATA_DIR.glob("*.txt"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        document = {
            "source": file_path.name,
            "text": text
        }

        documents.append(document)

    return documents


def chunk_documents(documents):
    """
    Chunk all loaded documents and preserve their source metadata.
    """

    all_chunks = []

    for document in documents:

        chunks = chunk_text(document["text"])

        for index, chunk in enumerate(chunks):

            chunk_data = {
                "source": document["source"],
                "chunk_id": index,
                "text": chunk
            }

            all_chunks.append(chunk_data)

    return all_chunks

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> list[str]:
    """
    Split text into chunks while trying to preserve natural
    line boundaries.
    """

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        # If we're not at the end of the document,
        # try to split at the last newline.
        if end < len(text):

            split_position = text.rfind("\n", start, end)

            # Only use the newline if it isn't too close
            # to the beginning of the chunk.
            if split_position > start + (chunk_size // 2):
                end = split_position

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        # Move forward but keep some previous context
        new_start = end - overlap

        # Avoid starting in the middle of a line.
        next_newline = text.find("\n", new_start, end)

        if next_newline != -1:
            new_start = next_newline + 1

        # Safety check to guarantee forward movement.
        if new_start <= start:
            new_start = end

        start = new_start

    return chunks


if __name__ == "__main__":

    documents = load_documents()

    print(f"Loaded {len(documents)} documents")

    chunks = chunk_documents(documents)

    print(f"Created {len(chunks)} chunks")

    for chunk in chunks[:5]:

        print("\n" + "=" * 60)

        print("SOURCE:", chunk["source"])
        print("CHUNK ID:", chunk["chunk_id"])
        print("LENGTH:", len(chunk["text"]))

        print("-" * 60)

        print(chunk["text"])