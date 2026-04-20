from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    """エージェントがやりとりするメッセージを表すクラス"""

    content: str
