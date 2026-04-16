import logging
import grpc

from src.generated.llm import llm_pb2, llm_pb2_grpc
from src.llm.engine import LlmEngine, LlmError
from src.core.settings import Settings

logger = logging.getLogger(__name__)


class LLMServicer(llm_pb2_grpc.LLMServiceServicer):
    """
    gRPC Servicer for the LLM.
    Bridges the generated gRPC code with our domain-driven LlmEngine.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        logger.info("Initializing LLMServicer and starting the vLLM engine...")

        # Instantiate the core business logic engine once on startup
        self.engine = LlmEngine(settings)

    def Generate(
        self, request: llm_pb2.GenerateRequest, context: grpc.ServicerContext
    ) -> llm_pb2.GenerateResponse:
        """Unary call: blocks until the entire LLM response is generated."""
        logger.debug(f"Received unary Generate request for query: {request.query}")

        # Extract optional fields properly (proto3 defaults to 0/False if unset)
        max_tokens = request.max_tokens if request.HasField("max_tokens") else None
        temperature = request.temperature if request.HasField("temperature") else None

        try:
            # 1. Hand off to the domain engine
            domain_response = self.engine.generate(
                query=request.query,
                context_chunks=list(request.context_chunks),
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # 2. Map domain usage to gRPC usage (if present)
            usage = None
            if domain_response.usage:
                usage = llm_pb2.Usage(
                    prompt_tokens=domain_response.usage.prompt_tokens,
                    completion_tokens=domain_response.usage.completion_tokens,
                    total_tokens=domain_response.usage.total_tokens,
                )

            # 3. Return the gRPC response
            return llm_pb2.GenerateResponse(text=domain_response.text, usage=usage)

        except LlmError as e:
            logger.error(f"LLM Engine error during Generate: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        except Exception:
            logger.exception("Unexpected error during unary generation.")
            context.abort(
                grpc.StatusCode.UNKNOWN, "An unexpected internal error occurred."
            )

    def GenerateStream(
        self, request: llm_pb2.GenerateRequest, context: grpc.ServicerContext
    ):
        """Streaming call: yields tokens back to the client as they are generated."""
        logger.debug(f"Received GenerateStream request for query: {request.query}")

        max_tokens = request.max_tokens if request.HasField("max_tokens") else None
        temperature = request.temperature if request.HasField("temperature") else None

        try:
            # 1. Get the generator from the domain engine
            stream = self.engine.generate_stream(
                query=request.query,
                context_chunks=list(request.context_chunks),
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # 2. Iterate over the yielded domain chunks
            for domain_chunk in stream:
                # Check if the client disconnected prematurely
                if not context.is_active():
                    logger.info("Client disconnected before stream finished. Halting.")
                    break

                # Map domain usage to gRPC usage (usually only on the final chunk)
                usage = None
                if domain_chunk.usage:
                    usage = llm_pb2.Usage(
                        prompt_tokens=domain_chunk.usage.prompt_tokens,
                        completion_tokens=domain_chunk.usage.completion_tokens,
                        total_tokens=domain_chunk.usage.total_tokens,
                    )

                # 3. Yield the gRPC response chunk
                yield llm_pb2.GenerateStreamResponse(
                    text_delta=domain_chunk.text_delta,
                    is_finished=domain_chunk.is_finished,
                    usage=usage,
                )

        except LlmError as e:
            logger.error(f"LLM Engine error during GenerateStream: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        except Exception:
            logger.exception("Unexpected error during streaming generation.")
            context.abort(
                grpc.StatusCode.UNKNOWN, "An unexpected internal error occurred."
            )
