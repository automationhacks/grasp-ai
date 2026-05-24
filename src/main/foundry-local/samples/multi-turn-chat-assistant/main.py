from foundry_local_sdk import Configuration, FoundryLocalManager

config = Configuration(app_name="foundry_local_samples")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

current_ep = ""

# Download and register all execution providers (ep)


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


def main():
    print("Hello from multi-turn-chat-assistant!")


if __name__ == "__main__":
    main()
