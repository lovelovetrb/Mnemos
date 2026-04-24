import builtins
from collections.abc import Callable, Sequence
from typing import Any

from langchain_core.language_models.base import LanguageModelInput
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool


class FakeLLM(FakeMessagesListChatModel):
    def bind_tools(
        self,
        tools: Sequence[builtins.dict[str, Any] | type | Callable | BaseTool],  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002, ANN401
    ) -> Runnable[LanguageModelInput, AIMessage]:
        return self  # 何もせず自分自身を返す
