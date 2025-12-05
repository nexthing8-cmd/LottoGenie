# LottoGenie

LottoGenie는 AI 기반 로또 당첨 번호 예측 시스템입니다. 과거 데이터를 수집하고 분석하여 당첨 확률이 높은 번호를 추천하며, 웹 대시보드와 자동화 스크립트를 통해 편리한 사용 환경을 제공합니다.

## 시스템 개요

LottoGenie는 다음과 같은 주요 컴포넌트로 구성되어 있습니다:

- **Collector**: 로또 공식 홈페이지 등에서 과거 당첨 번호 데이터를 수집합니다.
- **Analyst**: 수집된 데이터를 바탕으로 다양한 통계 기법(Hot/Cold 분석, 연속 번호 등)을 적용하여 다음 회차 번호를 예측합니다.
- **Auditor**: 예측된 번호와 실제 당첨 번호를 비교하여 예측 정확도를 검증합니다.
- **Web App**: 사용자가 예측 번호를 확인하고 과거 기록을 조회할 수 있는 웹 인터페이스를 제공합니다 (회원가입/로그인 포함).
- **Automation**: 매주 자동으로 데이터 수집, 결과 확인, 예측 생성을 수행하는 워크플로우를 지원합니다.

## 설치 방법

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd LottoGenie
   ```

2. **의존성 패키지 설치**
   Python 3.x 환경이 필요합니다.
   ```bash
   pip install -r requirements.txt
   ```

3. **환경 설정 (.env)**
   `env.example` 파일을 복사하여 `.env` 파일을 생성하고, 환경에 맞게 변수를 설정하세요.
   ```bash
   cp env.example .env
   ```
   `.env` 파일을 열어 `SECRET_KEY` 등 필요한 설정을 추가하거나 수정합니다.
   ```ini
   SECRET_KEY=your_secret_key_here
   ```
   **SECRET_KEY 생성 방법:**
   터미널에서 다음 명령어를 실행하여 생성된 무작위 문자열을 사용하세요.
   ```bash
   # OpenSSL 사용 (Mac/Linux)
   openssl rand -hex 32

   # Python 사용 (운영체제 무관)
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## 사용 방법

`main.py`를 통해 시스템의 다양한 기능을 사용할 수 있습니다.

### 1. 데이터 수집 (Load)
과거 당첨 번호 데이터를 수집합니다.
```bash
python main.py load
# 옵션: --from <시작회차> --to <종료회차>
python main.py load --from 1 --to 1200
```

### 2. 번호 예측 (Predict)
다음 회차의 당첨 번호를 예측합니다.
```bash
python main.py predict
# 옵션: --round <회차> (특정 회차 예측 시)
```

### 3. 결과 확인 (Check)
예측한 번호의 당첨 여부를 확인합니다.
```bash
python main.py check
# 옵션: --round <회차>
```

### 4. 웹 앱 실행 (Web)
웹 대시보드를 실행합니다.
```bash
python main.py web
```
웹 브라우저에서 `http://localhost:8000`으로 접속하여 사용할 수 있습니다.

### 5. 주간 자동화
매주 토요일 추첨 후 데이터를 갱신하고 새로운 예측을 생성하려면 `run_weekly.sh` 스크립트를 사용하거나 crontab에 등록하여 사용할 수 있습니다.
```bash
./run_weekly.sh
```

### 6. Docker 배포
Docker 및 Docker Compose를 사용하여 간편하게 실행할 수 있습니다.

1. **컨테이너 실행**
   ```bash
   docker compose up -d
   ```
   - `web` 서비스(FastAPI)와 `db` 서비스(MariaDB)가 시작됩니다.
   - 웹 대시보드는 `http://localhost:8000`에서 접근 가능합니다.

2. **데이터 초기화 (최초 실행 시)**
   컨테이너 내부에서 데이터 수집을 수행하려면 다음 명령을 실행하세요.
   ```bash
   docker compose run web python main.py load --from 1 --to 1200
   ```

## 배포 주의사항

- 이 저장소에는 소스 코드와 `README.md`만 포함되며, `.env` 파일 및 기타 문서 파일(`*.md`)은 보안 및 관리상의 이유로 배포되지 않습니다.
