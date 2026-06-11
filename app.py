import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌", layout="centered")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민이 있나요? Gemini가 진심을 다해 들어드릴게요. (비밀 보장!)")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
try:
    # Streamlit Cloud 배포 환경 또는 로컬 .streamlit/secrets.toml 대처
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        st.error("🔑 API 키를 찾을 수 없습니다. Streamlit Secrets 설정을 확인해주세요.")
        st.stop()
        
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"설정 오류가 발생했습니다: {e}")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "안녕하세요! 당신의 연애 고민 상담사 Gemini입니다. 짝사랑, 이별, 썸 등 무슨 고민이든 편하게 말씀해주세요. 💕"
        }
    ]

# 4. 이전 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("고민을 이야기해주세요..."):
    # 사용자가 입력한 메시지를 화면에 표시 및 저장
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6. Gemini 모델을 통한 답변 생성 (오류 처리 포함)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("답변을 생각 중이에요... 💭"):
                # 최신 gemini-2.5-flash-lite 모델 설정
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=(
                        "당신은 공감 능력이 뛰어나고 다정한 연애 상담사입니다. "
                        "사용자의 연애 고민을 경청하고, 따뜻하면서도 현실적인 조언을 해주세요. "
                        "이모지를 적절히 섞어서 친근한 말투로 답변해주세요."
                    )
                )
                
                # 대화 맥락을 유지하기 위해 전체 대화 기록을 모델에 전달할 수 있는 형태로 변환
                # (Gemini API의 대화 형식에 맞춤: user / model)
                history = []
                for msg in st.session_state.messages[:-1]: # 현재 입력 직전까지의 기록
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [msg["content"]]})
                
                # 멀티턴 대화 시작
                chat = model.start_chat(history=history)
                response = chat.send_message(user_input)
                
                # 답변 출력
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                
                # 대화 기록에 추가
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
        except genai.types.generation_types.BlockedPromptException:
            message_placeholder.error("⚠️ 안전 정책에 위배되는 내용이 포함되어 답변을 생성할 수 없습니다.")
        except Exception as e:
            message_placeholder.error(f"❌ 오류가 발생했습니다: {e}\n잠시 후 다시 시도해주세요.")
