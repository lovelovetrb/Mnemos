from langchain.tools import tool


@tool
def fake_tool() -> str:
    """テスト用のツール定義。挨拶をしてくれる"""
    return "Hello!"


@tool
def fake_error_tool() -> str:
    """テスト用のツール定義。エラーを発生させる"""
    raise Exception("This is a fake error from the tool.")  # noqa: EM101,TRY002,TRY003
