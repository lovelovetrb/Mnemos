from collections.abc import Callable

import pytest
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from mnemos.adapter.langgraph_agent import LangGraphAgent
from mnemos.protocols import Message
from tests.fake import FakeLLM, fake_error_tool, fake_tool


@pytest.fixture
def setup_tool_use_mock_llm() -> Callable[[str], FakeLLM]:
    def _setup(tool_name: str) -> FakeLLM:
        return FakeLLM(
            responses=[
                AIMessage(
                    content="ツールが呼び出されました!",
                    tool_calls=[
                        {
                            "id": "call_1",
                            "name": tool_name,
                            "args": {},
                        }
                    ],
                ),
                AIMessage(content="こんにちは!"),
            ]
        )

    return _setup


def test_ok_response_from_langgraph_agent() -> None:
    expected_response = "こんにちは!"
    llm = FakeLLM(responses=[AIMessage(content=expected_response)])
    agent = LangGraphAgent(llm, checkpointer=InMemorySaver())
    agent_response = agent.invoke(
        Message(content="Hello, Agent!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response


def test_tool_called_by_langgraph_agent(setup_tool_use_mock_llm: Callable) -> None:
    expected_response = "こんにちは!"
    llm = setup_tool_use_mock_llm("fake_tool")
    agent = LangGraphAgent(llm, checkpointer=InMemorySaver(), tools=[fake_tool])
    agent_response = agent.invoke(
        Message(content="Call the tool!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response


def test_tool_called_invoke_error(setup_tool_use_mock_llm: Callable) -> None:
    expected_response = "こんにちは!"
    llm = setup_tool_use_mock_llm("fake_error_tool")
    agent = LangGraphAgent(llm, checkpointer=InMemorySaver(), tools=[fake_error_tool])
    agent_response = agent.invoke(
        Message(content="Call the tool!"), thread_id="test_thread"
    )
    assert agent_response.content == expected_response


def test_invalid_tool_name(setup_tool_use_mock_llm: Callable) -> None:
    llm = setup_tool_use_mock_llm("non_existent_tool")
    agent = LangGraphAgent(llm, checkpointer=InMemorySaver(), tools=[fake_tool])
    agent_response = agent.invoke(
        Message(content="Call the tool!"), thread_id="test_thread"
    )
    assert agent_response.content == "こんにちは!"


def test_system_prompt_is_passed_to_llm() -> None:
    system_prompt = "これはシステムプロンプトです。"
    human_message = "Hello, Agent!"
    expected_history_length = 2

    llm = FakeLLM(responses=[AIMessage(content="こんにちは!")])
    agent = LangGraphAgent(
        llm, checkpointer=InMemorySaver(), system_prompt=system_prompt
    )
    agent.invoke(Message(content=human_message), thread_id="test_thread")
    llm_recive_content = [history.content for history in llm.histories[-1]]

    assert llm_recive_content[0] == system_prompt
    assert llm_recive_content[1] == human_message
    assert len(llm_recive_content) == expected_history_length


def test_stream_yields_tool_call_and_response(
    setup_tool_use_mock_llm: Callable,
) -> None:
    llm = setup_tool_use_mock_llm("fake_tool")
    agent = LangGraphAgent(llm, checkpointer=InMemorySaver(), tools=[fake_tool])
    events = list(
        agent.stream(Message(content="Call the tool!"), thread_id="test_thread")
    )

    assert len(events) == 2  # noqa: PLR2004
    assert events[0].type == "tool_call_start"
    assert "fake_tool" in events[0].data
    assert events[1].type == "response"
    assert events[1].data == "こんにちは!"


def test_system_prompt_is_not_duplicated_in_history() -> None:
    system_prompt = "これはシステムプロンプトです。"
    human_message_1 = "Hello, Agent!"
    agent_resopnse_1 = "こんにちは!"
    human_message_2 = "こんにちは、エージェントさん!"
    expected_history_length = 4

    llm = FakeLLM(responses=[AIMessage(content=agent_resopnse_1)])
    agent = LangGraphAgent(
        llm, checkpointer=InMemorySaver(), system_prompt=system_prompt
    )
    agent.invoke(Message(content=human_message_1), thread_id="test_thread")
    agent.invoke(Message(content=human_message_2), thread_id="test_thread")
    llm_recive_content = [history.content for history in llm.histories[-1]]

    assert llm_recive_content[0] == system_prompt
    assert llm_recive_content[1] == human_message_1
    assert llm_recive_content[2] == agent_resopnse_1
    assert llm_recive_content[3] == human_message_2
    assert len(llm_recive_content) == expected_history_length
