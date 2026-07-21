import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from foundry_local_sdk import Configuration, FoundryLocalManager


app = FastAPI()


def main():
    print("Hello from local-ai!")

    config = Configuration(app_name="local_ai_agent")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model("qwen2.5-0.5b")
    model.download(lambda p: print(f"Downloading. {p}%"))
    model.load()
    client = model.get_chat_client()

    class ChatRequest(BaseModel):
        messages: list

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatRequest):
        client = get_model_client()
        response = client.complete_chat(request.messages)

        return {
            'choices': [
                {
                    'messages': {
                        "role": "assistant",
                        content: response.choices[0].messages.content
                    }
                }
            ]
        }


if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, reload=True)
