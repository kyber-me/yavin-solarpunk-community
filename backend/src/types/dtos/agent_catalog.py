"""Public catalog contract; IDs identify available participants, not agent instances."""
from pydantic import BaseModel


class AgentSummary(BaseModel):
    id: str
    name: str
    public_description: str | None


class AgentCatalog(BaseModel):
    agents: list[AgentSummary]
