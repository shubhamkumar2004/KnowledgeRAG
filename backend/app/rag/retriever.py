import re

import chromadb

from app.rag.embeddings import load_embedding_model


VECTOR_DB_DIR = "vector_db"
COLLECTION_NAME = "ekta_trust"

# ---------------------------------------------------------
# These are cached once per Python process.
#
# This is important because loading the embedding model
# repeatedly was causing retrieval to take several seconds.
# ---------------------------------------------------------

_embedding_model = None
_collection = None


def load_retrieval_system():
    """
    Load the embedding model and ChromaDB collection once.

    Future retrieve() calls in the same Python process reuse
    both instead of loading them again.
    """

    global _embedding_model, _collection

    if _embedding_model is None:
        print("Loading retrieval system...")

        _embedding_model = load_embedding_model()

        client = chromadb.PersistentClient(
            path=VECTOR_DB_DIR
        )

        _collection = client.get_collection(
            name=COLLECTION_NAME
        )

        print("Retrieval system ready.")

    return _embedding_model, _collection


def tokenize(text: str) -> set[str]:
    """
    Convert text into a set of lowercase words.

    Example:

        "What is the Vision?"
            ->
        {"what", "is", "the", "vision"}
    """

    return set(
        re.findall(
            r"[a-zA-Z0-9]+",
            text.lower()
        )
    )


# ---------------------------------------------------------
# Words that are not useful for distinguishing one Ekta
# Trust page from another.
#
# "ekta", "trust", and "navnirman" are intentionally here
# because they appear throughout the website.
# ---------------------------------------------------------

STOP_WORDS = {
    "what",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "for",
    "to",
    "in",
    "on",
    "and",
    "about",
    "tell",
    "me",
    "please",
    "does",
    "do",
    "how",
    "can",
    "i",
    "give",
    "show",
    "explain",
    "details",
    "detail",
    "information",
    "ekta",
    "trust",
    "navnirman",
}


def get_important_words(text: str) -> list[str]:
    """
    Extract meaningful words from a question.

    Example:

        "What is the vision of Ekta Trust?"

    becomes:

        ["vision"]
    """

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower()
    )

    return [
        word
        for word in words
        if word not in STOP_WORDS
    ]


def keyword_score(
    question: str,
    document: str,
    source: str
) -> float:
    """
    Calculate lexical relevance.

    The score considers:

    1. Individual keyword matches in document text
    2. Keyword matches in source/page name
    3. Consecutive phrase matches

    Source matches receive more weight because a query
    containing "insurance", for example, is strong evidence
    for Insurance.aspx.txt.

    Phrase matching is especially useful for queries such as:

        "Education Loan Scheme"

    because the full phrase is stronger evidence than the
    individual words appearing separately.
    """

    important_words = get_important_words(
        question
    )

    if not important_words:
        return 0.0

    document_lower = document.lower()
    source_lower = source.lower()

    document_words = tokenize(document)
    source_words = tokenize(source)

    score = 0.0

    # =====================================================
    # 1. INDIVIDUAL KEYWORD MATCHING
    # =====================================================

    for word in important_words:

        # Match inside actual document content.
        if word in document_words:
            score += 1.0

        # Match inside page/source name.
        # Source metadata receives more weight.
        if word in source_words:
            score += 2.0

    # =====================================================
    # 2. CONSECUTIVE PHRASE MATCHING
    #
    # Example:
    #
    # important_words:
    #
    # ["education", "loan", "scheme"]
    #
    # Generates:
    #
    # "education loan"
    # "loan scheme"
    # "education loan scheme"
    # =====================================================

    if len(important_words) >= 2:

        for phrase_length in range(
            2,
            len(important_words) + 1
        ):

            for start in range(
                len(important_words)
                - phrase_length
                + 1
            ):

                phrase_words = important_words[
                    start:
                    start + phrase_length
                ]

                phrase = " ".join(
                    phrase_words
                )

                # Longer exact phrases provide stronger
                # evidence.
                phrase_bonus = (
                    phrase_length * 2.0
                )

                if phrase in document_lower:
                    score += phrase_bonus

                if phrase in source_lower:
                    score += (
                        phrase_bonus * 1.5
                    )

    return score


def calculate_title_bonus(
    question: str,
    source: str
) -> float:
    """
    Give a small additional ranking bonus when important
    words from the question directly match the page name.

    Examples:

        "What is the vision..."
            -> Vision.txt

        "What is the motto..."
            -> Motto.txt

        "What insurance schemes..."
            -> Insurance.aspx.txt

    This is generic. No page name or topic is hardcoded.

    The bonus is intentionally small so semantic meaning
    still remains the main retrieval signal.
    """

    important_words = get_important_words(
        question
    )

    source_words = tokenize(source)

    title_matches = sum(
        1
        for word in important_words
        if word in source_words
    )

    # Each title match = +0.08
    #
    # Maximum bonus = 0.16 so title matching cannot
    # completely dominate semantic relevance.
    title_bonus = min(
        title_matches * 0.05,
        0.10
    )

    return title_bonus


def retrieve(
    question: str,
    top_k: int = 5,
    semantic_candidate_count: int = 30,
    keyword_candidate_count: int = 30
):
    """
    Hybrid retrieval pipeline.

    PIPELINE:

    1. Embed the user's question
    2. Semantic search using ChromaDB
    3. Global keyword search over ALL chunks
    4. Merge semantic + keyword candidate pools
    5. Calculate missing semantic similarities
    6. Calculate keyword/phrase relevance
    7. Calculate title/source bonus
    8. Hybrid reranking
    9. Return Top K chunks

    This gives us the benefits of both:

        semantic understanding
                +
        exact terminology/page matching
    """

    model, collection = (
        load_retrieval_system()
    )

    total_documents = collection.count()

    if total_documents == 0:
        return []

    # =====================================================
    # STEP 1: EMBED QUESTION
    # =====================================================

    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    )

    # =====================================================
    # STEP 2: SEMANTIC CANDIDATES
    #
    # Retrieve a wider candidate pool instead of taking
    # only the final Top 5 immediately.
    # =====================================================

    semantic_candidate_count = min(
        semantic_candidate_count,
        total_documents
    )

    semantic_results = collection.query(
        query_embeddings=[
            question_embedding.tolist()
        ],
        n_results=semantic_candidate_count
    )

    candidates = {}

    for index in range(
        len(
            semantic_results[
                "documents"
            ][0]
        )
    ):

        document = (
            semantic_results[
                "documents"
            ][0][index]
        )

        metadata = (
            semantic_results[
                "metadatas"
            ][0][index]
        )

        distance = (
            semantic_results[
                "distances"
            ][0][index]
        )

        candidate_id = (
            metadata["source"],
            metadata["chunk_id"]
        )

        candidates[candidate_id] = {
            "document": document,
            "source": metadata["source"],
            "chunk_id":
                metadata["chunk_id"],
            "distance": distance
        }

    # =====================================================
    # STEP 3: GLOBAL KEYWORD SEARCH
    #
    # Search ALL stored chunks.
    #
    # This solved our earlier problem where Vision.txt
    # could be ranked around #20 semantically and therefore
    # never reach the hybrid reranker.
    # =====================================================

    all_data = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    keyword_results = []

    for document, metadata in zip(
        all_data["documents"],
        all_data["metadatas"]
    ):

        score = keyword_score(
            question=question,
            document=document,
            source=metadata["source"]
        )

        if score > 0:

            keyword_results.append(
                {
                    "document": document,
                    "source":
                        metadata["source"],
                    "chunk_id":
                        metadata["chunk_id"],
                    "keyword_score":
                        score
                }
            )

    # Highest lexical relevance first.
    keyword_results.sort(
        key=lambda item:
            item["keyword_score"],
        reverse=True
    )

    keyword_results = (
        keyword_results[
            :keyword_candidate_count
        ]
    )

    # =====================================================
    # STEP 4: MERGE KEYWORD CANDIDATES
    #
    # Add keyword candidates that were missing from the
    # semantic candidate pool.
    # =====================================================

    for result in keyword_results:

        candidate_id = (
            result["source"],
            result["chunk_id"]
        )

        if candidate_id not in candidates:

            candidates[candidate_id] = {
                "document":
                    result["document"],
                "source":
                    result["source"],
                "chunk_id":
                    result["chunk_id"],

                # We do not yet know its semantic distance.
                "distance": None
            }

    # =====================================================
    # STEP 5:
    # CALCULATE SEMANTIC DISTANCE FOR KEYWORD-ONLY RESULTS
    #
    # Chroma returned distances only for semantic search
    # results.
    #
    # Keyword-only candidates therefore need their
    # embeddings calculated here.
    # =====================================================

    missing_candidates = [
        candidate
        for candidate
        in candidates.values()
        if candidate["distance"] is None
    ]

    if missing_candidates:

        missing_texts = [
            candidate["document"]
            for candidate
            in missing_candidates
        ]

        missing_embeddings = model.encode(
            missing_texts,
            normalize_embeddings=True
        )

        # Because both embeddings are normalized:
        #
        # dot product = cosine similarity
        #
        # cosine distance =
        #
        # 1 - cosine similarity

        for candidate, embedding in zip(
            missing_candidates,
            missing_embeddings
        ):

            similarity = float(
                question_embedding
                @ embedding
            )

            candidate["distance"] = (
                1.0 - similarity
            )

    # =====================================================
    # STEP 6: HYBRID RERANKING
    # =====================================================

    hybrid_results = []

    for candidate in candidates.values():

        # -------------------------------------------------
        # SEMANTIC SCORE
        #
        # Chroma cosine distance:
        #
        # lower = better
        #
        # Convert it into similarity:
        #
        # similarity = 1 - distance
        # -------------------------------------------------

        semantic_score = (
            1.0
            - candidate["distance"]
        )

        # -------------------------------------------------
        # KEYWORD / PHRASE SCORE
        # -------------------------------------------------

        lexical_score = keyword_score(
            question=question,
            document=candidate[
                "document"
            ],
            source=candidate[
                "source"
            ]
        )

        # Keyword scores can become larger than 1 because
        # phrase matches receive bonuses.
        #
        # Convert the raw score into a bounded value
        # between 0 and 1.
        normalized_keyword_score = min(
            lexical_score / 10.0,
            1.0
        )

        # -------------------------------------------------
        # TITLE / SOURCE BONUS
        #
        # Example:
        #
        # "vision" -> Vision.txt
        #
        # This helps when the embedding model gives an
        # unexpectedly low semantic score to a page whose
        # title directly matches the question.
        # -------------------------------------------------

        title_bonus = (
            calculate_title_bonus(
                question=question,
                source=candidate[
                    "source"
                ]
            )
        )

        # -------------------------------------------------
        # FINAL HYBRID SCORE
        #
        # Semantic meaning remains the main signal.
        #
        # Keyword/phrase evidence provides additional
        # lexical grounding.
        #
        # Exact source-title evidence gets a small bonus.
        # -------------------------------------------------

        hybrid_score = (
            0.60 * semantic_score
            +
            0.40
            * normalized_keyword_score
            +
            (title_bonus * 0.5)
        )

        hybrid_results.append(
            {
                "document":
                    candidate["document"],

                "source":
                    candidate["source"],

                "chunk_id":
                    candidate["chunk_id"],

                "distance":
                    candidate["distance"],

                "semantic_score":
                    semantic_score,

                "keyword_score":
                    lexical_score,

                "normalized_keyword_score":
                    normalized_keyword_score,

                "title_bonus":
                    title_bonus,

                "hybrid_score":
                    hybrid_score
            }
        )

    # =====================================================
    # STEP 7: FINAL SORT
    #
    # Higher hybrid score = better result.
    # =====================================================

    hybrid_results.sort(
        key=lambda item:
            item["hybrid_score"],
        reverse=True
    )

    return hybrid_results[:top_k]


# =========================================================
# MANUAL TEST
# =========================================================

if __name__ == "__main__":

    question = (
        "What are the details of the "
        "Education Loan Scheme?"
    )

    print("\nQUESTION:")
    print(question)

    results = retrieve(
        question=question,
        top_k=10
    )

    print("\nTOP HYBRID RESULTS:")

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            "\n"
            + "=" * 60
        )

        print(
            f"RESULT {index}"
        )

        print(
            "SOURCE:",
            result["source"]
        )

        print(
            "CHUNK ID:",
            result["chunk_id"]
        )

        print(
            "VECTOR DISTANCE:",
            round(
                result["distance"],
                4
            )
        )

        print(
            "SEMANTIC SCORE:",
            round(
                result["semantic_score"],
                4
            )
        )

        print(
            "KEYWORD SCORE:",
            round(
                result["keyword_score"],
                4
            )
        )

        print(
            "NORMALIZED KEYWORD SCORE:",
            round(
                result[
                    "normalized_keyword_score"
                ],
                4
            )
        )

        print(
            "TITLE BONUS:",
            round(
                result["title_bonus"],
                4
            )
        )

        print(
            "HYBRID SCORE:",
            round(
                result["hybrid_score"],
                4
            )
        )

        print("-" * 60)

        print(
            result["document"]
        )