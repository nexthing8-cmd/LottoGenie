# LottoGenie

LottoGenie는 AI 기반 로또 당첨 번호 예측 시스템입니다. 과거 데이터를 수집하고 분석하여 당첨 확률이 높은 번호를 추천하며, 웹 대시보드와 자동화 스크립트를 통해 편리한 사용 환경을 제공합니다.

## 시스템 개요

LottoGenie는 다음과 같은 주요 컴포넌트로 구성되어 있습니다:

- **Collector**: 로또 공식 홈페이지 등에서 과거 당첨 번호 데이터를 수집합니다.
- **Analyst**: LSTM 모델 기반의 AI 분석을 통해 다음 회차 번호를 예측합니다. (자동 학습 및 튜닝 포함)
- **Auditor**: 예측된 번호와 실제 당첨 번호를 비교하여 예측 정확도를 검증합니다.
- **Web App**:
  - 직관적인 대시보드 및 당첨 결과 시각화
  - 사용자 기반 예측 번호 생성 및 관리 (메모 기능 포함)
  - 회원가입, 로그인, **회원 탈퇴** 기능
  - 역대 당첨 내역 조회 및 상세정보 페이지
  - **분석 페이지**: 번호별 출현 빈도, 최근 출현 비율, 전체 회차 당첨 번호 흐름 차트 (인터랙티브)
  - **1등 배출점 위치 확인**: 네이버 지도 연동
- **Automation**: 매주 자동으로 데이터 수집, 모델 재학습, 결과 확인, 예측 생성을 수행하는 워크플로우를 지원합니다.

## 설치 방법

1. **저장소 클론**

   ```bash
   git clone <repository-url>
   cd LottoGenie
   ```

2. **의존성 패키지 설치**
   Python 3.12 이상 환경이 권장됩니다.

   ```bash
   pip install -r requirements.txt
   ```

3. **환경 설정 (.env)**
   `env.example` 파일을 복사하여 `.env` 파일을 생성하고, 환경에 맞게 변수를 설정하세요.
   ```bash
   cp env.example .env
   ```
   `.env` 파일 내 `SECRET_KEY`, `WEBHOOK_URL`, `DB_` 설정 등을 수정합니다.

## 사용 방법

`main.py`를 통해 시스템의 다양한 기능을 사용할 수 있습니다.

### 1. 데이터 수집 (Load)

과거 당첨 번호 데이터 및 당첨금 정보를 수집합니다.

## 🚀 Deployment (Docker)

### 1. Build and Run

```bash
docker-compose up --build -d
```

### 2. Check Logs

- **Web App**: `docker logs -f lottogenie-web-1`
- **Scheduler**: `docker logs -f lottogenie-scheduler-1`
- **File Logs**: The scheduler also writes to `./logs/lottogenie_YYYY-MM-DD.log` (mounted to `/var/log/lottogenie`).

### 3. Manual Scheduler Execution (One-off)

If the scheduler missed a run or needs to be forced:

```bash
# Inside Container (Recommended)
docker exec -it lottogenie-scheduler-1 python src/scheduler.py

# Or using the test script (Local)
python tests/run_weekly_manual.py
```

## 🛠 Features

- **Prediction System**: LSTM-based lottery number prediction.
- **Analysis**: Statistical charts including Winner Count trends.
- **Automation**: Weekly auto-updates via Scheduler (Saturdays 21:15 KST).
- **Security**: Soft Delete for data preservation.
- **Operational**: Block prediction generation during draw times (Sat 19:30-21:30).

### 2. 1등 당첨점 수집 (Load Stores) - NEW

1등 당첨 판매점 정보를 수집합니다.

```bash
python main.py load_stores --from 1 --to 1200
```

### 3. 모델 학습 (Train)

최신 데이터를 기반으로 AI 모델을 학습/파인튜닝합니다.

```bash
python main.py train
```

### 4. 번호 예측 (Predict)

학습된 모델을 사용하여 예측 번호를 생성합니다.

```bash
python main.py predict
```

### 5. 결과 확인 (Check)

예측한 번호의 당첨 여부를 확인합니다.

```bash
python main.py check
```

### 6. 웹 앱 실행 (Web - 개발 모드)

웹 대시보드를 개발 모드로 실행합니다.

```bash
python main.py web
```

웹 브라우저에서 `http://localhost:8000`으로 접속하여 사용할 수 있습니다.

- **당첨금 정보 표시**: 최신 회차의 등수별 당첨금, 당첨자 수, 1등 당첨 유형(자동/수동) 등을 확인할 수 있습니다.
- **분석 페이지** (`/analysis`): 번호별 출현 빈도, 최근 출현 비율, 전체 회차 당첨 번호 흐름을 인터랙티브 차트로 확인할 수 있습니다.
- **당첨 상세정보** (`/history/{round_no}`): 특정 회차의 상세 정보, 등위별 당첨금, 1등 배출점 정보 및 네이버 지도 위치 확인이 가능합니다.

### 7. 프로덕션 배포 (Production)

`gunicorn`을 사용하여 고성능 모드로 서버를 실행합니다.

```bash
./start.sh
```

### 8. Docker 배포

Docker Compose를 사용하여 간편하게 실행할 수 있습니다.

```bash
# 실행
docker compose up -d

# 데이터 초기화 (최초 1회 - 당첨정보 및 당첨점)
docker compose run web python main.py load --from 1 --to 1200
docker compose run web python main.py load_stores --from 1 --to 1200
```

## 주간 자동화

매주 토요일 추첨 후 데이터를 갱신하고 모델을 재학습하려면 `run_weekly.sh` 스크립트를 crontab에 등록하여 사용할 수 있습니다. 이 스크립트는 수집 -> 검증 -> 학습 -> 예측 과정을 순차적으로 수행합니다.

```bash
./run_weekly.sh
```
