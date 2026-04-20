"""LLMに関する抽象クラスを定義する"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLMに関する振る舞いを定義する抽象クラス"""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """メッセージを受け取り、それに対するレスポンスを生成する関数"""
