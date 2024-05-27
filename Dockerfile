# 기반이 될 이미지 선택
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 호스트의 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사
COPY . .

# 필요한 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt


# config.json 파일을 /app 디렉토리로 복사
COPY config.json /app/config.json

# 환경 변수 설정
ENV CONFIG_PATH="/app/config.json"

# 컨테이너 실행 시 실행할 명령 설정
CMD ["python", "main.py"]
