"""Langgraphを用いたエージェントの具体実装"""

from typing import TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.state import END, START, CompiledStateGraph

from mnemos.protocols import Agent, Message


class MessagesState(TypedDict):
    """エージェントの状態を表すクラス"""

    messages: list[BaseMessage]


class LangGraphAgent(Agent):
    """Langgraphを用いたエージェントの具体実装"""

    def __init__(self, llm: BaseChatModel) -> None:
        """LanggraphAgentのコンストラクタ"""
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        state_graph = StateGraph(MessagesState)  # pyrefly: ignore[bad-specialization]
        state_graph.add_node("call_llm", self._call_llm)

        state_graph.add_edge(START, "call_llm")
        state_graph.add_edge("call_llm", END)
        return state_graph.compile(checkpointer=MemorySaver())

    def _call_llm(self, state: MessagesState) -> dict[str, list[AIMessage]]:
        """LLMを呼び出す関数"""
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    def invoke(self, message: Message, thread_id: str) -> Message:
        """メッセージを受け取り、それに対するレスポンスを生成する関数"""
        response = self.graph.invoke(
            {"messages": [HumanMessage(content=message.content)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        last_message = response["messages"][-1]
        return Message(content=last_message.content)
