from mnemos.protocols import Agent, Message


class FakeAgent(Agent):
    def __init__(self, response: str) -> None:
        self.response = response
        self.received_message: Message | None = None
        self.received_thread_id: str | None = None

    def invoke(self, message: Message, thread_id: str) -> Message:
        self.received_message = message
        self.received_thread_id = thread_id
        return Message(content=self.response)
