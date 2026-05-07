"""エージェントの抽象クラスを定義するモジュール"""

from abc import ABC, abstractmethod
from collections.abc import Generator

from mnemos.protocols.event import AgentEvent
from mnemos.protocols.message import Message


class Agent(ABC):
    """エージェントの抽象クラス"""

    @abstractmethod
    def invoke(self, message: Message, thread_id: str) -> Message:
        """エージェントを呼び出す関数"""
        ...

    @abstractmethod
    def stream(self, message: Message, thread_id: str) -> Generator[AgentEvent]:
        """エージェントをストリーミングモードで呼び出す関数"""
        ...
