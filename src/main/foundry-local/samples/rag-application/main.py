import math

from foundry_local_sdk import Configuration, FoundryLocalManager

# Knowledge base
documents = [
    "Foundry Local runs AI models directly on your device without cloud connectivity.",
    "The Foundry Local SDK supports Python, C#, JavaScript, and Rust.",
    "Embedding models convert text into numerical vectors for similarity search.",
    "Foundry Local uses ONNX Runtime for efficient model inference on CPUs and GPUs.",
    "The model catalog provides pre-optimized models that you can download and run locally.",
    "Retrieval-augmented generation grounds model responses in your own data.",
    "Vector similarity search finds documents that are semantically close to a query.",
    "Chat completions generate natural language responses from a prompt and context.",
]


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

    # Load the chat model
    chat_model = manager.catalog.get_model("qwen2.5-0.5b")
    chat_model.download(
        lambda p: print(
            f"\rDownloading chat model: {p:.1f}%", end="", flush=True)
    )
    print()
    chat_model.load()
    chat_client = chat_model.get_chat_client()

    print("\nModels loaded. Ready for questions.")
    print("\nThe knowledge base contains information about:")
    print("  - Foundry Local features and architecture")
    print("  - Supported programming languages")
    print("  - Embedding models and vector search")
    print("  - ONNX Runtime inference")
    print("  - The model catalog")
    print("  - RAG and chat completions")
    print("\nExample questions:")
    print('  "What programming languages does the SDK support?"')
    print('  "How does Foundry Local run models?"')
    print('  "What is retrieval-augmented generation?"')
    print('\nType "quit" to exit.\n')

    # Interactive query loop
    while True:
        query = input("Question: ").strip()
        if not query or query.lower() == "quit":
            break

        # Embed the query
        query_response = embedding_client.generate_embedding(query)
        query_embedding = query_response.data[0].embedding

        # Retrieve the most relevant documents
        results = find_relevant(query_embedding, doc_embeddings, top_k=2)
        context = "\n".join(f"- {documents[i]}" for i, _ in results)

        # Build the prompt with retrieved context
        messages = [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using only the provided context. "
                    "If the context doesn't contain enough information, say so.\n\n"
                    f"Context:\n{context}"
                ),
            },
            {"role": "user", "content": query},
        ]

        # Stream the response
        print("Answer: ", end="", flush=True)
        for chunk in chat_client.complete_streaming_chat(messages):
            if chunk.choices:
                content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print("\n")

    # Clean up
    embedding_model.unload()
    chat_model.unload()
    print("Models unloaded. Done!")


if __name__ == "__main__":
    main()
