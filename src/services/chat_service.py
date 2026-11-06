from pathlib import Path
from typing import Any

from src.agents.main import Agent
from src.domain.chat.conversations.main import Conversation
from src.domain.chat.conversations.value_objects.conversation_id import ConversationId
from src.domain.chat.messages.main import TextMessage
from src.services.service_interface import IService
from src.types.app_error import AppError
from src.types.dtos.chat_service_request import ChatServiceRequestDto

# current_path é um objeto representando o arquivo atual. Neste objeto
# pode-se realizar operações de arquivos, como por exemplo, `mkdir`.
current_path = Path(
    __file__
)  # /Users/tiagocuri/Repos/Yavin/src/services/chat_service.py

# project_path_module = Path(__name__)  # "src.services.chat_service"

PROJECT_ROOT = current_path.resolve().parents[2]  # /Users/tiagocuri/Repos/Yavin
PROJECT_SOURCE = current_path.resolve().parents[1]  # /Users/tiagocuri/Repos/Yavin/src


# Redis Analogue (this remains on memory?)
CHAT_CACHE: dict[str, str] = {}


# 1 - O ChatService pode ser utilizado apenas quando há conversas em andamento (é mais barato enviar mensagens via agente por telefone virtual?)

# 2 - Como identificar que há uma conversa em andamento entre 2 agentes? (humanos ou máquinas). O Frontend é responsável por enviar informações do `sender` (há como burlar o id do sender? Dificilmente. Seria preciso conhecer um id válido. É importante não expor id's.)


# 3. Em caso de tentativa de estabelecer contato com um id que não pertence à aquele usuário, precisamos conferir se: usuário está conectado ao sistema. Se não, configura potencial fraude. Se sim, uma conversa seria iniciada por um usuário X com um outro agente Y
# se passando por uma outra pessoa Z.
class ChatService(IService):
    @classmethod
    async def run(cls, dto: ChatServiceRequestDto) -> dict[str, Any]:

        # Adicionar camada de PromptShield
        if not dto.message.content.strip():
            raise AppError(
                code="INVALID_REQUEST",
                message="The message is required",
                status_code=400,
            )

        conversation_id = ConversationId(dto.message.sender, dto.message.receiver)
        # Look-up for a existent conversation by id
        conversation_exists = CHAT_CACHE.get(conversation_id.id)
        if not conversation_exists:
            # This Conversation has a mixed ID (review it)
            # If conversation does not exist, there is no messages exchanged between no one
            # If conversation does not exist, this will be the first message
            new_conversation = Conversation(conversation_id, dto.thread_id)
            new_message = TextMessage(
                dto.message.content,
                dto.sender_id,
                dto.receiver_id,
                new_conversation.id,
                conversation_id.id,
            )

            # Cache the conversation for future recovering
            CHAT_CACHE[conversation_id.id] = new_conversation

            # Save the conversation and the message on the Database (?)
            # ?

        identity_path = (
            PROJECT_ROOT / "src" / "agents" / "prompts" / "IDENTIDADE_ID_SILAS.md"
        )
        silas = Agent("Silas", identity_path)

        try:
            response = silas.invoke(dto.message.content, dto.thread_id)

            return response
        except Exception as e:  # noqa: BLE001
            print(e)  # Logs

            raise AppError(
                code="INTERNAL_SERVER_ERROR",
                message="An error has ocurred",
                status_code=500,
            )
