from src.ports.drivens.ai_provider_port import AiModelPort

class GptOss20bCloudModel(AiModelPort):
    def __init__(self):
        self.codename = "gpt-oss:20b-cloud"

        self.name = "GPT"
        self.version = ""
        self.params = "20b"