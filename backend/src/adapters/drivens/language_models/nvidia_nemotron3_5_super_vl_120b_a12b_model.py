from ports import AiModelPort


class Nemotron3_5SuperVL120bA12b(AiModelPort):
    codename = "nvidia/nemotron-3.5-super-vl-120b-a12b"

    def __init__(self):
        self.codename = "nvidia/nemotron-3.5-super-vl-120b-a12b"

        self.name = "Nemotron"
        self.version = "3.5"
        self.params = "120b"