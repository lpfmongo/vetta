import logging
from typing import List, Optional, Generator

from mlx_lm import load, generate as mlx_generate, stream_generate
from src.core.settings import Settings
from src.llm.domain import DomainGenerateResponse, DomainGenerateStreamResponse
from src.llm.prompt import build_qwen_prompt, LlmError

logger = logging.getLogger(__name__)


class MlxEngine:
    """Strategy for macOS using Apple MLX."""

    def __init__(self, settings: Settings):
        self.model_name = "mlx-community/Qwen2.5-14B-Instruct-4bit"
        logger.info(f"Initializing Apple MLX engine with model: {self.model_name}")

        try:
            self.model, self.tokenizer = load(self.model_name)
        except Exception as e:
            logger.exception("Failed to initialize MLX engine.")
            raise LlmError(f"MLX initialization failed: {str(e)}") from e

    def generate(
        self,
        query: str,
        context_chunks: List[str],
        max_tokens: Optional[int] = 512,
        temperature: Optional[float] = 0.1,
    ) -> DomainGenerateResponse:
        prompt = build_qwen_prompt(query, context_chunks)
        try:
            response_text = mlx_generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens or 512,
                temp=temperature or 0.1,
                verbose=False,
            )
            return DomainGenerateResponse(text=response_text)
        except Exception as e:
            logger.exception("MLX generation failed.")
            raise LlmError(f"Generation failed: {str(e)}") from e

    def generate_stream(
        self,
        query: str,
        context_chunks: List[str],
        max_tokens: Optional[int] = 512,
        temperature: Optional[float] = 0.1,
    ) -> Generator[DomainGenerateStreamResponse, None, None]:
        prompt = build_qwen_prompt(query, context_chunks)
        try:
            response_stream = stream_generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=max_tokens or 512,
                temp=temperature or 0.1,
            )
            for chunk in response_stream:
                yield DomainGenerateStreamResponse(text_delta=chunk, is_finished=False)
            yield DomainGenerateStreamResponse(text_delta="", is_finished=True)
        except Exception as e:
            logger.exception("MLX streaming generation failed.")
            raise LlmError(f"Streaming generation failed: {str(e)}") from e
