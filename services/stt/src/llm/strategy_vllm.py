import logging
import uuid
from typing import List, Optional, Generator

from vllm import EngineArgs, LLMEngine, SamplingParams

from src.core.settings import Settings
from src.llm.domain import DomainGenerateResponse, DomainGenerateStreamResponse
from src.llm.prompt import build_qwen_prompt, LlmError

logger = logging.getLogger(__name__)


class VllmEngine:
    """Strategy for Linux using vLLM."""

    def __init__(self, settings: Settings):
        model_name = (
            getattr(settings.llm, "model", "Qwen/Qwen2.5-14B-Instruct-AWQ")
            if hasattr(settings, "llm")
            else "Qwen/Qwen2.5-14B-Instruct-AWQ"
        )
        logger.info(f"Initializing vLLM engine with model: {model_name}")

        try:
            engine_args = EngineArgs(
                model=model_name,
                quantization="awq",
                tensor_parallel_size=1,
                gpu_memory_utilization=0.60,
                max_model_len=8192,
                enforce_eager=True,
            )
            self.engine = LLMEngine.from_engine_args(engine_args)
        except Exception as e:
            logger.exception("Failed to initialize vLLM engine.")
            raise LlmError(f"vLLM initialization failed: {str(e)}") from e

    def generate(
        self,
        query: str,
        context_chunks: List[str],
        max_tokens: Optional[int] = 512,
        temperature: Optional[float] = 0.1,
    ) -> DomainGenerateResponse:
        prompt = build_qwen_prompt(query, context_chunks)
        sampling_params = SamplingParams(
            temperature=temperature or 0.1, max_tokens=max_tokens or 512
        )
        request_id = str(uuid.uuid4())

        try:
            self.engine.add_request(request_id, prompt, sampling_params)
            final_output = ""
            while self.engine.has_unfinished_requests():
                for output in self.engine.step():
                    if output.request_id == request_id and output.finished:
                        final_output = output.outputs[0].text
            return DomainGenerateResponse(text=final_output)
        except Exception as e:
            logger.exception("LLM generation failed.")
            raise LlmError(f"Generation failed: {str(e)}") from e

    def generate_stream(
        self,
        query: str,
        context_chunks: List[str],
        max_tokens: Optional[int] = 512,
        temperature: Optional[float] = 0.1,
    ) -> Generator[DomainGenerateStreamResponse, None, None]:
        prompt = build_qwen_prompt(query, context_chunks)
        sampling_params = SamplingParams(
            temperature=temperature or 0.1, max_tokens=max_tokens or 512
        )
        request_id = str(uuid.uuid4())

        try:
            self.engine.add_request(request_id, prompt, sampling_params)
            previous_text_len = 0
            while self.engine.has_unfinished_requests():
                for output in self.engine.step():
                    if output.request_id == request_id:
                        current_text = output.outputs[0].text
                        text_delta = current_text[previous_text_len:]
                        previous_text_len = len(current_text)
                        yield DomainGenerateStreamResponse(
                            text_delta=text_delta, is_finished=output.finished
                        )
        except Exception as e:
            logger.exception("LLM streaming generation failed.")
            raise LlmError(f"Streaming generation failed: {str(e)}") from e
