import openai
from foundry_local_sdk import Configuration, FoundryLocalManager


# Initialize the Foundry Local SDK
config = Configuration(app_name="foundry_local_samples")
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance

# Download and register all execution providers.
current_ep = ""
def _ep_progress(ep_name: str, percent: float):
    global current_ep
    if ep_name != current_ep:
        if current_ep:
            print()
        current_ep = ep_name
    print(f"\r  {ep_name:<30}  {percent:5.1f}%", end="", flush=True)

manager.download_and_register_eps(progress_callback=_ep_progress)
if current_ep:
    print()

# Load a model
model = manager.catalog.get_model("qwen2.5-0.5b")
model.download(
    lambda progress: print(
        f"\rDownloading model: {progress:.2f}%",
        end="",
        flush=True,
    )
)
print()
model.load()
print("Model loaded.")

# Start web service to expose OpenAI compatible REST endpoint
manager.start_web_service()
base_url = f"{manager.urls[0]}/v1"

client = openai.OpenAI(
    base_url=base_url,
    api_key="none"
)

# Make a chat completion request via API
response = client.chat.completions.create(
    model=model.id,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the golden ratio?"}
    ],
    stream=True,
)

for chunk in response:
    choices = chunk.choices

    if len(choices) > 0:
        choice = choices[0]
        if choice.delta and choice.delta.content:
            print(choice.delta.content, end="", flush=True)
print()

model.unload()
manager.stop_web_service()