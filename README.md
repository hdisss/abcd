# Mini Chat

OpenAI API의 `gpt-4o-mini`를 사용하는 한국어 Streamlit 챗봇입니다.

## Streamlit Community Cloud 배포

1. 이 프로젝트를 GitHub 저장소에 올립니다. `.venv`, `.deps`, 실제 API 키는 올리지 마세요.
2. Streamlit Community Cloud에서 **Create app**으로 저장소를 선택합니다.
3. 실행 파일(Main file path)은 `app.py`, Python 버전은 **3.12**로 지정합니다.
4. **Advanced settings → Secrets**에 다음 값을 입력한 뒤 배포합니다. 이미 배포했다면 앱의 **Settings → Secrets**에서 설정할 수 있습니다.

```toml
OPENAI_API_KEY = "실제 OpenAI API 키"
```

키는 `st.secrets["OPENAI_API_KEY"]`에서 읽습니다. 코드에 넣거나 저장소에 커밋할 필요가 없습니다. 키가 없으면 설정 안내 화면이 표시됩니다.

## 로컬 실행 (선택)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml에 실제 키를 입력한 후 실행
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## 동작

- 답변을 실시간으로 출력하고 현재 세션에서 대화 기록을 유지합니다.
- 최근 10개의 완성된 대화와 현재 질문을 API에 전송합니다.
- 질문은 최대 4,000자, 답변은 최대 2,048토큰으로 제한합니다.
- 새 대화를 시작하면 기록을 초기화합니다.
- 인증, 사용 한도, 연결 오류를 안내하고 실패한 질문을 다시 시도하거나 취소할 수 있습니다.
- 대화는 별도 데이터베이스에 저장하지 않습니다. 새로고침이나 세션 종료 시 초기화될 수 있습니다.
- 방문자의 질문과 최근 대화 내용은 답변 생성을 위해 OpenAI API로 전송됩니다.
- 공개 앱의 요청은 등록된 API 키로 처리되어 해당 OpenAI 계정에 비용이 발생합니다.

## 공식 문서

- [OpenAI GPT-4o mini](https://developers.openai.com/api/docs/models/gpt-4o-mini)
- [Streamlit 챗봇 튜토리얼](https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps)
- [Community Cloud Secrets 설정](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
