# from pathlib import Path

# from agents.main import Agent

# PROJECT_ROOT = Path(__file__).resolve().parents[3]

# IDENTITY_PATH = PROJECT_ROOT / "src" / "agents" / "silas" / "IDENTIDADE.md"


# class World:
#     citizens: list[Citizen]

#     def __init__(self) -> None:
#         loaded = [Citizen("Silas", IDENTITY_PATH)]

#         self.citizens = loaded

#     async def load_citizens(self):
#         if not self.citizens or not len(self.citizens):
#             loaded = [Citizen("Silas", IDENTITY_PATH)]
#             self.citizens = loaded
