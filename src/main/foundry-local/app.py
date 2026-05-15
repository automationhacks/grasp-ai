from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    # Initialize the Foundry local SDK
    config = Configuration(app_name="foundry_local_samples")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    # Download and register all execution providers
    current_ep = ""

    def ep_progress(ep_name: str, percent: float):
        nonlocal current_ep
        if ep_name != current_ep:
            if current_ep:
                print()
            current_ep = ep_name
        # this enables a live progress bar
        # \r is carriage return which moves cursor back to beginning of the line
        # <30 means left aligned with a fixed 30 char width, for longer names this would not impact the percentage
        # 5.1f indicates total width is 5 characters and 1 decimal place of precision
        # by default python print() adds a newline, end="" keeps cursor on the same line to \r can move it back
        # flush=True, python buffers output and waits for some text to be available to save resources
        # by setting this to true, the text appears instantly, avoiding the hang experience
        print(f"\r {ep_name:<30} {percent:5.1f}%", end="", flush=True)

    manager.download_and_register_eps(progress_callback=ep_progress)
    if current_ep:
        print()

    # Select and load a model from the catalog
    model = manager.catalog.get_model("qwen2.5-0.5b")
    model.download(
        lambda progress: print(
            f"\rDownloading model: {progress:.2f}%",
            end="",
            flush=True
        )
    )
    print()
    model.load()
    print("Model loaded and ready.")

    # Get a chat client
    client = model.get_chat_client()

    # Create the conversation messages
    messages = [
        {
            "role": "user",
            "content": "What is the golden ratio?"
        }
    ]

    # Stream the response token by token
    print("Assistant: ", end="", flush=True)
    try:
        for chunk in client.complete_streaming_chat(messages):
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            if not choice.delta:
                continue
            content = getattr(choice.delta, "content", None)
            if content:
                print(content, end="", flush=True)
        print()
    finally:
        # Clean up even if streaming fails
        model.unload()
        print("Model unloaded.")


# The first run would take time for the model to download and would be a bit slow
if __name__ == '__main__':
    main()
