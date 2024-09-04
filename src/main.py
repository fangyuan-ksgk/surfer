import asyncio
from dataclasses import dataclass
from typing import Optional

import typer
from playwright.async_api import Page, async_playwright

from . import gladia
from .utils.logging import logger
from .utils.utils import read_file

app = typer.Typer()


@dataclass
class MainConfig:
    input_type: str
    prompt_file: str
    start_url: str
    max_steps: int
    max_iterations: int


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


@app.command()
def main(
    input_type: str = typer.Option(
        "text", 
        help="Input type must be either `text` or `audio`"
    ),
    prompt_file: Optional[str] = typer.Option(
        None, 
        help="Path to the prompt file (only when input_type=text)"
    ),
    start_url: str = typer.Option(
        "https://google.com", 
        help="URL to start the browser at"
    ),
    max_steps: int = typer.Option(
        10, 
        help="Maximum number of steps to run / recursion limit"
    ),
    max_iterations: int = typer.Option(
        1, 
        help="Maximum number of iterations to run"
    ),
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
