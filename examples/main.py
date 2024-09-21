import asyncio

import typer
from openai import OpenAI
from playwright.async_api import Page, async_playwright

from src import gladia
from src.orchestrator.orchestrator import Orchestrator
from src.orchestrator.prompt import WEB_BROWSING
from src.schemas.config import MainConfig, OrchestratorConfig
from src.utils.logging import logger
from src.utils.utils import read_file

app = typer.Typer()


async def call_agent(question: str, page: Page, max_steps: int):
    pass


async def start(config: MainConfig):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(config.start_url)

        if config.input_type == "text":
            if config.prompt_file:
                question = read_file(config.prompt_file)
            else:
                question = typer.prompt("Please enter your question")

            try:
                final_answer = await call_agent(question, page, config.max_steps)
                logger.info(f"final_answer: {final_answer}")
            except Exception:
                pass
        else:
            for _ in range(config.max_iterations):
                question = await gladia.listen()

        await browser.close()


async def start_test(config: MainConfig):
    client = OpenAI()

    config = OrchestratorConfig(
        system_prompt=WEB_BROWSING,
        # llm="openai/gpt-4o",
        llm="anthropic/claude-3-5-sonnet-20240620",
    )
    orchestrator = Orchestrator(config)


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

    # asyncio.run(start(config))
    asyncio.run(start_test(config))


if __name__ == "__main__":
    app()
