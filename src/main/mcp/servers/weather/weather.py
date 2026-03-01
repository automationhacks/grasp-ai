from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """
    Make a request to the NWS API and return the JSON response.
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_alert(feature: dict) -> str:
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)


# Resource example
@mcp.resource("weather://us_states")
def get_us_states() -> str:
    """Return a list of all US state codes for use with get_alerts tool."""
    states = """
US State Codes:
AL - Alabama, AK - Alaska, AZ - Arizona, AR - Arkansas, CA - California
CO - Colorado, CT - Connecticut, DE - Delaware, FL - Florida, GA - Georgia
HI - Hawaii, ID - Idaho, IL - Illinois, IN - Indiana, IA - Iowa
KS - Kansas, KY - Kentucky, LA - Louisiana, ME - Maine, MD - Maryland
MA - Massachusetts, MI - Michigan, MN - Minnesota, MS - Mississippi, MO - Missouri
MT - Montana, NE - Nebraska, NV - Nevada, NH - New Hampshire, NJ - New Jersey
NM - New Mexico, NY - New York, NC - North Carolina, ND - North Dakota, OH - Ohio
OK - Oklahoma, OR - Oregon, PA - Pennsylvania, RI - Rhode Island, SC - South Carolina
SD - South Dakota, TN - Tennessee, TX - Texas, UT - Utah, VT - Vermont
VA - Virginia, WA - Washington, WV - West Virginia, WI - Wisconsin, WY - Wyoming
"""
    return states


@mcp.resource("weather://tips")
def get_weather_tips() -> str:
    """Return weather safety and forecasting tips."""
    tips = """
Weather Safety and Forecasting Tips:

1. ALERTS: Always check for active weather alerts in your area before making plans
2. FORECAST: Use forecasts for up to 5 days - accuracy decreases beyond that
3. SEVERE WEATHER: Wind speeds above 40 mph and temperatures below 0°F require precautions
4. PLANNING: High impact weather can affect travel, outdoor events, and utilities
5. UPDATES: Check forecasts regularly as conditions can change throughout the day
"""
    return tips


# Prompt examples
@mcp.prompt(
    name="analyze_forecast",
    description="Prompt for analyzing weather forecast data"
)
def analyze_forecast_prompt() -> str:
    """Prompt template for analyzing weather forecast."""
    return """You are a weather analyst. Analyze the forecast data provided and:
1. Identify the key weather patterns
2. Highlight any significant temperature swings
3. Note wind conditions that might affect activities
4. Provide a summary suitable for general audience
Format your response clearly with sections for each aspect."""


@mcp.prompt(
    name="severe_weather_response",
    description="Prompt for responding to severe weather alerts"
)
def severe_weather_prompt() -> str:
    """Prompt template for responding to severe weather."""
    return """You are an emergency response coordinator. Given the weather alert:
1. Assess the severity and affected areas
2. Recommend immediate actions for residents
3. Suggest precautions based on the specific hazard
4. Identify vulnerable populations (elderly, children, outdoor workers)
Be concise but comprehensive in your response."""


if __name__ == "__main__":
    mcp.run()
