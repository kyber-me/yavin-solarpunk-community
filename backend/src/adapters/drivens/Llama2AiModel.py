from ports.drivens.ai_provider_port import AiModelPort


class Llama2AiModel(AiModelPort):
    def __init__(self):
        self.codename = "llama2:7b"

        self.name = "Llama2"
        self.version = "2"
        self.params = "7b"