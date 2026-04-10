"""Weather Agent - Main agent orchestration."""

import logging
from typing import List, Dict, Any, Optional, cast

from .config import get_config
from .tools import WeatherTool, get_tool_schemas
from .models import AgentResponse, WeatherData
from .utils import format_weather_response
from .exceptions import WeatherAgentError, APIKeyError


logger = logging.getLogger(__name__)


class WeatherAgent:
    """Main agent class for weather information."""

    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """Initialize WeatherAgent.

        Args:
            provider: LLM provider (anthropic/openai)
            model: Model name
        """
        self.config = get_config()
        self.provider = provider or self.config.get("llm.provider", "anthropic")
        self.model = model or self.config.get("llm.model", "claude-3-haiku-20240307")

        self.weather_tool = WeatherTool()
        self.tools = get_tool_schemas()
        self.conversation_history: List[Dict[str, str]] = []

        self._setup_system_prompt()

    def _setup_system_prompt(self) -> None:
        """Set up the system prompt for the agent."""
        self.system_prompt = """You are a helpful weather information assistant. 
Your role is to provide accurate weather information to users in a friendly and conversational manner.

You have access to tools to fetch weather data:
- get_weather: Get current weather for a city
- get_forecast: Get weather forecast for a city
- geocode_location: Convert city names to coordinates

When a user asks about weather:
1. Use the appropriate tool to get the weather data
2. Format the response in a helpful, conversational way
3. Provide additional helpful information like clothing or activity recommendations

Always be accurate and honest about weather conditions. If you don't have information, say so."""

    def _get_llm_response(self, user_message: str) -> Dict[str, Any]:
        """Get response from LLM.

        Args:
            user_message: User's message

        Returns:
            LLM response dictionary

        Raises:
            APIKeyError: If API key is missing
        """
        if self.provider == "anthropic":
            return self._get_anthropic_response(user_message)
        elif self.provider == "openai":
            return self._get_openai_response(user_message)
        else:
            raise WeatherAgentError(f"Unknown provider: {self.provider}")

    def _get_anthropic_response(self, user_message: str) -> Dict[str, Any]:
        """Get response from Anthropic Claude.

        Args:
            user_message: User's message

        Returns:
            LLM response with tool_use
        """
        try:
            import anthropic
        except ImportError:
            raise APIKeyError("anthropic")

        api_key = self.config.get_api_key("anthropic")
        client = anthropic.Anthropic(api_key=api_key)

        messages = self.conversation_history + [
            {"role": "user", "content": user_message}
        ]

        response = client.messages.create(
            model=self.model,
            max_tokens=self.config.get("llm.max_tokens", 1024),
            system=self.system_prompt,
            messages=cast(Any, messages),
            tools=cast(Any, self.tools),
        )

        result: Dict[str, Any] = {"content": [], "tool_calls": []}

        for block in response.content:
            if block.type == "text":
                result["content"].append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                result["tool_calls"].append(
                    {"name": block.name, "input": block.input, "id": block.id}
                )

        return result

    def _get_openai_response(self, user_message: str) -> Dict[str, Any]:
        """Get response from OpenAI.

        Args:
            user_message: User's message

        Returns:
            LLM response with tool_calls
        """
        try:
            import openai
        except ImportError:
            raise APIKeyError("openai")

        api_key = self.config.get_api_key("openai")
        client = openai.OpenAI(api_key=api_key)

        messages = self.conversation_history + [
            {"role": "user", "content": user_message}
        ]

        response = client.chat.completions.create(
            model=self.model, messages=cast(Any, messages), tools=cast(Any, self.tools)
        )

        message = response.choices[0].message
        result: Dict[str, Any] = {"content": [], "tool_calls": []}

        if message.content:
            result["content"].append({"type": "text", "text": message.content})

        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_data = getattr(tool_call, "function", None)
                if function_data is None:
                    continue

                result["tool_calls"].append(
                    {
                        "name": getattr(function_data, "name", ""),
                        "arguments": getattr(function_data, "arguments", {}),
                        "id": tool_call.id,
                    }
                )

        return result

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool and return the result.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tool execution result
        """
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

        if tool_name == "get_weather":
            city = tool_input.get("city")
            if not city:
                raise ValueError("City parameter is required for get_weather")
            return self.weather_tool.get_weather(
                city=city, units=tool_input.get("units", "metric")
            )
        elif tool_name == "get_forecast":
            city = tool_input.get("city")
            if not city:
                raise ValueError("City parameter is required for get_forecast")
            return self.weather_tool.get_forecast(
                city=city,
                units=tool_input.get("units", "metric"),
                days=tool_input.get("days", 5),
            )
        elif tool_name == "geocode_location":
            if "lat" in tool_input and "lon" in tool_input:
                lat = tool_input.get("lat")
                lon = tool_input.get("lon")
                if lat is None or lon is None:
                    raise ValueError(
                        "Both lat and lon parameters are required for reverse geocoding"
                    )
                return self.weather_tool.reverse_geocode(lat=lat, lon=lon)
            else:
                city = tool_input.get("city")
                if not city:
                    raise ValueError("City parameter is required for geocoding")
                return self.weather_tool.geocode(city=city)
        else:
            raise WeatherAgentError(f"Unknown tool: {tool_name}")

    def _format_tool_result(self, tool_name: str, result: Any) -> str:
        """Format tool result for LLM.

        Args:
            tool_name: Name of the executed tool
            result: Tool result

        Returns:
            Formatted result string
        """
        if tool_name == "get_weather":
            if isinstance(result, WeatherData):
                units = "metric"
                return format_weather_response(
                    {
                        "name": result.city,
                        "main": {
                            "temp": result.temperature,
                            "feels_like": result.feels_like,
                            "humidity": result.humidity,
                        },
                        "weather": [{"description": result.condition.description}],
                        "wind": {"speed": result.wind_speed},
                    },
                    units,
                )
            return str(result)

        elif tool_name == "get_forecast":
            lines = [f"Weather forecast for {result.city}, {result.country}:"]
            for day in result.forecasts:
                lines.append(
                    f"- {day.date.strftime('%Y-%m-%d')}: "
                    f"{day.condition.description}, "
                    f"High: {day.temp_max}°, Low: {day.temp_min}°, "
                    f"Humidity: {day.humidity}%"
                )
            return "\n".join(lines)

        elif tool_name == "geocode_location":
            if isinstance(result, list):
                return f"Found {len(result)} locations: " + ", ".join(
                    f"{r.city}, {r.country} ({r.latitude}, {r.longitude})"
                    for r in result
                )
            elif result:
                return f"Location: {result.city}, {result.country} ({result.latitude}, {result.longitude})"
            return "No location found"

        return str(result)

    def chat(self, user_message: str) -> AgentResponse:
        """Process a user message and return agent response.

        Args:
            user_message: User's message

        Returns:
            AgentResponse object
        """
        if not user_message or not user_message.strip():
            return AgentResponse(
                message="I need a valid message to help you with weather information. Please ask me about the weather!",
                error="Empty message",
            )

        user_message = user_message.strip()
        logger.info(f"Processing message: {user_message}")

        try:
            response = self._get_llm_response(user_message)

            tool_calls = response.get("tool_calls", [])

            if tool_calls:
                tool_results = []
                used_tools = []
                for tool_call in tool_calls:
                    tool_name = tool_call.get("name")
                    if not tool_name:
                        logger.error(f"Tool call missing name: {tool_call}")
                        continue

                    tool_input = tool_call.get("input") or tool_call.get(
                        "arguments", {}
                    )

                    if isinstance(tool_input, str):
                        import json

                        try:
                            tool_input = json.loads(tool_input)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse tool input JSON: {e}")
                            continue

                    try:
                        result = self._execute_tool(tool_name, tool_input)
                        formatted_result = self._format_tool_result(tool_name, result)
                        tool_results.append(
                            {
                                "tool_call_id": tool_call.get("id"),
                                "result": formatted_result,
                            }
                        )
                        used_tools.append(tool_name)
                    except Exception as e:
                        logger.error(f"Tool execution error for {tool_name}: {e}")
                        continue

                    if isinstance(tool_input, str):
                        import json

                        try:
                            tool_input = json.loads(tool_input)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse tool input JSON: {e}")
                            continue

                    try:
                        result = self._execute_tool(tool_name, tool_input)
                        formatted_result = self._format_tool_result(tool_name, result)
                        tool_results.append(
                            {
                                "tool_call_id": tool_call.get("id"),
                                "result": formatted_result,
                            }
                        )
                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        tool_results.append(
                            {
                                "tool_call_id": tool_call.get("id"),
                                "result": f"Error: {str(e)}",
                            }
                        )

                self.conversation_history.append(
                    {"role": "user", "content": user_message}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": str(response.get("content", []))}
                )

                final_response = self._get_llm_with_tool_results(
                    user_message, tool_results
                )
                message = final_response.get("content", [{}])[0].get(
                    "text", "Here's the weather information:"
                )

                return AgentResponse(
                    message=message, tool_used=used_tools[0] if used_tools else None
                )
            else:
                message = response.get("content", [{}])[0].get(
                    "text", "I'm here to help with weather information!"
                )

                self.conversation_history.append(
                    {"role": "user", "content": user_message}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": message}
                )

                return AgentResponse(message=message)

        except WeatherAgentError as e:
            logger.error(f"Chat error: {e}")
            return AgentResponse(message=e.user_message, error=str(e))
        except Exception as e:
            logger.error(f"Unexpected chat error: {e}")
            return AgentResponse(
                message="I'm having trouble right now. Please try again in a moment.",
                error=str(e),
            )

    def _get_llm_with_tool_results(
        self, original_message: str, tool_results: List[Dict]
    ) -> Dict:
        """Get final LLM response after tool execution.

        Args:
            original_message: Original user message
            tool_results: List of tool execution results

        Returns:
            LLM response
        """
        tool_result_content = []
        for result in tool_results:
            content = f"Tool result: {result.get('result', 'No result')}"
            tool_result_content.append(
                {
                    "type": "tool_result",
                    "tool_use_id": result.get("tool_call_id"),
                    "content": content,
                }
            )

        if self.provider == "anthropic":
            return self._get_anthropic_response_with_results(
                original_message, tool_result_content
            )
        else:
            return self._get_openai_response_with_results(
                original_message, tool_result_content
            )

    def _get_anthropic_response_with_results(
        self, message: str, tool_results: List[Dict]
    ) -> Dict:
        """Get Anthropic response with tool results."""
        import anthropic

        api_key = self.config.get_api_key("anthropic")
        client = anthropic.Anthropic(api_key=api_key)

        messages = self.conversation_history + [{"role": "user", "content": message}]

        anthropic_messages = messages + [
            {"role": "assistant", "content": cast(Any, tool_results)}
        ]

        any_client = cast(Any, client)
        response = any_client.messages.create(
            model=self.model,
            max_tokens=self.config.get("llm.max_tokens", 1024),
            system=self.system_prompt,
            messages=anthropic_messages,
        )

        return {
            "content": [{"type": "text", "text": block.text}]
            for block in response.content
            if hasattr(block, "text")
        }

    def _get_openai_response_with_results(
        self, message: str, tool_results: List[Dict]
    ) -> Dict:
        """Get OpenAI response with tool results."""
        import openai

        api_key = self.config.get_api_key("openai")
        client = openai.OpenAI(api_key=api_key)

        messages = self.conversation_history + [{"role": "user", "content": message}]

        for result in tool_results:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": str(result.get("tool_use_id", "")),
                    "content": str(result.get("content", "")),
                }
            )

        response = client.chat.completions.create(
            model=self.model, messages=cast(Any, messages)
        )

        return {
            "content": [{"type": "text", "text": response.choices[0].message.content}]
        }

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history.

        Returns:
            List of conversation messages
        """
        return self.conversation_history.copy()
