# 대학 과제 관리 웹앱

Python + Streamlit + SQLite 기반의 8개 과목 과제 관리 웹앱입니다.

## 기능
- 과목별 과제 등록 / 수정 / 삭제
- 마감일 및 D-day 표시
- 예상 소요시간(분) 기록
- 완료 체크 및 상태 필터
- 과목별 필터, 마감일 순 정렬
- 아이패드 Safari에 맞춘 반응형 레이아웃

## Windows 실행
1. Python 3.10 이상 설치
2. 프로젝트 폴더에서 PowerShell 실행
3. 다음 명령 입력

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

## iPad Safari에서 사용하기
아이패드 단독으로 Python 서버를 상시 실행하는 대신, PC 또는 클라우드에 앱을 실행한 뒤 Safari로 접속하세요.

**같은 Wi-Fi의 Windows PC에서 접속:**
```powershell
streamlit run app.py --server.address 0.0.0.0
```
PC의 로컬 IP 주소를 확인하고 아이패드에서 `http://PC_IP:8501`로 접속합니다. Windows 방화벽에서 개인 네트워크 접근을 허용해야 할 수 있습니다. 외부 인터넷에 포트를 직접 공개하지 마세요.

**클라우드 배포:** GitHub에 프로젝트를 올린 후 Streamlit Community Cloud에서 `app.py`를 지정해 배포할 수 있습니다. 다만 Community Cloud의 로컬 SQLite 저장소는 영구 보존을 보장하지 않습니다. 장기 사용 시 외부 데이터베이스(Supabase 등)를 연동하세요.

## 테스트
```powershell
python -m unittest discover -s tests -v
python -m py_compile app.py storage.py
```

## 데이터 보관
PC에서 실행하면 `data/tasks.db`에 저장됩니다. 이 파일을 정기적으로 백업하세요. 개인용 로컬 앱을 전제로 설계되었으며 사용자 로그인 기능은 없습니다.
