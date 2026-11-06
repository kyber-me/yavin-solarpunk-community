from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from src.agents.infra.open_checkpointer_helper import open_checkpointer
from src.services.chat_service import ChatService
from src.types.app_error import AppError
from src.types.dtos.api_response import ApiError, ApiResponse
from src.types.dtos.chat_service_request import ChatServiceRequestDto


@asynccontextmanager
async def lifespan(app: FastAPI):
    with open_checkpointer() as checkpointer:
        app.state.checkpointer = checkpointer
        yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(AppError)
async def handle_app_error(_, exception: AppError):
    response = ApiResponse[None](
        error=ApiError(code=exception.code, message=exception.message)
    )

    return JSONResponse(
        status_code=exception.status_code, content=response.model_dump()
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat", response_model=ApiResponse[dict])
async def chat(payload: ChatServiceRequestDto, request: Request):
    result = await run_in_threadpool(
        ChatService.run, payload, request.app.state.checkpointer
    )

    return ApiResponse(data=result)


def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    print("Hello from yavin!")

    main()
