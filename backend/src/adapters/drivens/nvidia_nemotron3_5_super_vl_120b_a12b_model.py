from ports.drivens.ai_model_port import AiModelPort


class Nemotron3_5SuperVL120bA12b(AiModelPort):
    codename = "nemotron3_5_super_vl_120b_a12b"

    def __init__(self):
        self.codename = "nemotron3_5_super_vl_120b_a12b"

        self.name = "Nemotron"
        self.version = "3.5"
        self.params = "120b"