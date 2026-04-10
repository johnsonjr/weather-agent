"""CLI interface for Weather Agent."""

import sys
import click

from .config import get_config
from .agent import WeatherAgent
from .tools import WeatherTool
from .exceptions import WeatherAgentError
from .logging_utils import setup_logging


@click.group()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to config file"
)
@click.option("--debug", "-d", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, config, debug):
    """Weather Agent - AI-powered weather information."""
    ctx.ensure_object(dict)

    config_obj = get_config()
    if config:
        config_obj.load(config)

    if debug:
        config_obj._config["logging"]["level"] = "DEBUG"
        config_obj._config["app"]["debug"] = True

    ctx.obj["config"] = config_obj
    setup_logging(config_obj.config)


@cli.command()
@click.argument("city")
@click.option(
    "--units", "-u", type=click.Choice(["metric", "imperial"]), default="metric"
)
@click.pass_context
def weather(ctx, city, units):
    """Get current weather for a city."""
    if not city or not city.strip():
        click.echo("Error: Please provide a valid city name", err=True)
        return

    city = city.strip()
    if len(city) < 2:
        click.echo("Error: City name must be at least 2 characters long", err=True)
        return

    try:
        config = ctx.obj["config"]

        try:
            tool = WeatherTool(config=config)
            data = tool.get_weather(city, units)

            click.echo(f"\n📍 {data.city}, {data.country}")
            click.echo(f"   {data.condition.description}")
            click.echo(
                f"   🌡️  Temperature: {data.temperature}°{'C' if units == 'metric' else 'F'}"
            )
            click.echo(
                f"   Feels like: {data.feels_like}°{'C' if units == 'metric' else 'F'}"
            )
            click.echo(f"   💧 Humidity: {data.humidity}%")
            click.echo(
                f"   💨 Wind: {data.wind_speed} {'m/s' if units == 'metric' else 'mph'}"
            )

            if data.sunrise and data.sunset:
                from .utils import format_time

                click.echo(f"   🌅 Sunrise: {format_time(data.sunrise)}")
                click.echo(f"   🌇 Sunset: {format_time(data.sunset)}")

        except WeatherAgentError as e:
            click.echo(f"Error: {e.user_message}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("city")
@click.option(
    "--units", "-u", type=click.Choice(["metric", "imperial"]), default="metric"
)
@click.option("--days", "-d", type=int, default=5, help="Number of days (1-5)")
@click.pass_context
def forecast(ctx, city, units, days):
    """Get weather forecast for a city."""
    try:
        config = ctx.obj["config"]
        tool = WeatherTool(config=config)

        data = tool.get_forecast(city, units, days)

        click.echo(f"\n📍 {data.city}, {data.country} - {days}-Day Forecast\n")

        for day in data.forecasts:
            date_str = day.date.strftime("%A, %B %d")
            click.echo(f"📅 {date_str}")
            click.echo(f"   🌤️  {day.condition.description}")
            click.echo(f"   🌡️  High: {day.temp_max}° | Low: {day.temp_min}°")
            click.echo(f"   💧 Humidity: {day.humidity}%\n")

    except WeatherAgentError as e:
        click.echo(f"Error: {e.user_message}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--prompt", "-p", help="Initial prompt")
@click.option(
    "--units", "-u", type=click.Choice(["metric", "imperial"]), default="metric"
)
@click.pass_context
def chat(ctx, prompt, units):
    """Start interactive chat with the weather agent."""
    try:
        config = ctx.obj["config"]
        config._config["cli"]["default_units"] = units

        agent = WeatherAgent()

        if prompt:
            response = agent.chat(prompt)
            click.echo(f"\n🤖 {response.message}\n")
        else:
            click.echo("🌤️  Weather Agent - Interactive Mode")
            click.echo("Type 'exit' or 'quit' to end the session\n")

            while True:
                try:
                    user_input = click.prompt("You")

                    if user_input.lower() in ["exit", "quit", "bye"]:
                        click.echo("Goodbye! 👋")
                        break

                    if not user_input.strip():
                        continue

                    response = agent.chat(user_input)
                    click.echo(f"\n🤖 {response.message}\n")

                except KeyboardInterrupt:
                    click.echo("\nGoodbye! 👋")
                    break
                except Exception as e:
                    click.echo(f"Error: {str(e)}", err=True)

    except WeatherAgentError as e:
        click.echo(f"Error: {e.user_message}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("city")
@click.pass_context
def geocode(ctx, city):
    """Get coordinates for a city."""
    try:
        config = ctx.obj["config"]
        tool = WeatherTool(config=config)

        results = tool.geocode(city)

        click.echo(f"\n📍 Found {len(results)} location(s):\n")

        for i, result in enumerate(results, 1):
            state = f", {result.state}" if result.state else ""
            click.echo(f"{i}. {result.city}{state}, {result.country}")
            click.echo(f"   📌 Coordinates: {result.latitude}, {result.longitude}\n")

    except WeatherAgentError as e:
        click.echo(f"Error: {e.user_message}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    from . import __version__

    click.echo(f"Weather Agent v{__version__}")


def main():
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    main()
