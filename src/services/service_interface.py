from abc import ABC, abstractmethod


class IService(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    async def run(self):
        return NotImplementedError()
