# AI 뉴스 브리핑 프로젝트

Claude Code 및 AI 코딩 도구의 일일 변경사항을 수집하는 JSON 수집 파이프라인.
수집된 데이터는 **Obsidian 뉴스 Routine**이 읽어 볼트에 노트로 저장한다.

> ℹ️ **카카오톡 전송은 폐기됨(deprecated).** 결과 소비는 Obsidian Routine이 대체.
> 이 저장소는 GitHub Actions로 커뮤니티 소스를 수집해
> `data/daily-community.json`을 생성하는 역할만 담당한다.

## 파일 구조

```
.
├── CLAUDE.md              # 프로젝트 문서 (이 파일)
├── briefing-prompt.md     # 브리핑 실행 프롬프트 (수집·검증·정리 로직)
├── source-access-map.md   # 출처별 접근 방법 맵
├── scripts/
│   └── collect_community_news.py   # 커뮤니티 소스 RSS/Atom 수집기
└── data/
    └── daily-community.json         # 수집 결과 (Obsidian Routine이 소비)
```

## 실행 방법

- **자동**: GitHub Actions(`.github/workflows/collect-community-news.yml`)가
  정기 실행해 `data/daily-community.json`을 갱신 → Obsidian Routine이 읽어 노트화.
- **수동 브리핑 로직**: `briefing-prompt.md`의 지시를 따라 수집·검증·정리 수행.

## 핵심 제약사항

- **403 차단 사이트**: `source-access-map.md` 참고 (Atom 피드 / WebSearch 우선)
- **24시간 필터 필수**: 날짜 미확인 항목 제외
