from typing import Any, TypedDict, Dict, List, Union, Optional

from pydantic import BaseModel, Field
from playwright.async_api import Page


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
    """Base abstract message class.

    Messages are the inputs and outputs of ChatModels.
    """

    content: Union[str, List[Union[str, Dict]]]
    """The string contents of the message."""

    additional_kwargs: dict = Field(default_factory=dict)
    """Reserved for additional payload data associated with the message.
    
    For example, for a message from an AI, this could include tool calls as
    encoded by the model provider.
    """

    response_metadata: dict = Field(default_factory=dict)
    """Response metadata. For example: response headers, logprobs, token counts."""

    type: str
    """The type of the message. Must be a string that is unique to the message type.
    
    The purpose of this field is to allow for easy identification of the message type
    when deserializing messages.
    """

    name: Optional[str] = None
    """An optional name for the message. 
    
    This can be used to provide a human-readable name for the message.
    
    Usage of this field is optional, and whether it's used or not is up to the
    model implementation.
    """

    id: Optional[str] = None
    """An optional unique identifier for the message. This should ideally be
    provided by the provider/model which created the message."""


# This represents the state of the agent
# as it proceeds through execution
class AgentState(TypedDict):
    page: Page  # The Playwright web page lets us interact with the web environment
    input: str  # User request
    img: str  # b64 encoded screenshot
    bboxes: list[BBox]  # The bounding boxes from the browser annotation function
    prediction: Prediction  # The Agent's output
    # A system message (or messages) containing the intermediate steps
    scratchpad: list[BaseMessage]
    observation: str  # The most recent response from a tool



