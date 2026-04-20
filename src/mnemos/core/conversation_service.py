"""会話に関する処理を行うクラス"""

from mnemos.protocols import Agent, Message


class ConversationService:
    """会話に関する処理を行うクラス"""

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    def handle_message(self, message: str, thread_id: str) -> str:
        """ユーザーから受け取ったメッセージを処理する関数"""
        response = self.agent.invoke(
            message=Message(content=message),
            thread_id=thread_id,
        )
        return response.content
