from http.server import BaseHTTPRequestHandler
import json
import os
from openai import OpenAI
from PyPDF2 import PdfReader
from io import BytesIO

def analyze_pdf(pdf_data):
    try:
        # PDF 읽기
        pdf = PdfReader(BytesIO(pdf_data))
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # ChatCompletion 요청
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "이력서를 분석하여 주요 경력과 기술을 요약해주세요."},
                {"role": "user", "content": text}
            ]
        )
        
        # 응답에서 텍스트 추출
        return response.choices[0].message.content

    except Exception as e:
        print(f"PDF 분석 중 에러: {str(e)}")
        raise e

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # CORS 헤더
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # PDF 분석
            result = analyze_pdf(post_data)
            
            # 응답 전송
            self.wfile.write(json.dumps({
                'result': result
            }).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 