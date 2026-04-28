import builtins
from collections.abc import Callable, Sequence
from typing import Any, override

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatResult
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from pydantic import PrivateAttr


class FakeLLM(FakeMessagesListChatModel):
    _histories: list[list[BaseMessage]] = PrivateAttr(default_factory=list)

    def __init__(self, responses: Sequence[AIMessage]) -> None:
        super().__init__(responses=responses)

    def bind_tools(
        self,
        tools: Sequence[builtins.dict[str, Any] | type | Callable | BaseTool],  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002, ANN401
    ) -> Runnable[LanguageModelInput, AIMessage]:
        return self  # 何もせず自分自身を返す

    @override
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        self._histories.append(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    @property
    def histories(self) -> list[list[BaseMessage]]:
        """LLMに渡された全てのメッセージの履歴を返す"""
        return self._histories
