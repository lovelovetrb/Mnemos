"""Langgraphを用いたエージェントの具体実装"""

from collections.abc import Generator
from typing import TYPE_CHECKING, Annotated, Any, TypedDict

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph, add_messages
from langgraph.graph.state import END, START, CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from mnemos.protocols import Agent, AgentEvent, Message

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable


class MessagesState(TypedDict):
    """エージェントの状態を表すクラス"""

    messages: Annotated[list[BaseMessage], add_messages]


class LangGraphAgent(Agent):
    """Langgraphを用いたエージェントの具体実装"""

    def __init__(
        self,
        llm: BaseChatModel,
        checkpointer: BaseCheckpointSaver,
        tools: list | None = None,
        system_prompt: str | None = None,
    ) -> None:
        """LanggraphAgentのコンストラクタ"""
        self.llm: Runnable = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.checkpointer = checkpointer
        if self.tools is not None:
            self.llm = llm.bind_tools(self.tools)
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        state_graph = StateGraph(MessagesState)  # pyrefly: ignore[bad-specialization]

        self._register_nodes(state_graph)
        self._register_edges(state_graph)

        return state_graph.compile(checkpointer=self.checkpointer)

    def _register_nodes(self, state_graph: StateGraph) -> None:
        state_graph.add_node("call_llm", self._call_llm)
        if self.tools:
            state_graph.add_node("tools", ToolNode(self.tools, handle_tool_errors=True))

    def _register_edges(self, state_graph: StateGraph) -> None:
        state_graph.add_edge(START, "call_llm")
        if self.tools:
            state_graph.add_conditional_edges("call_llm", tools_condition)
            state_graph.add_edge("tools", "call_llm")
        else:
            state_graph.add_edge("call_llm", END)

    def _call_llm(self, state: MessagesState) -> dict[str, list[AIMessage]]:
        """LLMを呼び出す関数"""
        llm_input = state["messages"]
        if self.system_prompt:
            llm_input = [
                SystemMessage(self.system_prompt, id="system_message"),
                *llm_input,
            ]
        response = self.llm.invoke(llm_input)
        return {"messages": [response]}

    def invoke(self, message: Message, thread_id: str) -> Message:
        """メッセージを受け取り、それに対するレスポンスを生成する関数"""
        response = self.graph.invoke(
            {"messages": [HumanMessage(content=message.content)]},
            config={"configurable": {"thread_id": thread_id}},
        )
        last_message = response["messages"][-1]
        return Message(content=last_message.content)

    def stream(self, message: Message, thread_id: str) -> Generator[AgentEvent]:
        """メッセージを受け取り、処理中のイベントをストリーミングで返す関数"""
        config = {"configurable": {"thread_id": thread_id}}
        for chunk in self.graph.stream(
            {"messages": [HumanMessage(content=message.content)]},
            config=config,
            stream_mode="updates",
        ):
            yield from self._chunk_to_events(chunk)

    def _chunk_to_events(self, chunk: dict[str, Any]) -> Generator[AgentEvent]:
        """LangGraphのストリームチャンクをAgentEventに変換する"""
        if "call_llm" in chunk:
            ai_message: AIMessage = chunk["call_llm"]["messages"][0]
            if ai_message.tool_calls:
                for tool_call in ai_message.tool_calls:
                    yield AgentEvent(
                        type="tool_call_start",
                        data=f"{tool_call['name']}: {tool_call['args']}",
                    )
            elif ai_message.content:
                yield AgentEvent(type="response", data=str(ai_message.content))
