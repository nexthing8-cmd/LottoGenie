# 작업 완료 내역 (Workflow)

## 🎨 UI 디자인 개선 (2025-12-05)

사용자의 요청에 따라 로또 번호 표시 UI를 개선했습니다.

### 1. 로또 볼 색상 적용

공식 동행복권 색상 규정에 맞춰 번호 구간별 색상을 적용했습니다.

| 번호 구간 | 색상            | CSS 클래스     |
| :-------- | :-------------- | :------------- |
| 1 ~ 10    | 노란색 (Yellow) | `.ball-yellow` |
| 11 ~ 20   | 파란색 (Blue)   | `.ball-blue`   |
| 21 ~ 30   | 빨간색 (Red)    | `.ball-red`    |
| 31 ~ 40   | 회색 (Gray)     | `.ball-gray`   |
| 41 ~ 45   | 초록색 (Green)  | `.ball-green`  |

### 2. 텍스트 및 스타일 디테일 작업

제공된 사진 자료를 참고하여 "프리미엄" 느낌이 나도록 스타일을 다듬었습니다.

- **크기 확대**: 볼 크기를 `40px`로 키워 가독성 확보
- **폰트**: `font-weight: 900` (Extra Bold) 적용 및 흰색 텍스트 통일
- **입체 효과**:
  - `text-shadow`: 텍스트에 그림자를 주어 양각 효과 구현
  - `box-shadow`: 볼 자체에 내부/외부 그림자를 주어 구체(Sphere) 느낌 구현

### 3. 파비콘(Favicon) 추가

- **디자인**: 황금색 로또 볼에 파란색 지니 램프가 그려진 아이콘 생성.
- **적용**: 모든 페이지(`index.html`, `analysis.html`)에 파비콘 적용.

### 📂 수정된 파일

- `templates/index.html`: CSS 스타일 정의 및 파비콘 링크 추가
- `templates/analysis.html`: 파비콘 링크 추가
- `static/favicon.png`: 생성된 파비콘 이미지

---

## 🗄️ 데이터베이스 마이그레이션 (2025-12-05)

기존 SQLite 데이터베이스를 MariaDB로 마이그레이션했습니다.

### 1. 마이그레이션 작업

- **SQLite -> MariaDB**: `migrate_db.py` 스크립트를 통해 데이터 이관 완료.
- **스키마 변경**: `my_predictions` 테이블의 `rank` 컬럼을 `rank_val`로 변경 (MariaDB 예약어 충돌 방지).
- **데이터 정리**: 로컬 `data/lotto.db` 파일 삭제.

### 2. 코드 변경

- **DB 연결**: `src/database.py`에서 `pymysql`을 사용하여 MariaDB 연결 로직으로 변경.
- **웹 앱**: `src/web_app.py` 및 `templates/index.html`에서 딕셔너리 커서(`DictCursor`) 대응.

### 📂 수정된 파일

- `src/database.py`: DB 연결 및 초기화 로직 변경
- `src/web_app.py`: DB 연결 방식 변경
- `templates/index.html`: 데이터 접근 방식 변경 (인덱스 -> 키)
- `requirements.txt`: `pymysql`, `python-dotenv` 추가

---

## 🤖 에이전트 및 CLI 구현 (2025-12-05)

기획서에 명시된 3가지 핵심 에이전트와 CLI 기능을 구현하고, MariaDB 환경에 맞게 최적화했습니다.

### 1. Agent A - 수집가 (Collector)

- **기능**: 동행복권 사이트 크롤링 및 최신 회차 데이터 DB 저장.
- **업데이트**: `INSERT IGNORE` 구문 및 `%s` 플레이스홀더 적용.
- **파일**: `src/collector.py`

### 2. Agent B - 분석가 (Analyst)

- **기능**: 과거 데이터 기반 빈도 분석 및 가중치 적용 예측 번호 생성.
- **업데이트**: `DictCursor` 데이터 처리 로직 수정.
- **파일**: `src/analyst.py`

### 3. Agent C - 검증가 (Auditor)

- **기능**: 예측 번호와 실제 당첨 번호 대조 및 등수 판정.
- **업데이트**: `DictCursor` 데이터 처리 및 SQL 문법 수정.
- **파일**: `src/auditor.py`

### 4. CLI (Command Line Interface)

- **기능**: 터미널에서 `load`, `predict`, `check`, `web` 명령어로 시스템 제어.
- **파일**: `main.py`

---

## ⚙️ 자동화 구현 (2025-12-05)

매주 반복되는 작업을 자동화하기 위한 스크립트를 구현했습니다.

### 1. 자동화 스크립트

- `run_weekly.sh`: 수집(`load`) -> 검증(`check`) -> 예측(`predict`) 과정을 순차적으로 실행하는 쉘 스크립트.
- `main.py` 업데이트: `load` 명령어가 인자 없이도 실행되도록 수정 (자동 범위 감지).

### 2. Crontab 설정 (가이드)

- 매주 토요일 21:30에 실행되도록 설정 권장.
- 예: `30 21 * * 6 /path/to/run_weekly.sh`

---

## 🧠 예측 알고리즘 고도화 (2025-12-05)

단순 빈도 분석을 넘어선 딥러닝 기반 예측 모델을 도입했습니다.

### 1. LSTM 모델 도입

- **기술**: TensorFlow/Keras 기반의 LSTM(Long Short-Term Memory) 신경망 사용.
- **학습**: 과거 10회차 당첨 번호 패턴을 학습하여 다음 회차 번호별 출현 확률 예측.
- **생성**: 예측된 확률을 가중치로 사용하여 6개 번호 조합 생성.

### 📂 수정된 파일

- `src/analyst.py`: LSTM 모델 구현 및 데이터 전처리 로직 추가.
- `requirements.txt`: `tensorflow`, `numpy`, `pandas`, `scikit-learn` 추가.

---

## 📊 웹 대시보드 고도화 (2025-12-05)

정적인 이미지 차트를 동적인 인터랙티브 차트로 변경했습니다.

### 1. Chart.js 도입

- **기술**: Chart.js 라이브러리(CDN) 사용.
- **기능**:
  - **번호별 빈도 차트**: 1~45번 번호별 출현 횟수 막대 그래프 (색상 적용).
  - **당첨 흐름 차트**: 최근 20회차 당첨 번호 산점도 (Scatter Plot).
- **장점**: 마우스 오버 시 상세 정보 확인 가능, 깔끔한 UI.

### 2. 버그 수정

- **Pandas Warning**: `pymysql` 직접 연결 대신 `SQLAlchemy` 엔진을 사용하여 pandas 경고 해결.
- **IDE Linting**: Jinja2 템플릿 문법과 JS 문법 충돌 해결 (DOM 데이터 주입 방식).

### 📂 수정된 파일

- `src/visualizer.py`: 데이터 추출 로직 추가 및 SQLAlchemy 엔진 사용.
- `src/web_app.py`: 데이터 전달 로직 변경.
- `templates/analysis.html`: Chart.js 캔버스 및 렌더링 스크립트 추가.
- `requirements.txt`: `sqlalchemy` 추가.

---

## 🔐 사용자 인증 (2025-12-05)

개인별 예측 번호 관리를 위한 로그인/회원가입 기능을 구현했습니다.

### 1. 인증 시스템

- **방식**: JWT (JSON Web Token) 기반 인증.
- **보안**: Bcrypt를 이용한 비밀번호 해싱 저장.
- **기능**: 회원가입, 로그인, 로그아웃.

### 2. 웹 앱 통합

- **UI**: 상단 네비게이션에 로그인/회원가입/로그아웃 링크 추가.
- **권한 제어**: 로그인한 사용자만 예측 번호 생성 가능.

### 📂 수정된 파일

- `src/auth.py`: 인증 로직 구현.
- `src/database.py`: `users` 테이블 추가.
- `src/web_app.py`: 인증 라우트 및 미들웨어 추가.
- `templates/login.html`, `templates/register.html`: 인증 페이지 추가.
- `templates/index.html`: 로그인 상태에 따른 UI 변경.

---

## 🔔 알림 기능 추가 (2025-12-05)

예측 번호 생성 및 당첨 확인 결과에 대한 실시간 알림 기능을 구현했습니다.

### 1. Notification Agent 추가

- **기능**: SynologyChat Webhook API를 통한 메시지 발송.
- **파일**: `src/notifier.py`

### 2. 에이전트 연동

- **Agent B (Analyst)**: 번호 예측 완료 시 알림 발송.
- **Agent C (Auditor)**: 당첨 확인 결과 알림 발송.

### 📂 수정된 파일

- `src/notifier.py`: 신규 생성.
- `src/analyst.py`: 알림 연동.
- `src/auditor.py`: 알림 연동.
- `requirements.txt`: `requests` 추가.

---

## 🚀 모델 성능 최적화 (2025-12-05)

예측 모델의 학습 효율성을 높이고 실행 속도를 개선했습니다.

### 1. 모델 저장 및 로드 (Persistence)

- **파일**: `data/lotto_model.keras`
- **기능**: 매번 처음부터 학습하지 않고, 기존 학습된 모델을 불러와 추가 데이터만 학습(Fine-tuning)하도록 개선.
  - **신규 학습**: 100 Epochs (최초 실행 시)
  - **추가 학습**: 10 Epochs (모델 존재 시)

### 2. 라이브러리 충돌 해결

- **문제**: `pandas`, `sklearn`과 `tensorflow` 동시 사용 시 프로세스 멈춤 현상(Hang) 발생.
- **해결**: `pandas`, `sklearn` 의존성을 제거하고 `numpy`만을 사용하여 데이터 전처리 로직(One-hot Encoding)을 재구현.

### 📂 수정된 파일

- `src/analyst.py`: 모델 저장/로드 로직 추가, 불필요한 import 제거, 수동 One-hot Encoding 구현.

---

## 📝 사용자별 예측 관리 고도화 (Memo) (2025-12-05)

사용자가 자신의 예측 번호에 개인적인 메모를 남길 수 있는 기능을 구현했습니다.

### 1. 데이터베이스 변경

- **테이블**: `my_predictions`
- **컬럼**: `memo` (TEXT 타입) 추가.

### 2. 메모 기능 구현

- **UI**: 마이페이지(`mypage.html`)의 각 예측 카드에 메모 입력 필드 및 저장 버튼 추가.
- **API**: `POST /update_memo/{id}` 엔드포인트 구현 (메모 업데이트).

### 📂 수정된 파일

- `src/database.py`: 스키마 초기화 로직 업데이트.
- `src/web_app.py`: 메모 수정 API 라우트 추가.
- `templates/mypage.html`: 메모 입력 폼 UI 추가.

---

## ⚡ 예측 번호 생성 UX 개선 (2025-12-05)

예측 번호 생성 시 "무반응"으로 느껴지던 속도 저하 문제를 해결했습니다.

### 1. 학습/예측 로직 분리

- **원인**: 기존에는 예측(`predict`) 요청 시마다 모델 학습(Fine-tuning)을 수행하여 응답 시간이 매우 길어짐 (1분 이상).
- **해결**:
  - `src/analyst.py`: `generate_numbers_ml` 함수를 학습(`train_model`)과 예측(`generate_numbers_ml` - Pure Predict)으로 분리.
  - `run_analyst`: `mode` 파라미터를 추가하여 기본적으로는 예측만 수행하도록 변경.
  - **결과**: 웹에서 예측 생성 클릭 시 즉시 응답 (1초 미만).

### 2. 자동화 스크립트 업데이트

- `run_weekly.sh`: 주간 작업 시에는 학습(`train`) 후 예측(`predict`)을 수행하도록 순서 변경.
- `main.py`: `train` 명령어 추가.

### 📂 수정된 파일

- `src/analyst.py`: 함수 분리 및 로직 개선.
- `main.py`: `train` CLI 핸들러 추가.
- `run_weekly.sh`: 학습 단계 추가.
- `templates/index.html`: 버튼 UX 개선 (기존 로직 유지하되 속도 개선으로 해결).

---

## 📜 당첨내역 조회 기능 구현 (2025-12-05)

역대 로또 당첨 내역을 조회할 수 있는 페이지를 구현하고, UI 일관성을 확보했습니다.

### 1. 기능 구현

- **엔드포인트**: `/history` (GET)
- **기능**: 전체 당첨 내역 조회, 페이징 처리 (10개씩 노출).

### 2. UI 개선

- `templates/history.html`: 메인 대시보드(`index.html`)와 동일한 헤더 및 로그인/로그아웃 네비게이션 적용.
- **일관성 확보**: 사이트 전반에 걸쳐 통일된 사용자 경험 제공.

### 📂 수정된 파일

- `templates/history.html`: UI 및 스크립트 업데이트.

---

## 🧩 템플릿 리팩토링 및 레이아웃 통일 (2025-12-05)

페이지 간 헤더/네비게이션 불일치 문제를 해결하기 위해 Jinja2 템플릿 상속 구조를 도입했습니다.

### 1. 구조 개선 (Template Inheritance)

- `templates/base.html`: 공통 레이아웃(Header, Footer, Scripts)을 정의하는 마스터 템플릿 생성.
- **상속 적용**: `index.html`, `analysis.html`, `history.html`, `mypage.html`, `login.html`, `register.html`이 `base.html`을 상속받도록 리팩토링.

### 2. 효과

- **일관성**: 모든 페이지에서 동일한 헤더와 네비게이션 바가 유지됨.
- **유지보수성**: 헤더 메뉴 수정 시 `base.html`만 수정하면 모든 페이지에 반영됨.
- **코드 중복 제거**: 공통 CSS(로또 볼, 버튼 스타일 등) 및 스크립트(로그아웃 등)를 `base.html`로 통합.

### 📂 수정된 파일

- `templates/base.html` (New)
- `templates/*.html` (Refactored)

---

## 🗑️ 회원 탈퇴 기능 구현 (2025-12-05)

사용자가 자신의 계정과 관련 데이터를 안전하게 삭제할 수 있는 기능을 구현했습니다.

### 1. 기능 구현

- **엔드포인트**: `POST /delete_account`
- **로직**:
  1.  사용자 인증(쿠키 확인).
  2.  `my_predictions` 테이블에서 해당 사용자의 모든 예측 데이터 삭제.
  3.  `users` 테이블에서 사용자 계정 삭제.
  4.  쿠키 만료 및 홈 화면 리다이렉트.

### 2. UI 추가

- `templates/mypage.html`: 하단에 [회원 탈퇴] 버튼 추가. 실수 방지를 위한 `confirm` 알림창 적용.

### 📂 수정된 파일

- `src/web_app.py`: 탈퇴 로직 추가.
- `templates/mypage.html`: 탈퇴 버튼 추가.

---

## 🚀 배포 준비 및 Gunicorn 설정 (2025-12-05)

프로덕션 환경 배포를 위한 프로세스 관리자(`gunicorn`) 설정 및 실행 스크립트를 작성했습니다.

### 1. 설정 추가

- `requirements.txt`: `gunicorn` 추가.
- `start.sh`: Gunicorn 실행 스크립트 작성 (Worker: 4, Class: UvicornWorker).

### 2. 검증

- 로컬 환경에서 `start.sh` 실행 및 `curl`을 통한 정상 구동 확인.

### 📂 수정된 파일

- `requirements.txt`: 의존성 추가.
- `start.sh` (New): 실행 스크립트.

### 3. Dockerfile 업데이트

- `python:3.12-slim` 베이스 이미지 사용.
- `start.sh`를 엔트리포인트로 설정하여 Gunicorn 실행 보장.

---

## 📚 프로젝트 최종 점검 및 문서화 (2025-12-05)

프로젝트의 모든 기능 구현을 완료하고, 최신 상태를 반영하여 문서화를 마쳤습니다.

### 1. README.md 업데이트

- **기능 추가**: 회원 탈퇴, 당첨 내역 조회, 메모 기능 등 신규 기능 명시.
- **사용법 최신화**: `main.py train`, `start.sh` 실행 방법 가이드 추가.
- **기술 스택**: Python 3.12 권장 사항 반영.

### ✅ 프로젝트 완료

LottoGenie의 주요 MVP 기능 개발이 모두 완료되었습니다. AI 예측부터 웹 대시보드, 자동화, 배포 설정까지 턴키로 구성되어 즉시 운영 가능합니다.

---

## 📜 당첨 내역 페이지 고도화 (2025-12-05)

사용자 피드백을 반영하여 당첨 내역 조회 페이지를 개선했습니다.

### 1. 기능 개선

- **페이지네이션 옵션**: 한 페이지당 표시할 항목 수(Limit)를 10, 25, 50개 중에서 선택할 수 있도록 Dropdown UI를 추가했습니다.
- **회차 검색**: 특정 회차 번호를 입력하여 해당 회차의 결과만 빠르게 조회할 수 있는 검색바를 추가했습니다.

### 2. Back-end 로직 수정

- `/history` 엔드포인트가 `limit` 및 `search_round` 파라미터를 받아 동적으로 쿼리를 생성하도록 수정했습니다.

### 📂 수정된 파일

- `src/web_app.py`: 파라미터 처리 및 SQL 쿼리 로직 변경.
- `templates/history.html`: 검색바 및 Limit 선택 UI 추가, 페이지네이션 링크 로직 수정.

---

## 🏪 1등 당첨 지점 데이터 구축 (2025-12-06)

1등 당첨 판매점 정보를 수집하고 DB화했습니다.

### 1. DB 스키마 추가

- `winning_stores` 테이블 생성 (round_no, store_name, choice_type, address).

### 2. 수집기 구현

- 동행복권 당첨점 페이지 크롤링 로직 추가 (`src/collector.py`).
- BeautifulSoup을 사용하여 상호명, 자동/수동 여부, 주소 추출.

### 3. CLI 기능 추가

- `python main.py load_stores --from 1 --to 1200` 명령어로 대량 데이터 적재 가능.

### 📂 수정된 파일

- `src/database.py`: 테이블 정의 추가.
- `src/collector.py`: `collect_winning_stores` 함수 구현.
- `main.py`: `load_stores` 커맨드 추가.

---

## 💰 당첨금 정보 수집 및 시각화 (2025-12-06)

당첨금 규모와 당첨자 수 등 상세 정보를 수집하여 사용자가 볼 수 있도록 개선했습니다.

### 1. DB 변경사항

- `prizes` 테이블 추가 (등수, 총상금, 당첨자수, 개별상금).
- `history` 테이블에 1등 당첨 유형(자동/수동) 컬럼 추가.

### 2. 수집기 개선

- `fetch_lotto_data`에서 당첨금 테이블 파싱 로직 추가.
- 차단 방지를 위한 3~5초 랜덤 딜레이 적용.

### 3. UI 변경사항

- 메인 대시보드(`index.html`)에 최신 회차의 당첨금 정보를 표 형태로 출력.
- 금액에 천 단위 콤마(,) 포맷팅 적용.

### 📂 수정된 파일

- `src/collector.py`: 당첨금 테이블 파싱 로직 추가.
- `templates/index.html`: 당첨금 정보 표시 추가.

---

## 📊 분석 페이지 고도화 및 데이터 탐색 기능 (2025-12-06)

당첨 번호 흐름 차트를 개선하여 전체 회차 데이터를 탐색할 수 있도록 했습니다.

### 1. 기능 개선

- **전체 데이터 로드**: 최근 20회차만 표시하던 제한을 제거하고 전체 회차 데이터를 로드하도록 변경.
- **인터랙티브 탐색**: Chart.js zoom 플러그인을 사용하여 마우스 휠로 확대/축소, 드래그로 이동하여 이전 회차 데이터 탐색 가능.
- **초기 표시 범위**: 처음에는 최근 20회차가 보이도록 초기 줌 설정.

### 📂 수정된 파일

- `src/visualizer.py`: `get_trend_data()` 함수 수정 (전체 데이터 반환 옵션 추가).
- `src/web_app.py`: 전체 데이터 로드하도록 변경.
- `templates/analysis.html`: 초기 줌 설정 및 zoom limits 추가.

---

## 🎨 당첨 상세정보 페이지 UI 개선 (2025-12-06)

당첨 상세정보 페이지의 테이블 정렬을 개선하여 가독성을 높였습니다.

### 1. 테이블 정렬 개선

- **등위별 당첨금 정보 테이블**:
  - 순위: 왼쪽 정렬
  - 총 당첨금액, 당첨자 수, 1게임당 당첨금액: 오른쪽 정렬
- **1등 배출점 테이블**:
  - 상호명, 소재지: 왼쪽 정렬

### 📂 수정된 파일

- `templates/history_detail.html`: CSS 클래스 추가 및 테이블 정렬 적용.

---

## 🗺️ 1등 배출점 네이버 지도 연동 (2025-12-06)

1등 배출점의 위치를 네이버 지도에서 바로 확인할 수 있는 기능을 추가했습니다.

### 1. 기능 구현

- **위치보기 버튼**: 1등 배출점 테이블에 "위치보기" 컬럼 추가.
- **네이버 지도 연동**: 소재지 주소를 기반으로 네이버 지도 검색 URL 생성.
- **새 탭 열기**: 클릭 시 새 탭에서 네이버 지도가 열리도록 설정.

### 📂 수정된 파일

- `src/web_app.py`: 네이버 지도 URL 생성 로직 추가 (`urllib.parse.quote` 사용).
- `templates/history_detail.html`: 위치보기 버튼 UI 추가.

---

## 🧪 테스트 구조 정리 (2025-12-06)

테스트 파일들을 `tests` 폴더로 정리하여 프로젝트 구조를 개선했습니다.

### 1. 구조 개선

- `tests/` 폴더 생성 및 테스트 파일 이동.
- `tests/__init__.py` 추가하여 Python 패키지로 구성.

### 📂 수정된 파일

- `tests/test_analysis_web.py`: 분석 페이지 테스트.
- `tests/test_web.py`: 웹 라우트 테스트.
- `tests/__init__.py`: 패키지 초기화 파일.

---

## 🛠️ 배포 및 운영 환경 구축 (2025-12-06)

Docker 기반의 배포 환경과 주간 자동화 스케줄러를 구축했습니다.

### 1. Docker 컨테이너화

- **Dockerfile**: Python 3.9 Slim 기반의 이미지 빌드 설정.
- **Docker Compose**: 웹 애플리케이션(Web)과 스케줄러(Scheduler) 서비스를 통합 관리.
  - 외부 DB 연결 설정 (`DB_HOST` 등 환경변수 지원).
  - 로그 볼륨 마운트 (`./logs` -> `/var/log/lottogenie`).

### 2. 주간 스케줄러 구현

- **파일**: `src/scheduler.py`
- **기능**: 매주 토요일 21:15에 자동으로 다음 작업 수행:
  1. 당첨 번호 크롤링.
  2. 1등 당첨점 정보 수집.
  3. 지난주 예측 결과 검증 (Auditor).
  4. 예측 모델 재학습 (Train).
  5. 다음 회차 번호 예측 (Predict).
- **로깅**: 날짜별 로그 파일 생성 (`lottogenie_YYYY-MM-DD.log`).

### 📂 수정된 파일

- `Dockerfile`, `docker-compose.yml`
- `src/scheduler.py`
- `requirements.txt` (`schedule` 추가)

---

## 🎨 UI/UX 리파인먼트 (2025-12-06)

사용자 피드백을 반영하여 세부적인 UI 문제를 수정하고 편의성을 개선했습니다.

### 1. 마이페이지 개선

- **당첨 상태 배지**: 각 예측 번호마다 "미추첨", "1등~5등", "낙첨" 상태를 직관적인 배지(Badge)로 표시.
- **색상 구분**: 대기중(회색), 당첨(금색/주황), 낙첨(빨강)으로 시각적 구분 강화.

### 2. 레이아웃 수정

- **모바일 헤더**: 모바일 환경에서 메뉴 버튼과 로고 텍스트가 겹치는 현상을 해결하기 위해 헤더 패딩 조정.
- **당첨내역 페이지**: 타이틀을 "당첨정보"로 변경하고, 상세 페이지 이동 팁("회차 클릭 시...") 추가.

### 3. 분석 차트 추가

- **파이 차트**: 최근 20회차 기준 번호별 출현 비율을 시각화하는 원형 차트 추가.

### 📂 수정된 파일

- `templates/mypage.html`: 상태 배지 UI 추가.
- `templates/base.html`: 모바일 헤더 CSS 수정.
- `templates/analysis.html`: 파이 차트 추가 (확인 완료).
- `templates/history.html`: 타이틀 및 안내 문구 수정.

---

## 📈 분석 기능 고도화 (2025-12-06)

워크플로우 지침에 따라 분석 페이지의 시각화와 운영 정책을 강화했습니다.

### 1. 역대 1등 당첨자 수 차트

- **기능**: 회차별 1등 당첨자 수의 추이를 보여주는 선형 차트(Line Chart) 추가.
- **UI**: 초기 로딩 시 최근 20회차 데이터를 보여주며, 줌/팬 기능을 통해 전체 데이터 탐색 가능.
- **데이터**: 우측 상단에 "총 1등 당첨자 수" 합계 표시.

### 2. 예측 생성 제한 (Time Lock)

- **정책**: 매주 토요일 19:30 ~ 21:30 사이에는 복권 구매 마감 임박으로 예측 생성을 차단.
- **구현**: 서버 측(`web_app.py`)에서 토요일 해당 시간대 요청 시 400 에러 반환 및 클라이언트 알림 처리.

### 📂 수정된 파일

- `src/visualizer.py`: 당첨자 수 데이터 조회 쿼리 추가.
- `src/web_app.py`: Time Lock 미들웨어 로직 추가.
- `templates/analysis.html`: 차트 추가 및 줌/팬 설정, 합계 표시.
- `templates/index.html`: 예외 처리 알림 로직 개선.

---
