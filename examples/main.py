import asyncio

import dotenv
import typer
from playwright.async_api import Page, async_playwright

from src.orchestrator.orchestrator import Orchestrator
from src.orchestrator.prompt import WEB_BROWSING
from src.orchestrator.tools.web import (
    click,
    go_back,
    scroll,
    to_google,
    type_text,
    wait,
)
from src.schemas.config import MainConfig, OrchestratorConfig
from src.schemas.models import AgentState
from src.utils.logging import logger
from src.utils.utils import read_file

app = typer.Typer()

dotenv.load_dotenv()


async def call_agent(question: str, page: Page, max_steps: int):
    agent_state = AgentState(
        page=page,
        input=question,
        scratchpad=[],
    )
    config = OrchestratorConfig(
        system_prompt=WEB_BROWSING,
        llm="openai/gpt-4o",
        agent_state=agent_state,
        tools=[click, type_text, scroll, wait, go_back, to_google],
        max_steps=max_steps,
    )
    orchestrator = Orchestrator(config)
    orchestrator.run()


async def handle_text_input(config: MainConfig, page: Page):
    if config.prompt_file:
        question = read_file(config.prompt_file)
    else:
        # question = typer.prompt("Please enter your question")
        question = "What is the weather in San Francisco?"

    try:
        final_answer = await call_agent(question, page, config.max_steps)
        logger.info(f"final_answer: {final_answer}")
    except Exception:
        pass


async def start(config: MainConfig):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(config.start_url)

        if config.input_type == "text":
            await handle_text_input(config, page)
        else:
            raise ValueError(f"Unsupported input type: {config.input_type}")

        await browser.close()


@app.command()
def main(
    input_type: str = typer.Option("text", help="Input type: 'text' or 'audio'"),
    prompt_file: str | None = typer.Option(None, help="Prompt file path"),
    start_url: str = typer.Option("https://google.com", help="Start URL"),
    max_steps: int = typer.Option(10, help="Max steps"),
    max_iterations: int = typer.Option(1, help="Max iterations"),
) -> None:
    assert input_type in ["text", "audio"]

    config = MainConfig(
        input_type=input_type,
        prompt_file=prompt_file,
        start_url=start_url,
        max_steps=max_steps,
        max_iterations=max_iterations,
    )

    asyncio.run(start(config))


if __name__ == "__main__":
    app()
