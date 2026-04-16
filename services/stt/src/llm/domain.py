from dataclasses import dataclass
from typing import Optional


@dataclass
class DomainUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __post_init__(self):
        for attr_name in ["prompt_tokens", "completion_tokens", "total_tokens"]:
            val = getattr(self, attr_name)
            if not isinstance(val, int) or isinstance(val, bool):
                raise TypeError(
                    f"Expected '{attr_name}' to be an int, got {type(val).__name__}"
                )
            if val < 0:
                raise ValueError(f"Expected '{attr_name}' to be non-negative.")


@dataclass
class DomainGenerateResponse:
    """The full result of a unary generation request."""

    text: str
    usage: Optional[DomainUsage] = None

    def __post_init__(self):
        if not isinstance(self.text, str):
            raise TypeError(
                f"Expected 'text' to be a string, got {type(self.text).__name__}"
            )
        if self.usage is not None and not isinstance(self.usage, DomainUsage):
            raise TypeError("Expected 'usage' to be a DomainUsage instance or None.")


@dataclass
class DomainGenerateStreamResponse:
    """A single chunk yielded during a streaming generation request."""

    text_delta: str
    is_finished: bool
    usage: Optional[DomainUsage] = None

    def __post_init__(self):
        if not isinstance(self.text_delta, str):
            raise TypeError(
                f"Expected 'text_delta' to be a string, got {type(self.text_delta).__name__}"
            )
        if not isinstance(self.is_finished, bool):
            raise TypeError(
                f"Expected 'is_finished' to be a bool, got {type(self.is_finished).__name__}"
            )
        if self.usage is not None and not isinstance(self.usage, DomainUsage):
            raise TypeError("Expected 'usage' to be a DomainUsage instance or None.")
