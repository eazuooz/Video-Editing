// v5 paper-white / Tetris / short original meme asides / 19.5-second examples.
// Durations remain draft estimates until approved full narration.
export const STORYBOARD = [
  {
    "id": "01",
    "title": "공부하러 앉았는데, 진로부터 다시 고민",
    "tag": "불안 → 작은 실천",
    "labels": [
      "오늘 계획",
      "AI 소식",
      "작은 실천"
    ],
    "visual": "flow"
  },
  {
    "id": "02",
    "title": "회사에서는 다 알고 있을까?",
    "tag": "기대 ≠ 검증",
    "labels": [
      "기대",
      "검증",
      "내가 배울 것"
    ],
    "visual": "flow"
  },
  {
    "id": "03",
    "title": "고쳐 달랬더니, 다른 데가 고장 났다",
    "tag": "돌아간다 ≠ 이해했다",
    "labels": [
      "예상: 5",
      "실제: 4",
      "조건 확인"
    ],
    "visual": "debug"
  },
  {
    "id": "04",
    "title": "기초가 중요하다는데, 그걸 언제 다 해요?",
    "tag": "내 문제부터 공부",
    "labels": [
      "내 기능",
      "막힌 질문",
      "기초 연결"
    ],
    "visual": "flow"
  },
  {
    "id": "05",
    "title": "포트폴리오는 멋진데, 왜 이 기술을 썼죠?",
    "tag": "기술 이름보다 선택 이유",
    "labels": [
      "요구 사항",
      "선택 이유",
      "더 단순하게"
    ],
    "visual": "flow"
  },
  {
    "id": "06",
    "title": "시험장에서는 왜 첫 줄부터 안 나올까?",
    "tag": "빈칸에서 시작하는 순서",
    "labels": [
      "예시 입력",
      "기대 출력",
      "처리 순서"
    ],
    "visual": "flow"
  },
  {
    "id": "07",
    "title": "작은 게임 하나가 생각보다 만만하지 않다",
    "tag": "작은 기능을 끝까지",
    "labels": [
      "판·입력",
      "충돌·고정",
      "줄 삭제"
    ],
    "visual": "board"
  },
  {
    "id": "08",
    "title": "왜 하필 거길 눌러? 그게 테스트입니다",
    "tag": "보여 준 장면 밖도 확인",
    "labels": [
      "정상 입력",
      "경계 조건",
      "반복 검사"
    ],
    "visual": "board"
  },
  {
    "id": "09",
    "title": "월급보다 먼저 나가는 AI 사용료",
    "tag": "사용료도 현실적인 문제",
    "labels": [
      "사용량",
      "재시도",
      "전체 비용"
    ],
    "visual": "bars"
  },
  {
    "id": "10",
    "title": "거의 다 됐는데, 왜 일이 안 끝날까?",
    "tag": "화면 동작 ≠ 업무 완료",
    "labels": [
      "완료 기준",
      "남은 작업",
      "도움 요청"
    ],
    "visual": "flow"
  },
  {
    "id": "11",
    "title": "선배님은 이미 취업하셨잖아요",
    "tag": "AI 없이도 다시 시작",
    "labels": [
      "빈 파일",
      "직접 구현",
      "로컬 실행"
    ],
    "visual": "flow"
  },
  {
    "id": "12",
    "title": "내가 끝낸 작은 일은 남습니다",
    "tag": "내가 끝낸 작은 일",
    "labels": [
      "작게 시작",
      "검증·완료",
      "내 말로 설명"
    ],
    "visual": "flow"
  }
] as const;

export const DRAFT_DURATIONS: readonly number[] = [61.4,64.73333333333333,59.266666666666666,64,62,76.86666666666666,64.13333333333334,62.7,83.86666666666666,91.46666666666667,82.9,77.7];
export const DRAFT_STARTS: readonly number[] = [0,61.4,126.13333333333334,185.4,249.4,311.4,388.26666666666665,452.4,515.1,598.9666666666667,690.4333333333333,773.3333333333334];
