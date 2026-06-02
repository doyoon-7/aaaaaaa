import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💖", layout="centered")
st.title("💖 달콤살벌 연애상담소")
st.caption("gemini-2.5-flash-lite 모델을 탑재한 AI 연애 컨설턴트입니다. 당신의 고민을 들려주세요!")

# 2. Streamlit Secrets에서 API 키 불러오기 및 검증
if "GEMINI_API_KEY" not in st.secrets:
    st.error("⚠️ Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. 패널에서 키를 추가해주세요.")
    st.stop()

# Gemini API 설정
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. 챗봇의 페르소나(System Instruction) 설정
SYSTEM_INSTRUCTION = (
    "당신은 따뜻하고 공감 능력이 뛰어나면서도, 때로는 뼛속 깊이 현실적인 조언을 건네는 베테랑 연애 상담가입니다. "
    "사용자의 고민을 진지하게 경청하고 위로해 주되, 필요한 경우 객관적인 팩트 폭행(위트 있는 유머 섞인 조언)도 마다하지 마세요. "
    "친근한 말투(반말과 존댓말 중 적절한 톤앤매너 유지, 여기서는 다정한 존댓말 권장)로 답변해주세요."
)

# 4. 세션 상태(Session State)를 이용한 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. 기존 채팅 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 6. 사용자 입력 및 챗봇 응답 처리
if prompt := st.chat_input("ex) 썸남이 선톡을 안 하는데 마음이 없는 걸까요?"):
    # 사용자의 메시지를 화면에 출력 및 기록 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 챗봇 응답 생성 영역
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 모델 설정 (요청하신 gemini-2.5-flash-lite 사용)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            # 과거 대화 기록을 Gemini API 형식에 맞게 변환 (user -> user, assistant -> model)
            gemini_history = []
            for msg in st.session_state.messages[:-1]: # 마지막 입력 제외한 이전 기록들
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
            
            # 대화 세션 시작 및 메시지 전송
            chat = model.start_chat(history=gemini_history)
            
            with st.spinner("연애 고수의 답변을 생성 중입니다... 💬"):
                response = chat.send_message(prompt)
                full_response = response.text
            
            # 결과 출력 및 기록 저장
            message_placeholder.write(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # API 오류, 네트워크 할당량 초과 등 예외 처리
            error_msg = f"❌ 오류가 발생했습니다. 잠시 후 다시 시도해주세요.\n(에러 내용: {str(e)})"
            message_placeholder.write(error_msg)
