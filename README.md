# LLM Village Prototype

LLM 기반 농촌 마을 시뮬레이션을 웹앱 형태로 빠르게 체험할 수 있는 프로토타입입니다. FastAPI 백엔드와 간단한 정적 프론트엔드를 제공하며, NPC들은 체력·스태미너·배고픔·호감도 스탯을 바탕으로 간단한 규칙형 대화를 주고받습니다.

## 주요 특징

- **NPC 스탯 관리**: 각 NPC는 체력(HP), 스태미너, 배고픔, 호감도를 보유하며 시간 경과에 따라 수치가 변합니다.
- **LLM 대화 모사**: 실제 LLM 대신, NPC 역할과 현재 스탯을 기반으로 상황에 맞는 대사를 생성하는 휴리스틱 로직을 구현했습니다.
- **마을 이벤트 루프**: 시간 경과 API를 호출하면 NPC 간 자동 대화와 스탯 변화가 발생합니다.
- **간단한 웹 UI**: `/frontend/index.html`을 통해 NPC 상태와 대화 로그를 확인하고 플레이어가 직접 대화를 시도할 수 있습니다.

## 프로젝트 구조

```
app/
  __init__.py        # FastAPI 앱 익스포트
  main.py            # REST API 엔드포인트 정의
  models.py          # NPC 및 대화 로그 데이터 모델
  state.py           # 인메모리 시뮬레이션 상태 및 로직
frontend/
  index.html         # 정적 관찰/상호작용 페이지
requirements.txt     # FastAPI 실행에 필요한 의존성 목록
README.md            # 이 문서
```

## 실행 방법

1. 가상 환경을 생성하고 의존성을 설치합니다.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 개발 서버를 실행합니다.
   ```bash
   uvicorn app.main:app --reload
   ```
3. 브라우저에서 `frontend/index.html` 파일을 열거나, 정적 서버를 띄워 API(`http://127.0.0.1:8000/api/...`)와 연동합니다.

## 사용 가능한 API

| Method | Endpoint                 | 설명 |
|--------|--------------------------|------|
| GET    | `/api/npcs`              | NPC 목록과 현재 스탯 조회 |
| GET    | `/api/logs?limit=40`     | 최근 대화 로그 조회 |
| POST   | `/api/interactions/user` | 플레이어가 NPC에게 말을 걸고 답변 획득 |
| POST   | `/api/simulate/tick`     | 마을 시간을 한 스텝(또는 여러 스텝) 진행 |
| POST   | `/api/admin/reset`       | 시뮬레이션 초기화 |

각 엔드포인트는 JSON을 반환하며, 간단한 프로토타입 시나리오 테스트에 활용할 수 있습니다.

## 차후 확장 아이디어

- 실제 LLM(OpenAI 등)과 연동하여 NPC 대사를 생성
- Supabase 등 외부 DB에 NPC 스탯과 로그를 저장해 세션 간 상태 유지
- Pygame 또는 WebGL 기반의 시각적 마을 맵 렌더링 추가
- 멀티 유저 접속을 위한 WebSocket 실시간 통신 적용

---

이 프로토타입을 바탕으로 LLM NPC 마을 콘셉트를 빠르게 검증하고, 필요한 기능을 단계적으로 확장해 나갈 수 있습니다.
