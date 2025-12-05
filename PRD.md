# AI 로또 분석 시스템 기획서 (Agent 기반)

## 1. 프로젝트 개요
	•	프로젝트명: LottoGenie (로또 지니)
	•	목표:
	•	매주 동행복권 로또 당첨번호 자동 수집
	•	과거 데이터 기반 분석 및 다음 회차 예측 번호 생성
	•	예측 결과 저장 및 실제 당첨 이후 자동 등수 판정
	•	작동 주기: 매주 1회(토요일 추첨 직후)

시스템은 역할(Role) 기반의 Agent 협업 구조로 운영된다.

⸻

## 2. 시스템 에이전트 구성 (R&R)

### 2.1 Agent A — Collector (수집가)

역할: 최신 로또 당첨 정보 자동 수집 및 저장
주요 기능
	•	DB 저장 마지막 회차 확인
	•	동행복권 페이지에서 최신 HTML 크롤링
	•	당첨번호 및 날짜 파싱
	•	history 테이블에 신규 회차 정보 저장
	•	신규 회차가 없으면 종료

사용 기술: HTTP 요청, BeautifulSoup, SQLite

⸻

### 2.2 Agent B — Analyst (분석가)

역할: 과거 기록 분석 및 다음 회차 예측 번호 생성
주요 기능
	•	history 전체 데이터 로드
	•	번호 출현 빈도 분석
	•	최근 미출현 번호 반영(옵션)
	•	가중치 기반 번호 생성(6개 × 5게임)
	•	결과를 my_predictions에 저장

사용 기술: 통계 분석, 번호 가중치 모델, 랜덤 생성

⸻

### 2.3 Agent C — Auditor (검증가)

역할: 예측 번호와 실제 당첨번호 비교 후 등수 판정
주요 기능
	•	직전 회차 예측번호 로드
	•	실제 history와 비교하여 등수 계산
	•	rank, matched_main, matched_bonus 업데이트
	•	수익률 리포트 생성(옵션)

사용 기술: 집합 연산(Set), SQLite

⸻

## 3. 전체 워크플로우 (Weekly Cycle)

[Trigger] 매주 토요일 21:00 또는 수동 실행
	1.	Collector 실행
	•	DB 마지막 회차 확인 (예: 1200)
	•	다음 회차(1201) HTML 수집 가능 여부 확인
	•	데이터 파싱 후 history 업데이트
	2.	Auditor 실행
	•	방금 저장된 회차(1201)의 실제 당첨번호 로드
	•	예측번호와 비교 후 등수 계산
	•	my_predictions 업데이트
	3.	Analyst 실행
	•	최신 데이터(1201 회차까지) 기반 분석
	•	다음 회차(1202) 예측번호 5세트 생성
	•	DB 저장

⸻

## 4. 데이터베이스 스키마

###4.1 Table: history (당첨 내역)

컬럼	타입	설명
round_no	INTEGER PK	회차 번호
num1~num6	INTEGER	메인 당첨 번호
bonus	INTEGER	보너스 번호
draw_date	TEXT	추첨일


⸻

### 4.2 Table: my_predictions (예측 번호)

컬럼	타입	설명
id	INTEGER PK	고유 ID
round_no	INTEGER	예측한 타깃 회차
num1~num6	INTEGER	예측 번호
matched_main	INTEGER	일치한 메인 번호 수
matched_bonus	INTEGER	보너스 일치 여부 (0/1)
rank	TEXT	등수 (미추첨, 1등 등)
created_at	TEXT	생성 시간


⸻

## 5. 기능 명세 (Tool / Action)

### 5.1 fetch_lotto_data(round_no)
	•	Input: 회차 번호(Int)
	•	Process:
	•	URL 요청
	•	HTML 파싱
	•	번호·보너스·날짜 추출
	•	Output:
	•	{ nums: [...], bonus: N, date: 'YYYY-MM-DD' }
	•	또는 실패 시 None

⸻

### 5.2 generate_numbers(history)
	•	Input: 과거 당첨 데이터(List)
	•	Process:
	•	출현 횟수 분석
	•	최근 미출현 번호 조건 적용(옵션)
	•	가중 랜덤 기반 번호 생성
	•	Output:
	•	예측 번호 5세트 (List)

⸻

### 5.3 calculate_rank(my_nums, win_nums, bonus)
	•	Input: 예측번호, 당첨번호, 보너스 번호
	•	Output:
	•	등수 (1등, 2등, … 꽝)
	•	일치개수
	•	보너스 일치 여부

⸻

## 6. 고도화 로드맵

### 6.1 예측 알고리즘 개선
	•	출현 빈도 외 패턴 기반 분석
	•	번호 상관관계 분석
	•	ML 모델(LSTM / XGBoost) 도입 가능

### 6.2 자동화 및 운영환경 고도화
	•	CLI 명령 제공
	•	python lotto.py load --from 1 --to 1200
	•	python lotto.py predict --round 1201
	•	python lotto.py check --round 1201
	•	Linux crontab 연동

### 6.3 시각화 기능 추가
	•	pandas 기반 통계 테이블
	•	matplotlib 기반 그래프
	•	Flask/FastAPI 기반 웹 대시보드 구현 가능

⸻

## 7. 요약

이 시스템은 다음 구조로 이루어진다:

역할	담당 에이전트	기능
데이터 수집	Collector	최신 회차 저장
예측 검증	Auditor	실제 당첨번호와 분석
예측 생성	Analyst	다음 회차 번호 생성

Agent 간 협력으로 수집 → 검증 → 예측 주기가 매주 자동으로 반복되는 구조이다.
