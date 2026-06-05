from foundry_local_sdk import Configuration, FoundryLocalManager


def main():
    # Initialize Foundry Local sdk
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
        print(f"\r {ep_name:<30} {percent:5.1f}%", end="", flush=True)

    manager.download_and_register_eps(progress_callback=ep_progress)
    if current_ep:
        print()

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

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to tools. "
                "Use them when needed to answer questions accurately. "
            )
        }
    ]

    print("\nTool-calling assistant ready! Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("quit", "exit"):
            break

        messages.append({
            "role": "user",
            "content": user_input
        })

        response = client.complete_chat(messages, tools=tools)
        answer = process_tool_calls(messages, response, client)

        messages.append({
            "role": "assistant",
            "content": answer
        })
        print(f"Assistant: {answer}\n")

    # Clean up
    model.unload()
    print("Model unloaded. Goodbye")


# Each tool describes tools name and description
# and parameters that describes expected input for each parameters
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city or location"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            # description helps a model decide when to use it
            "description": "Perform a math calculation",
            # parameters describe the expected input
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "The math expression to evaluate"
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def get_weather(location, unit='celsius'):
    return {
        "location": location,
        "temperature": 22 if unit == 'celsius' else 72,
        "unit": unit,
        "condition": 'Sunny'
    }


def calculate(expression):
    allowed = set('0123456789+-*/(). ')
    if not all(char in allowed for char in expression):
        return {"error": "Invalid expression"}

    try:
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


tool_functions = {
    "get_weather": get_weather,
    "calculate": calculate
}


if __name__ == "__main__":
    main()
