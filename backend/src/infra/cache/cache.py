from typing import Any

# Redis Analogue (this remains on memory?)
CHAT_CACHE: dict[tuple[str, str], Any] = {}