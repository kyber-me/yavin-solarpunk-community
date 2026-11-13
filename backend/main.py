from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import uvicorn
import os
from fastapi import FastAPI, Query, Request, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from src.agents.infra.open_checkpointer_helper import open_checkpointer
from src.persistence.db.relational.conversation_pool import open_conversation_pool
from src.services.send_message_service import SendMessageService
from src.services.create_conversation_service import CreateConversationService
from src.services.agent_catalog_service import get_agent_catalog
from src.types.app_error import AppError
from src.types.dtos.api_response import ApiError, ApiResponse
from src.types.dtos.send_message_service_request import SendMessageRequest
from src.types.dtos.create_conversation_request import CreateConversationRequest, UpdateConversationTitleRequest
from src.types.dtos.agent_catalog import AgentCatalog
from src.services.helpers.conversation_history import list_conversations, list_messages
from src.persistence.db.relational.agent_repository import AgentRepository
from src.types.dtos.conversation_history import ConversationPage, MessagePage
from src.services.update_conversation_title_service import UpdateConversationTitleService
from src.persistence.cache.container import cache_container
from src.constants import IDEALIZADOR_ACCESS_KEY_ENV
from src.types.dtos.idealizador_access import IdealizadorAccessRequest
from src.domain.document import ingest_documents

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")


@asynccontextmanager
async def lifespan(super_app: FastAPI):
    db_uri = os.getenv("DATABASE_URI")
    if not db_uri:
        raise ValueError("DATABASE_URI environment variable not set.")

    super_app.state.cache_container = cache_container
    # result = ingest_documents([
    #     "institutional/YAVIN_RESEARCH_PROJECT.md", ""
    #     "library/JUGAAD",
    #     "library/SOLARPUNK_MANIFESTO.md",
    #     "library/SWADESHI.md"
    # ], use_vec_store=True)
    with open_conversation_pool(db_uri) as pool:
        # Why AgentRepository?
        AgentRepository(pool).seed()
        with open_checkpointer() as checkpointer:
            super_app.state.conversation_pool = pool
            super_app.state.checkpointer = checkpointer
            yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(AppError)
async def handle_app_error(_, exception: AppError):
    response = ApiResponse[None](
        error=ApiError(code=exception.code, message=exception.message, details=exception.details)
    )

    return JSONResponse(
        status_code=exception.status_code, content=response.model_dump(mode="json")
    )


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(request: Request, exception: RequestValidationError):
    if request.url.path != "/access/idealizador":
        return await request_validation_exception_handler(request, exception)

    response = ApiResponse[None](
        error=ApiError(
            code="IDEALIZADOR_ACCESS_INVALID_REQUEST",
            message="Payload inválido.",
        )
    )
    return JSONResponse(status_code=422, content=response.model_dump(mode="json"))


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/access/idealizador", response_model=ApiResponse[dict[str, bool]])
async def idealizador_access(payload: IdealizadorAccessRequest):
    expected = os.getenv(IDEALIZADOR_ACCESS_KEY_ENV)
    if not expected:
        raise AppError(
            code="IDEALIZADOR_ACCESS_NOT_CONFIGURED",
            message="O acesso provisório do Idealizador não está configurado.",
            status_code=503,
        )
    if payload.key != expected:
        raise AppError(
            code="IDEALIZADOR_ACCESS_DENIED",
            message="Palavra-chave incorreta.",
            status_code=401,
        )
    return ApiResponse(data={"authorized": True})


@app.get("/agents", response_model=ApiResponse[AgentCatalog])
async def list_agents(request: Request):
    return ApiResponse(data=await run_in_threadpool(get_agent_catalog, request.app.state.conversation_pool))


@app.post("/conversation/message", response_model=ApiResponse[dict[Any, Any]])
async def chat(payload: SendMessageRequest, request: Request):
    result = await run_in_threadpool(
        SendMessageService.run, payload, request
    )

    return ApiResponse(data=result)


@app.get("/conversations", response_model=ApiResponse[ConversationPage])
async def conversations(
    request: Request, sender_id: str = Query(min_length=1),
    limit: int = Query(default=100, ge=1, le=100), offset: int = Query(default=0, ge=0),
):
    result = await run_in_threadpool(list_conversations, request, sender_id, limit, offset)
    return ApiResponse(data=result)


@app.get("/conversations/{conversation_id}/messages", response_model=ApiResponse[MessagePage])
async def messages(
    conversation_id: str, request: Request, sender_id: str = Query(min_length=1),
    limit: int = Query(default=100, ge=1, le=100), offset: int = Query(default=0, ge=0),
):
    result = await run_in_threadpool(list_messages, request, conversation_id, sender_id, limit, offset)
    return ApiResponse(data=result)


@app.post(
    "/conversation/create",
    response_model=ApiResponse[dict[str, str]],
    status_code = status.HTTP_201_CREATED
)
async def create_conversation(payload: CreateConversationRequest, request: Request):
    result = await run_in_threadpool(CreateConversationService.run, payload, request)
    return ApiResponse(data=result)


@app.patch("/conversations/{conversation_id}/title", response_model=ApiResponse[dict[str, str]])
async def update_conversation_title(conversation_id: str, payload: UpdateConversationTitleRequest, request: Request):
    result = await run_in_threadpool(UpdateConversationTitleService.run, conversation_id, payload, request)
    return ApiResponse(data=result)


def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    print("Hello from yavin!")
    main()
