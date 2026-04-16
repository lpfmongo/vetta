import sys
import logging
from src.llm.prompt import LlmError

logger = logging.getLogger(__name__)

# Determine the strategy at runtime based on the OS
if sys.platform == "linux":
    logger.info("Linux OS detected. Loading vLLM engine strategy.")
    from src.llm.strategy_vllm import VllmEngine as LlmEngine

elif sys.platform == "darwin":
    logger.info("macOS detected. Loading Apple MLX engine strategy.")
    from src.llm.strategy_mlx import MlxEngine as LlmEngine

else:
    raise RuntimeError(
        f"Unsupported operating system: {sys.platform}. Only Linux and macOS are supported."
    )

# Expose LlmError and the dynamically selected LlmEngine
__all__ = ["LlmEngine", "LlmError"]
