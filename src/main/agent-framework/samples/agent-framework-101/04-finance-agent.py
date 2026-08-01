import datetime
import os
import random
from time import timezone
from typing import Annotated

from agent_framework import create_harness_agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()
# Config
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")

# instructions
FINANCE_INSTRUCTIONS = """\
## Personal Finance Assistant Instructions

You are a personal finance and investing assistant. When asked about a stock, look up its current
price with the get_stock_price tool, and use web search for recent news, earnings, or analyst
commentary.

### Working style
- Always verify numbers with a tool rather than relying on memory. Stock prices change.
- Cite web sources inline when you use them.
- Keep the user's watchlist in a memory file called `watchlist.md`: read it when reviewing the
  watchlist, and update it whenever the user adds or removes a ticker.
"""

# constants
_PRICE_BOOK: dict[str, float] = {
    "MSFT": 462.97,
    "AAPL": 229.35,
    "GOOGL": 178.12,
    "AMZN": 201.45,
    "NVDA": 134.81,
}


# tools
def get_stock_price(
    symbol: Annotated[str, "The stock ticker symbol, e.g. MSFT or AAPL."],
) -> dict[str, object]:
    """
    Get the latest (delayed, illustrative) stock price for a ticker symbol.
    """
    ticker = symbol.upper()
    price = _PRICE_BOOK.get(ticker)

    if not price:
        price = random.uniform(100.10, 500.99)
    return {
        "symbol": ticker,
        "price": round(price, 2),
        "currency": "USD",
        "as_of": datetime.now(timezone.utc).isoformat(),
    }


# Setup
client = FoundryChatClient(
    project_endpoint=PROJECT_ENDPOINT,
    model="gpt5.4-mini",
    credential=AzureCliCredential(),
)

# Agent harness
agent = create_harness_agent(
    client=client, agent_instructions=FINANCE_INSTRUCTIONS, tools=get_stock_price
)
