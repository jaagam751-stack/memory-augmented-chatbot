"""
Why this file exists:
    Weather is a classic dynamic tool example. It should be called only when the
    user asks for current weather.

Responsibility:
    - Call OpenWeatherMap's free current weather endpoint.
    - Return temperature, condition, humidity, and wind speed.

How it connects to the project:
    The LangGraph Tool Calling node uses this tool when the router chooses weather.
"""

from typing import Dict

import requests

from app.utils.config import settings


def get_weather(city: str) -> Dict[str, object]:
    """Fetch current weather for a city using OpenWeatherMap."""
    if not settings.openweather_api_key:
        return {"success": False, "output": "OPENWEATHER_API_KEY is missing."}

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": settings.openweather_api_key, "units": "metric"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        output = (
            f"Current weather in {data.get('name', city)}: "
            f"{data['weather'][0]['description']}, "
            f"temperature {data['main']['temp']}°C, "
            f"feels like {data['main']['feels_like']}°C, "
            f"humidity {data['main']['humidity']}%, "
            f"wind {data['wind']['speed']} m/s."
        )
        return {"success": True, "output": output, "raw": data}
    except Exception as exc:
        return {"success": False, "output": f"Weather lookup failed: {exc}"}
