from typing import TypedDict

from playwright.async_api import Page
from pydantic import BaseModel, Field


class BBox(TypedDict):
    x: float
    y: float
    text: str
    type: str
    ariaLabel: str


class Prediction(TypedDict):
    action: str
    args: list[str] | None


class BaseMessage(BaseModel):
    content: str | list[str | dict]
    additional_kwargs: dict = Field(default_factory=dict)
    response_metadata: dict = Field(default_factory=dict)
    type: str
    name: str | None = None
    id: str | None = None


class AgentState(BaseModel):
    page: Page
    input: str
    img: str
    bboxes: list[BBox]
    prediction: Prediction
    scratchpad: list[BaseMessage]
    observation: str
