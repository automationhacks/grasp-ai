def main():
    # Initialize the SDK
    config = Configuration(app_name="foundry_local_rag")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    # Load the embedding model
    embedding_model = manager.catalog.get_model("qwen3-embedding-0.6b")
    embedding_model.download(
        lambda p: print(
            f"\rDownloading embedding model: {p:.1f}%", end="", flush=True)
    )
    print()
    embedding_model.load()
    embedding_client = embedding_model.get_embedding_client()

    # Embed all documents in a single batch call
    response = embedding_client.generate_embeddings(documents)
    doc_embeddings = [item.embedding for item in response.data]
    print(f"Indexed {len(doc_embeddings)} documents.")


def find_relevant(query_embedding, doc_embedding, top_k=2):
    """
    This method takes a user query converted into embedding and a database of each document
    embedding and computes the cosine similarity score. It then picks the top_k documents
    with a higher score
    """
    scores = []
    for i, doc_emb in enumerate(doc_embedding):
        # Take the query embedding and compute the cosine_similarity from each
        # document embedding
        score = cosine_similarity(query_embedding, doc_emb)
        scores.append((i, score))
    # Sort the scores based on score
    scores.sort(key=lambda x: x[1], reverse=True)
    # Pick the top 2
    return scores[:top_k]


def cosine_similarity(a, b):
    """
    Compute cosine similarity between 2 vectors
    Cosine tells how close 2 vectors are in direction regardless of magnitude
    Values near 1.0 indicate high similarity
    """

    # Step 1: Store the dot product
    # Dot product is a rough measure of alignment as if the vector represents similarity with large
    # positive nos, the product will climb higher
    # zip will create a tuple from each vector no
    # we then do multiplications and store the sum of all dot products
    dot = sum(x * y for x, y in zip(a, b))

    # Step 2: Compute the euclidean norm or length of a vector written as ||a||
    # This computes the raw size or magnitude of the vector, larger docs will have higher norm
    # than shorter single word query
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    # Step 3: Normalization
    # This strips the length/magnitude and isolates the angle between them
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


if __name__ == "__main__":
    main()
