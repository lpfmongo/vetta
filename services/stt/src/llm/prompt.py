import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class LlmError(Exception):
    """Custom exception raised when the local LLM engine fails."""

    pass


def build_qwen_prompt(query: str, chunks: List[str]) -> str:
    """Formats the context and query by loading the ChatML template from disk."""
    context_text = "\n\n".join(
        [f"Transcript Chunk {i + 1}:\n{chunk}" for i, chunk in enumerate(chunks)]
    )
    prompt_file = Path(__file__).parent / "qwen_prompt.txt"

    if not prompt_file.is_file():
        logger.error(f"Missing required prompt template: {prompt_file}")
        raise LlmError(
            f"Cannot generate response: Missing prompt file at {prompt_file}"
        )

    prompt_template = prompt_file.read_text(encoding="utf-8")
    return prompt_template.format(context_text=context_text, query=query)
