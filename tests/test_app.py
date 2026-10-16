"""실제 API 요청 없이 채팅 UI와 오류 복구를 검증한다."""

import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
import openai
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


class ChatAppTests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(APP), default_timeout=45)
        app.secrets["OPENAI_API_KEY"] = "test-key-not-real"
        return app.run()

    def test_missing_key(self):
        app = AppTest.from_file(str(APP), default_timeout=15)
        app.secrets["OPENAI_API_KEY"] = ""
        app.run()
        self.assertFalse(app.exception)
        self.assertTrue(app.info)
        self.assertTrue(app.chat_input[0].disabled)

    @patch("openai.OpenAI")
    def test_stream_history_and_reset(self, factory):
        client = factory.return_value.__enter__.return_value
        client.chat.completions.create.return_value.__enter__.side_effect = (
            lambda: iter(["안녕하세요", "! 무엇을 도와드릴까요?"])
        )
        app = self.app()
        app.chat_input[0].set_value("안녕").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state.messages), 2)
        self.assertEqual(app.session_state.messages[-1]["content"], "안녕하세요! 무엇을 도와드릴까요?")
        app.chat_input[0].set_value("이전 질문 기억해?").run()
        call = client.chat.completions.create.call_args.kwargs
        self.assertEqual(call["model"], "gpt-4o-mini")
        self.assertEqual([m["role"] for m in call["messages"]], ["system", "user", "assistant", "user"])
        app.sidebar.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state.messages, [])

    @patch("openai.OpenAI")
    def test_failed_request_only_retries_on_click(self, factory):
        client = factory.return_value.__enter__.return_value
        client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        )
        app = self.app()
        app.chat_input[0].set_value("질문").run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertTrue(app.chat_input[0].disabled)
        self.assertEqual(client.chat.completions.create.call_count, 1)
        app.run()
        self.assertEqual(client.chat.completions.create.call_count, 1)
        client.chat.completions.create.side_effect = None
        client.chat.completions.create.return_value.__enter__.return_value = iter(["복구된 답변"])
        next(b for b in app.button if b.label == "답변 다시 받기").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.session_state.messages[-1]["content"], "복구된 답변")
        self.assertFalse(app.chat_input[0].disabled)


if __name__ == "__main__":
    unittest.main()
