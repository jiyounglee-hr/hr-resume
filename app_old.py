import streamlit as st
import streamlit.web.cli as stcli
import sys
import PyPDF2
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import math
from resume_analysis import show_resume_analysis
from salary_negotiation import show_salary_negotiation

# 환경 변수 로드
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 세션 상태 초기화
if 'analysis_result' not in st.session_state:
    st.session_state['analysis_result'] = None
if 'interview_questions' not in st.session_state:
    st.session_state['interview_questions'] = None
if 'job_description' not in st.session_state:
    st.session_state['job_description'] = None

# 페이지 설정
st.set_page_config(page_title="HR-채용", layout="wide")

# 사이드바 스타일 수정 (기존 스타일 부분 교체)
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 520px !important;
            max-width: 520px !important;
            background-color: #f8f9fa;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 2rem;
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }
    </style>
""", unsafe_allow_html=True)

# 사이드바 내용
with st.sidebar:
    st.image("https://neurophethr.notion.site/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fe3948c44-a232-43dd-9c54-c4142a1b670b%2Fneruophet_logo.png?table=block&id=893029a6-2091-4dd3-872b-4b7cd8f94384&spaceId=9453ab34-9a3e-45a8-a6b2-ec7f1cefbd7f&width=410&userId=&cache=v2", 
             width=120)
    
    st.markdown("<div class='sidebar-title'>HR-채용</div>", unsafe_allow_html=True)
    
    # 1. 이력서 첨부 섹션
    st.markdown("""
        <h4 style='color: #333333; margin-bottom: 20px;'>
            이력서 분석 및 면접 질문 TIP
        </h4>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "이력서(PDF 파일)를 선택해주세요",
        type=['pdf'],
        help="200MB 이하의 PDF 파일만 가능합니다"
    )
    
    if uploaded_file:
        st.markdown(f"<div style='padding: 5px 0px; color: #666666;'>{uploaded_file.name}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='upload-text'>Drag and drop file here<br>Limit 200MB per file • PDF</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 처우협상 메뉴 추가
    if st.button("💰 처우협상"):
        st.session_state.current_page = "salary"
    
    st.markdown("<br>", unsafe_allow_html=True)

# 메인 영역에 페이지 라우팅 추가
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"

if st.session_state.current_page == "salary":
    from salary_negotiation import show_salary_negotiation
    show_salary_negotiation()
else:
    # 기존의 메인 페이지 코드는 그대로 유지
    st.markdown("""
        <h3 style='text-align: left; color: #333333; margin-bottom: 30px;'>
            이력서 분석 및 면접 질문 TIP
        </h3>
    """, unsafe_allow_html=True)

    # 채용공고 데이터
    job_descriptions = {
        "ra_manager": """[의료기기 인허가(RA) 팀장]

담당업무
- 국내외 의료기기 인허가 (MFDS, FDA, CE, MHLW 등) 및 사후관리
- 국가별 기술문서 작성 및 최신화
- 국가별 의료기기 규제 요구사항 분석
- 의료기기법/규격/가이던스 변경사항 모니터링
- 품질시스템 심사 대응 (ISO 13485, KGMP, MDSAP 등)

필수자격
- 제품 인허가 업무경력 7년이상
- 의료기기 인증팀 관리 경험
- SaMD, SiMD, 전기전자 의료기기 인허가 경험
- 영어 중급 이상 (Reading & Writing 필수)

우대사항
- 3등급 SW 의료기기 허가 경험
- 의료기기 개발 프로세스에 대한 이해
- 의료기기 RA(의료기기 규제과학 전문가) 자격증 소지자""",
        
        "marketing": """[의료 AI 솔루션 마케팅(3~6년)]

담당업무
- 의료 AI 솔루션 마케팅 전략 수립 및 실행
- 제품 포지셔닝 및 가치 제안
- 디지털 마케팅 캠페인 기획 및 실행
- 마케팅 성과 분석 및 보고

필수자격
- 의료기기/헬스케어 마케팅 경력 3년 이상
- 디지털 마케팅 전략 수립 및 실행 경험
- 데이터 기반 마케팅 성과 분석 능력

우대사항
- AI/의료 분야 이해도 보유
- 글로벌 마케팅 경험
- 의료진 대상 마케팅 경험""",
        
        "japan_head": """[일본 법인장]

담당업무
- 일본 법인 총괄 및 운영 관리
- 일본 시장 사업 전략 수립 및 실행
- 현지 영업/마케팅 조직 구축 및 관리
- 일본 시장 매출 및 수익성 관리

필수자격
- 일본 의료기기 시장 경력 10년 이상
- 의료기기 기업 임원급 경험 보유
- 일본어 비즈니스 레벨 이상

우대사항
- AI 의료기기 관련 경험
- 일본 의료기기 인허가 경험
- 글로벌 기업 경영 경험"""
    }

    # 1. 채용요건 섹션
    st.markdown("""
        <h4 style='color: #333333; margin-bottom: 20px;'>
            1. 채용요건
        </h4>
    """, unsafe_allow_html=True)
    job_option = st.selectbox(
        "채용공고 선택",
        ["선택해주세요", "의료기기 인허가(RA) 팀장", "의료 AI 솔루션 마케팅", "일본 법인장", "직접 입력"]
    )

    if job_option == "직접 입력":
        job_description = st.text_area("채용공고 내용을 입력해주세요", height=300)
    else:
        job_map = {
            "의료기기 인허가(RA) 팀장": "ra_manager",
            "의료 AI 솔루션 마케팅": "marketing",
            "일본 법인장": "japan_head"
        }
        if job_option in job_map:
            # 기본값으로 기존 내용을 보여주고, 수정 가능하도록 설정
            default_description = job_descriptions[job_map[job_option]]
            job_description = st.text_area(
                "채용공고 내용 (필요시 수정 가능합니다)",
                value=default_description,
                height=500
            )
        else:
            job_description = ""

    # 2. 이력서 분석 섹션 수정
    st.markdown("""
        <h4 style='color: #333333; margin-bottom: 20px;'>
            2. 이력서 분석
        </h4>
    """, unsafe_allow_html=True)

    # 버튼을 왼쪽에 배치하고 스타일 적용
    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_button = st.button(
            "분석 시작하기",
            key="analyze_button",
            help="이력서와 채용공고를 분석합니다"
        )

    # 분석 로직
    if analyze_button:
        if uploaded_file is not None and job_description:
            with st.spinner("이력서를 분석중입니다..."):
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": """당신은 전문 채용 담당자입니다. 
다음 형식에 맞춰 이력서를 분석해주세요:

(1) 핵심 경력 요약
- 총 경력 기간: [총 경력 연월]
- 주요 직무 경험:
1) [최근 회사명]: [직위/직책]
2) [이전 회사명]: [직위/직책]
3) [이전 회사명]: [직위/직책]
- 주요 업무 내용: [핵심 업무 내용 요약]

(2) 채용요건 연관성 분석
- 부합되는 요건: [채용공고의 요건 중 이력서에서 확인된 항목들]
- 미확인/부족 요건: [채용공고의 요건 중 이력서에서 확인되지 않거나 부족한 항목들]"""},
                            {"role": "user", "content": f"다음은 이력서 내용입니다:\n\n{text}\n\n다음은 채용공고입니다:\n\n{job_description}\n\n위 형식에 맞춰 이력서를 분석해주세요."}
                        ]
                    )
                    st.session_state.analysis_result = response.choices[0].message.content
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("이력서 파일과 채용공고를 모두 입력해주세요.")

    # 분석 결과를 구분선으로 분리하여 표시
    if st.session_state.analysis_result:
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        st.text_area("분석 결과", st.session_state.analysis_result, height=350)
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. 면접 질문 섹션
    st.markdown("""
        <h4 style='color: #333333; margin: 30px 0 20px 0;'>
            3. 면접 질문 TIP
        </h4>
    """, unsafe_allow_html=True)

    st.markdown("""
        <small style='color: #666666;'>
            1~6번은 직무기반의 경험, 프로젝트, 문제해결, 자격요건 관련 사례 질문<br>
            7~10번은 핵심가치 기반의 '[도전]두려워 말고 시도합니다, [책임감]대충은 없습니다, [협력]동료와 협업합니다, [전문성]능동적으로 일합니다'와 관련된 사례 질문
        </small>
    """, unsafe_allow_html=True)

    # 질문 추출 버튼을 왼쪽에 배치
    col3, col4 = st.columns([1, 4])
    with col3:
        question_button = st.button(
            "질문 추출하기",
            key="question_button",
            help="분석 결과를 바탕으로 면접 질문을 생성합니다"
        )

    # 질문 생성 로직 부분 수정
    if question_button:
        if st.session_state.analysis_result and st.session_state.analysis_result != "":
            with st.spinner("면접 질문을 생성중입니다..."):
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": """당신은 경험 많은 면접관입니다. 
다음 형식에 맞춰 10개의 면접 질문을 생성해주세요:

[직무 관련 질문 1-6번]
- 경력과 프로젝트 경험
- 문제 해결 사례
- 자격요건 충족 여부
- 전문성 검증
각 질문은 구체적인 경험과 상황, 역할, 결과를 물어보는 방식으로 작성

[핵심가치 관련 질문 7-10번]
7번: [도전] 새로운 시도나 혁신 경험
8번: [책임감] 책임감 있는 업무 수행 사례
9번: [협력] 팀워크와 협업 경험
10번: [전문성] 전문성 발휘 사례

각 질문은 다음 형식으로 작성:
1. [구체적인 상황/경험에 대한 질문] + [역할과 결과에 대한 추가 질문]"""},
                            {"role": "user", "content": f"이력서 분석 결과:\n{st.session_state.analysis_result}\n\n채용공고:\n{job_description}\n\n위 내용을 바탕으로 상세한 면접 질문 10개를 생성해주세요."}
                        ]
                    )
                    st.session_state.interview_questions = response.choices[0].message.content
                except Exception as e:
                    st.error(f"질문 생성 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("먼저 이력서 분석을 진행해주세요.")

    # 면접 질문 결과를 구분선으로 분리하여 표시
    if st.session_state.interview_questions:
        st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
        st.text_area("면접 질문", st.session_state.interview_questions, height=450)
        st.markdown("</div>", unsafe_allow_html=True)

    # 기존의 메인 페이지 코드는 그대로 유지
    # ... 

def show_resume_analysis():
    st.markdown("## 📄 이력서 분석 및 면접 질문 TIP")
    # 이력서 분석 관련 코드...

def show_salary_negotiation():
    st.markdown("## 💰 처우협상 분석")
    
    try:
        # 엑셀 파일 직접 로드
        df = pd.read_excel("salary_table.xlsx")
        
        # 직군 매핑 정의
        job_mapping = {
            "연구직": "직군1",
            "개발직": "직군2",
            "임상연구, QA": "직군2",
            "연구기획": "직군3",
            "디자인": "직군3",
            "인증(RA), SV, SCM": "직군3",
            "마케팅": "직군3",
            "기획": "직군3",
            "기술영업 / SE(5년 이상)": "직군3",
            "경영기획(전략,회계,인사,재무,법무,보안)": "직군3",
            "지원(연구, 기술, 경영 지원 등)": "직군4",
            "일반영업 /SE(5년 미만)": "직군4",
            "고객지원(CS)": "직군5",
            "레이블링": "직군5"
        }
        
        # 직군 상세 목록
        job_roles = list(job_mapping.keys())
        
        # 입력 폼 생성
        with st.form("salary_form"):
            # 1줄: 포지션명, 후보자명
            col1, col2 = st.columns(2)
            with col1:
                position = st.text_input("포지션명", "")
            with col2:
                candidate_name = st.text_input("후보자명", "")
            
            # 2줄: 직군선택
            job_role = st.selectbox("직군 선택", job_roles)
            
            # 3줄: 현재연봉, 기타 처우, 희망연봉
            col3, col4, col5 = st.columns(3)
            with col3:
                current_salary = st.number_input("현재연봉 (만원)", min_value=0, step=100)
            with col4:
                other_salary = st.number_input("기타 처우 (만원)", min_value=0, step=100)
            with col5:
                desired_salary = st.number_input("희망연봉 (만원)", min_value=0, step=100)
            
            # 4줄: 인정경력 연차, 학력특이사항
            col6, col7 = st.columns(2)
            with col6:
                years = st.number_input("인정경력 (년)", min_value=0.0, step=0.1, format="%.1f")
            with col7:
                education_notes = st.text_input("학력특이사항", "")
            
            # 5줄: 특이사항
            special_notes = st.text_area("특이사항 (성과, 스킬, 기타)", height=100)
            
            # 분석하기 버튼
            submitted = st.form_submit_button("분석하기")

            if submitted:
                # ... (기존 처우협상 분석 코드) ...

# 메인 함수 정의
def main():
    st.sidebar.title("HR-채용")

    # 페이지 초기화
    if "page" not in st.session_state:
        st.session_state.page = "resume"

    # 네비게이션 버튼
    if st.session_state.page == "salary":
        if st.sidebar.button("📄 이력서 분석 및 면접 질문 TIP"):
            st.session_state.page = "resume"
            st.rerun()
    else:
        if st.sidebar.button("💰 처우협상"):
            st.session_state.page = "salary"
            st.rerun()

    # 페이지 라우팅
    if st.session_state.page == "resume":
        show_resume_analysis()
    else:
        show_salary_negotiation()

# 메인 함수 실행
main() 