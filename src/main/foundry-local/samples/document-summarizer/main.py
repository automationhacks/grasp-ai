import sys
from pathlib import Path

from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    print("Hello from document-summarizer!")

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

    system_prompt = (
        "Summarize the following document into concise bullet points. "
        "Focus on the key points and the main ideas"
    )

    target = sys.argv[1] if len(sys.argv) > 1 else 'document.txt'
    target_path = Path(target)

    if target_path.is_dir():
        summarize_directory(client, target_path, system_prompt)
    else:
        print(f'--- {target_path.name} ---')
        summarize_file(client, target_path, system_prompt)

    # Clean up
    model.unload()
    print('\nModel unloaded. Done!')


def summarize_directory(client, directory, system_prompt):
    txt_files = sorted(Path(directory).glob("*.txt"))

    if not txt_files:
        print(f'No .txt files found in {directory}')
        return

    for txt_file in txt_files:
        print(f'--- {txt_file.name} ---')
        summarize_file(client, txt_file, system_prompt)
        print()


def summarize_file(client, file_path, system_prompt):
    content = Path(file_path).read_text(encoding='utf-8')
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]
    response = client.complete_chat(messages)
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
