from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    config = Configuration(app_name="foundry_local_samples")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    # Download and register all execution providers (ep)
    current_ep = ""

    def ep_progress(ep_name: str, percent: float):
        nonlocal current_ep
        if ep_name != current_ep:
            if current_ep:
                print()
            current_ep = ep_name
        print(f'\r {ep_name:<30} {percent:5.1f}%', end="", flush=True)

    manager.download_and_register_eps(progress_callback=ep_progress)
    if current_ep:
        print()

    # Select and load a model from catalogue
    model = manager.catalog.get_model("qwen2.5-0.5b")
    # Fetches model weights to your local cache
    model.download(lambda progress: print(
        f'\nDownloading model: {progress:.2f}%', end='', flush=True))
    print()
    # makes the model ready for inference.
    model.load()
    print('Model loaded and ready')

    # Get a chat client
    client = model.get_chat_client()

    # Start the conversation with a system prompt
    messages = [
        {
            "role": "system",
            "content": "You are a helpful, friendly assistant. Keep your responses"
            "concise and conversational. If you don't know something, say so"
        }
    ]
    print("\nChat assistant ready! Type 'quit' to exit.\n")

    # To maintain context across the conversation, we need to append the user input
    # as well as model responses to a running history and pass it to the model on each turn
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("quit", "exit"):
            break

        # Add the users message to conversation history
        messages.append({"role": "user", "content": user_input})

        # Stream response by token
        print("Assistant: ", end="", flush=True)
        full_response = ""

        for chunk in client.complete_streaming_chat(messages):
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_response += content
        print("\n")

        # Add the complete message to conversation history
        messages.append({"role": "assistant", "content": full_response})

    # Clean up - unload the model
    model.unload()
    print("Model unloaded. Goodbye!")


if __name__ == "__main__":
    main()
