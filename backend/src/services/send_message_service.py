from pathlib import Path
from fastapi import Request

from src.persistence.db.relational.conversation_repository import PostgresConversationRepository
from src.persistence.db.relational.message_record import MessageRecord
from src.persistence.db.relational.message_repository import PostgresMessageRepository
from src.agents.agent import Agent
from src.services.service_interface import IService
from src.types.app_error import AppError
from src.types.dtos.send_message_service_request import SendMessageRequest, Message
from src.services.helpers.message_mapper import message_to_record
from src.persistence.db.relational.agent_repository import AgentRepository
from src.agents.knowledge import load_general_documents


current_path = Path(
    __file__
)  # /Users/tiagocuri/Repos/Yavin/backend/src/services/send_message_service.py


class SendMessageService(IService):
    @classmethod
    def run(
        cls, dto: SendMessageRequest, request: Request
    ) -> dict[str, str]:

        content = dto.message
        # Add Prompt Injection Defend (PromptShield)
        if not content or not content.strip():
            raise AppError(
                code="INVALID_REQUEST",
                message="The message is required",
                status_code=400,
            )

        # A message sent to a conversation that does not exist does not make sense
        # It can be interpreted as a suspicious behavior
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

        message_repo = PostgresMessageRepository(request.app.state.conversation_pool)
        agent_repo = AgentRepository(request.app.state.conversation_pool)

        agent_id = conversation_exists.participant_id
        agent_record = request.app.state.cache_container["agents"].get(agent_id)
        if agent_record is None:
            agent_record = agent_repo.get(conversation_exists.participant_id)
            if agent_record is None:
                raise AppError(
                    code="AGENT_UNAVAILABLE",
                    message="The conversation agent is unavailable",
                    status_code=422
                )
        try:
            general_documents = request.app.state.cache_container.get("general_documents")
            if not general_documents:
                # Create a Documents repository may be the best approach
                general_documents = load_general_documents(agent_repo.general_pages())
                request.app.state.cache_container["general_documents"] = general_documents
        except (OSError, ValueError) as error:
            raise AppError(
                code="KNOWLEDGE_UNAVAILABLE",
                message="Required knowledge is unavailable",
                status_code=503) from error
        response: dict[str, str] | None
        try:
            # What are the consequences for the user experience if it fails?
            result = message_repo.create(message_record)
            try:
                checkpointer = request.app.state.checkpointer
                silas = Agent(
                    agent_record.name, None,
                    checkpointer,
                    identity_content=agent_record.identity,
                    general_documents=general_documents,
                    agent_id=agent_record.id)

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


