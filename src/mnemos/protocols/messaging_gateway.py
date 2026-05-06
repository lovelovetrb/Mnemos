"""外部メッセージングプラットフォームとの橋渡しを行う抽象クラスを定義するモジュール"""

from abc import ABC, abstractmethod


class MessagingGateway(ABC):
    """外部メッセージングプラットフォームとの橋渡しを行う抽象クラス"""

    @abstractmethod
    async def start(self) -> None:
        """プラットフォームへの接続を開始し、メッセージの待ち受けを始める"""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """待ち受けを停止してプラットフォームとの接続を切断する"""
        ...

    @abstractmethod
    async def handle_message(self, message: str, thread_id: str) -> str:
        """メッセージを受信して応答を返す"""
        ...
