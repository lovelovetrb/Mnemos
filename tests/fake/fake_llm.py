from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel


class FakeLLM(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self  # 何もせず自分自身を返す
