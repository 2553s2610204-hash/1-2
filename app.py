import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌", layout="centered")
st.title("💌 달콤살벌 연애상담소")
st.caption("연애 고민이 있나요? Gemini가 진심을 다해 들어드릴게요. (비밀 보장!)")

# 2. Streamlit Secrets API 키 설정 및 예외 처리
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("🔑 API 키를 찾을 수 없습니다. Streamlit Cloud의 Secrets 설정을 확인해주세요.")
    st.stop()

# 3. 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "안녕하세요! 당신의 연애 고민 상담사 Gemini입니다. 짝사랑, 이별, 썸 등 무슨 고민이든 편하게 말씀해주세요. 💕"
        }
    ]

# 4. 이전 채팅 기록 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 처리
if user_input := st.chat_input("고민을 이야기해주세요..."):
    # 사용자 메시지 화면 표시 및 저장
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6. Gemini API 호출 및 답변 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("답변을 생각 중이에요... 💭"):
                # 모델 설정 (gemini-2.5-flash-lite)
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash-lite",
                    system_instruction=(
                        "당신은 공감 능력이 뛰어나고 다정한 연애 상담사입니다. "
                        "사용자의 연애 고민을 경청하고, 따뜻하면서도 현실적인 조언을 해주세요. "
                        "이모지를 적절히 섞어서 친근한 말투로 답변해주세요."
                    )
                )
                
                # 이전 대화 맥락 가공 (user / model 구조 맞춤)
                history = []
                for msg in st.session_state.messages[:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [msg["content"]]})
                
                # 대화 시작 및 답변 요청
                chat = model.start_chat(history=history)
                response = chat.send_message(user_input)
                
                ai_response = response.text
                message_placeholder.markdown(ai_response)
                
                # AI 메시지 저장
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
        except Exception as e:
            message_placeholder.error(f"❌ 답변을 가져오는 중 오류가 발생했습니다: {e}")
