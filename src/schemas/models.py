from playwright.async_api import Page
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict


class BBox(TypedDict):
    x: float
    y: float
    text: str
    type: str
    ariaLabel: str


class Prediction(TypedDict):
    action: str
    args: dict | None


class BaseMessage(BaseModel):
    content: str | list[str | dict]
    additional_kwargs: dict = Field(default_factory=dict)
    response_metadata: dict = Field(default_factory=dict)
    type: str
    name: str | None = None
    id: str | None = None


class AgentState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    page: Page | None = None
    input: str | None = None
    img: str | None = None
    bboxes: list[BBox] | None = None
    prediction: Prediction | None = None
    scratchpad: str = ""
    observation: str | None = None
