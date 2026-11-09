from ulid import ULID
from src.agents.agent import Agent


class Member:
    id: str
    name: str
    agent: Agent | None

    def __init__(self, id: str, name: str, agent: Agent | None):
        self.id = id
        self.name = name
        self.agent = agent





if __name__ == "__main__":
    print("Hello new Agent")

    member = Member(str(ULID()), "John Doe", None)
    print(member.id)
    print(member.name)
    # print(member.agent)