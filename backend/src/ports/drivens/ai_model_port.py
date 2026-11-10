from abc import ABC, abstractmethod

# What is the effect of having a Qwen Provider Adapter in the system?

class AiModelPort(ABC):
    codename: str
    name: str
    version: str
    params: str

    @abstractmethod
    def __init__(self):
        ...