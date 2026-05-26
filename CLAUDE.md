# AI 뉴스 브리핑 프로젝트

Claude Code 및 AI 코딩 도구의 일일 변경사항을 수집해 카카오톡 메모채팅으로 전송하는 자동화 브리핑 시스템.

## 파일 구조

```
.
├── CLAUDE.md              # 프로젝트 문서 (이 파일)
├── briefing-prompt.md     # 브리핑 실행 프롬프트 (메인 로직)
└── source-access-map.md   # 출처별 접근 방법 맵
```

## 실행 방법

Claude Code 세션에서 아래 명령을 실행:

```
briefing-prompt.md 의 지시를 따라 일일 브리핑을 실행하고 카카오톡으로 전송해줘
```

## 핵심 제약사항

- **KakaotalkChat 200자 제한**: 섹션별로 분할 전송
- **403 차단 사이트**: `source-access-map.md` 참고 (Atom 피드 / WebSearch 우선)
- **24시간 필터 필수**: 날짜 미확인 항목 전송 금지
