"""エージェントのストリーミングイベントを定義するモジュール"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentEvent:
    """エージェントの処理中に発生するイベント"""

    type: str
    data: str = ""
