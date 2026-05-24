def main():
    print("Hello from tutorial-tool-calling!")


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
]


def get_weather(location, unit='celsius'):
    return {
        "location": location,
        "temperature": 22 if unit == 'celsius' else 72,
        "unit": unit,
        "condition": 'Sunny'
    }


tool_functions = {
    "get_weather": get_weather
}


if __name__ == "__main__":
    main()
