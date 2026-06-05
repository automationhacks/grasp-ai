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
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a math calculation",
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
