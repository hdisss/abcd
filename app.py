"""Streamlit Community Cloud용 GPT-4o mini 챗봇."""

import openai
import streamlit as st


MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = (
    "당신은 친절하고 유능한 AI 도우미입니다. 사용자가 다른 언어를 요청하지 않으면 "
    "한국어로 답변하세요. 질문의 의도를 파악해 명확하고 실용적으로 답하고, "
    "모르는 내용은 추측을 사실처럼 말하지 마세요. 필요하면 Markdown을 사용하세요."
)

st.set_page_config(page_title="Mini Chat · AI 챗봇", page_icon="💬", layout="centered")


def read_api_key():
    """키가 없어도 앱이 열리도록 설정 누락을 처리한다."""
    try:
        value = st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None
    return value.strip() if isinstance(value, str) and value.strip() else None


def clear_chat():
    st.session_state.messages = []
    st.session_state.pop("chat_error", None)


if "messages" not in st.session_state:
    st.session_state.messages = []

api_key = read_api_key()
messages = st.session_state.messages

with st.sidebar:
    st.title("💬 Mini Chat")
    st.caption("생각을 정리하고, 새로운 답을 찾아보세요.")
    st.divider()
    st.markdown("**사용 모델**")
    st.code(MODEL, language=None)
    st.button("새 대화 시작", icon=":material/add:", on_click=clear_chat, width="stretch")
    st.divider()
    st.caption("현재 세션에서 대화가 유지됩니다. 새로고침하면 초기화될 수 있습니다.")
    st.caption("답변에는 최근 10회 대화를 참고합니다.")

st.caption("YOUR EVERYDAY AI ASSISTANT")
st.title("무엇을 도와드릴까요?")
st.write("글쓰기부터 코딩, 일상 속 궁금한 점까지 편하게 이야기해 보세요.")
st.caption("GPT-4o mini · 실시간 답변 · 한국어 대화")
st.divider()

if not api_key:
    st.info("챗봇을 시작하려면 앱 관리자가 OpenAI API 키를 설정해 주세요.")
    with st.expander("Streamlit Community Cloud 설정 방법", expanded=True):
        st.markdown("앱의 **Settings → Secrets**에 아래 항목을 저장하세요.")
        st.code('OPENAI_API_KEY = "여기에 실제 API 키를 입력하세요"', language="toml")
        st.caption("API 키는 서버의 Secrets에서만 읽습니다.")
    st.chat_input("API 키 설정 후 대화를 시작할 수 있어요", disabled=True)
    st.stop()

if not messages:
    with st.container(border=True):
        st.markdown("**이렇게 시작해 보세요**")
        st.markdown("💡 복잡한 개념을 쉬운 예시로 설명해 줘\n\n✍️ 정중한 업무 이메일을 작성해 줘\n\n💻 파이썬 학습 계획을 세워 줘")

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 실패한 질문은 보존하며, 버튼을 누른 경우에만 다시 API를 호출한다.
pending = bool(messages and messages[-1]["role"] == "user")
retry = False
if pending:
    st.error(st.session_state.get("chat_error", "답변을 완료하지 못했습니다. 다시 시도해 주세요."))
    left, right = st.columns(2)
    retry = left.button("답변 다시 받기", width="stretch")
    if right.button("마지막 질문 취소", width="stretch"):
        messages.pop()
        st.session_state.pop("chat_error", None)
        st.rerun()

prompt = st.chat_input("메시지를 입력하세요", max_chars=4000, disabled=pending)
if prompt and prompt.strip():
    messages.append({"role": "user", "content": prompt.strip()})
    with st.chat_message("user"):
        st.markdown(prompt.strip())

if (prompt and prompt.strip()) or retry:
    st.session_state.pop("chat_error", None)
    try:
        with st.chat_message("assistant"):
            # 마지막 질문 + 최근 10개 완성된 대화 쌍. 세션별 기록만 전송한다.
            context = messages[-21:]
            with openai.OpenAI(api_key=api_key, timeout=60.0, max_retries=0) as client:
                with client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}, *context],
                    max_completion_tokens=2048,
                    stream=True,
                ) as stream:
                    response = st.write_stream(stream)
        if not isinstance(response, str) or not response.strip():
            st.session_state.chat_error = "빈 답변이 도착했습니다. 다시 시도해 주세요."
        else:
            messages.append({"role": "assistant", "content": response})
    except openai.AuthenticationError:
        st.session_state.chat_error = "API 인증에 실패했습니다. 관리자는 Secrets의 API 키를 확인해 주세요."
    except openai.RateLimitError:
        st.session_state.chat_error = "API 사용 한도에 도달했습니다. 잠시 후 재시도하거나 관리자가 잔액과 사용 한도를 확인해 주세요."
    except (openai.APITimeoutError, openai.APIConnectionError):
        st.session_state.chat_error = "서버 연결이 지연되거나 끊어졌습니다. 잠시 후 다시 시도해 주세요."
    except openai.OpenAIError:
        st.session_state.chat_error = "답변을 받지 못했습니다. 다시 시도하고, 문제가 계속되면 관리자가 모델 접근 권한과 API 설정을 확인해 주세요."
    st.rerun()

st.caption("AI 답변은 부정확할 수 있습니다. 중요한 내용은 확인해 주세요.")
