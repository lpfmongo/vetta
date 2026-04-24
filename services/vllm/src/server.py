import asyncio
import uuid
import grpc

from src.generated import chat_pb2_grpc, chat_pb2

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm import SamplingParams

class ChatServicer(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self, engine: AsyncLLMEngine):
        self.engine = engine

    async def StreamChat(self, request, context):
        # Generate a unique request ID for vLLM continuous batching
        request_id = f"req_{uuid.uuid4().hex}"

        # Configure sampling parameters
        sampling_params = SamplingParams(
            temperature=request.temperature if request.temperature else 0.7,
            max_tokens=512
        )

        # Start async generation
        results_generator = self.engine.generate(request.prompt, sampling_params, request_id)

        last_text = ""
        async for request_output in results_generator:
            # Extract the full generated text so far
            text = request_output.outputs[0].text
            # Calculate only the new tokens to stream back
            new_text = text[len(last_text):]
            last_text = text

            if new_text:
                yield chat_pb2.ChatResponse(text=new_text)


async def serve():
    print("Initializing vLLM AsyncEngine on NVIDIA L4...")
    engine_args = AsyncEngineArgs(model="Qwen/Qwen2.5-3B-Instruct")
    engine = AsyncLLMEngine.from_engine_args(engine_args)

    # Start the async gRPC server
    server = grpc.aio.server()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServicer(engine), server)

    server.add_insecure_port('[::]:50051')
    await server.start()
    print("gRPC Server listening on port 50051")
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
