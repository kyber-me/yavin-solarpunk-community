from pathlib import Path
from fastapi import Request
# from typing import Any
# from ulid import ULID

from src.infra.db.relational.conversation_repository import PostgresConversationRepository
from src.infra.db.relational.message_record import MessageRecord
from src.infra.db.relational.message_repository import PostgresMessageRepository
from src.agents.agent import Agent
from src.services.service_interface import IService
from src.types.app_error import AppError
from src.types.dtos.chat_service_request import ChatServiceRequest, Message
from src.services.message_mapper import message_to_record
# from src.infra.cache.cache import CHAT_CACHE


current_path = Path(
    __file__
)  # /Users/tiagocuri/Repos/Yavin/backend/src/services/chat_service.py

# project_path_module = Path(__name__)  # "src.services.chat_service"

PROJECT_ROOT = current_path.resolve().parents[2]  # /Users/tiagocuri/Repos/Yavin/backend
PROJECT_SOURCE = current_path.resolve().parents[1]  # /Users/tiagocuri/Repos/Yavin/backend/src


class ChatService(IService):
    @classmethod
    def run(
        cls, dto: ChatServiceRequest, request: Request
    ) -> dict[str, str]:

        content = dto.message
        # Add Prompt Injection Defend (PromptShield)
        if not content.strip():
            raise AppError(
                code="INVALID_REQUEST",
                message="The message is required",
                status_code=400,
            )

        # If conversation does not exist in cache, search in the database
        # If not found raise an error
        # ---------------------------------------------------------------
        # Rapidly look-up for an existent conversation by id
        # cache_key = (str(conversation_look_up_id), dto.thread_id)
        # conversation_exists = CHAT_CACHE.get(cache_key)
        # ---------------------------------------------------------------
        conversation_repo = PostgresConversationRepository(request.app.state.conversation_pool)
        conversation_exists = conversation_repo.get_by_id(dto.conversation_id)
        if not conversation_exists:
            raise AppError(
                code="CONVERSATION_NOT_FOUND",
                message="The conversation was not found",
                status_code=404,
            )
        if dto.sender_id not in (conversation_exists.sender_id, conversation_exists.participant_id):
            raise AppError(
                code="CONVERSATION_FORBIDDEN",
                message="The sender does not participate in this conversation",
                status_code=403,
            )
        if not conversation_exists.active:
            raise AppError(
                code="CONVERSATION_INACTIVE",
                message="The conversation is inactive",
                status_code=409,
            )

        message = Message(content=content)
        message_record = message_to_record(
            message,
            conversation_id=dto.conversation_id,
            sender_id=dto.sender_id
        )

        # Once the system receives a message from a sender (the `sender_id` identifies the message owner)
        # it must persist it on database. If, for some reason, the receiver could not respond,
        # the system returns an error but the original message from the sender is kept (?)

        message_repo = PostgresMessageRepository(request.app.state.conversation_pool)
        # return {"content": result["messages"][-1].content}
        response: dict[str, str] | None
        try:
            result = message_repo.create(message_record) # What happens if it fails?
            try:
                instructions_path = (
                        PROJECT_ROOT / "src" / "agents" / "prompts" / "IDENTIDADE_ID_SILAS.md"
                )
                checkpointer = request.app.state.checkpointer

                # checkpointer gives memory to the agent (even the object Agent is recreated every request)
                silas = Agent("Silas", instructions_path, checkpointer)
                response = silas.invoke(result.content, conversation_exists.thread_id)

                if not response:
                    raise AppError(
                        code="INTERNAL_SERVER_ERROR",
                        message="An error has occurred",
                        status_code=500,
                    )

                message_record = MessageRecord(
                    conversation_id=dto.conversation_id,
                    sender_id=(
                        conversation_exists.participant_id
                        if dto.sender_id == conversation_exists.sender_id
                        else conversation_exists.sender_id
                    ),
                    content=response["content"]
                )
                message_repo.create(message_record)
            except AppError:
                raise
            except ValueError as e:
                print(e)
                raise AppError(
                    code="INVALID_REQUEST",
                    message=str(e),
                    status_code=400,
                ) from e
            except Exception as e:  # noqa: BLE001
                print(e)  # Logs
                raise AppError(
                    code="INTERNAL_SERVER_ERROR",
                    message="An error has occurred",
                    status_code=500,
                ) from e
        except AppError:
            raise
        except ValueError as e:
            print(e)  # Logs
            raise AppError(
                code="INVALID_REQUEST",
                message=str(e),
                status_code=400,
            ) from e
        except RuntimeError as e:
            print(e)  # Logs
            raise AppError(
                code="INTERNAL_SERVER_ERROR",
                message=str(e),
                status_code=500,
            ) from e
        except Exception as e:
            print(e)  # Logs
            raise AppError(
                code="INTERNAL_SERVER_ERROR",
                message="An error has occurred",
                status_code=500,
            ) from e

        return response


