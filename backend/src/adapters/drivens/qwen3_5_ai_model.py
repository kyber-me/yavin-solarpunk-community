from src.ports.drivens.ai_provider_port import AiModelPort


class Qwen3_5_4bAiModel(AiModelPort):
    def __init__(self):
        self.codename = "qwen3.5:4b"

        self.name = "Qwen"
        self.version = "3.5"
        self.params = "4b"

