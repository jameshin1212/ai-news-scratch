# 출처별 접근 방법 맵

> 마지막 검증일: 2026-05-28  
> ✅ = WebFetch 직접 접근 가능 | ⚠️ = 우회 필요 | ❌ = 차단됨

---

## 1차 공식 출처

### Claude Code (Anthropic)

| 용도 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| 릴리즈 목록 | `https://github.com/anthropics/claude-code/releases.atom` | ✅ | WebFetch 직접 |
| 전체 변경로그 | `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | ✅ | WebFetch 직접 |
| What's New 페이지 | `https://code.claude.com/docs/en/whats-new` | ✅ | WebFetch 직접 |
| Changelog 페이지 | `https://code.claude.com/docs/en/changelog` | ✅ | WebFetch 직접 |
| npm 패키지 | `https://registry.npmjs.org/@anthropic-ai/claude-code` | ✅ | WebFetch 직접 |
| 뉴스 인덱스 | `https://www.anthropic.com/news` | ❌ | WebSearch fallback |
| 개별 뉴스 기사 | `https://www.anthropic.com/news/*` | ❌ | WebSearch snippet 활용 |
| 엔지니어링 블로그 | `https://www.anthropic.com/engineering` | ❌ | WebSearch fallback |

### OpenAI Codex

| 용도 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| 릴리즈 목록 | `https://github.com/openai/codex/releases.atom` | ✅ | WebFetch 직접 |
| Codex 뉴스 인덱스 | `https://openai.com/index/` | ❌ | WebSearch fallback |
| Developer changelog | `https://developers.openai.com/codex/changelog` | ❌ | WebSearch fallback |

---

---

## 한국어 커뮤니티 출처 (🟨 KR 섹션)

### GeekNews (news.hada.io)

| 용도 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| 최신 글 목록 | `https://news.hada.io/new` | ❌ | WebSearch fallback |
| RSS 피드 | `https://news.hada.io/rss` | ❌ | WebSearch fallback |
| Atom 피드 | `https://news.hada.io/atom` | ❌ | WebSearch fallback |
| 개별 토픽 | `https://news.hada.io/topic?id=N` | ❌ | WebSearch fallback |
| 지난 소식 | `https://news.hada.io/past?day=YYYY-MM-DD` | ❌ | WebSearch fallback |

**접근 전략 (우선순위순)**

1. `WebSearch "news.hada.io" claude code OR AI 코딩 OR anthropic "날짜"`
2. 사용자가 Slack(#technews 채널)에서 붙여넣은 GeekNews 내용 직접 처리
3. 원본 출처 URL(HN, 원문 블로그 등)을 대신 사용

**필터 기준**
- 포함: Claude Code, AI 코딩 도구, Anthropic, OpenAI Codex 관련 항목
- 제외: 폰트, CEO 뉴스, 구독 조언, 레드팀/보안, 무관 스타트업 뉴스 등

---

## 2차 실무 출처

| 출처 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| Simon Willison 블로그 | `https://simonwillison.net/` | ❌ | WebSearch `site:simonwillison.net` |
| Simon Willison 월별 아카이브 | `https://simonwillison.net/2026/May/` | ❌ | WebSearch fallback |
| Hacker News 프론트 | `https://news.ycombinator.com/` | ❌ | WebSearch `site:news.ycombinator.com` |
| HN Algolia API | `https://hn.algolia.com/api/v1/search_by_date?...` | ❌ | WebSearch fallback |

---

## WebSearch 우회 전략

### Anthropic 뉴스
```
WebSearch: 'site:anthropic.com "May 25" OR "May 26" 2026'
→ 검색 결과 스니펫에서 날짜·내용 추출
→ 해당 URL로 WebFetch 재시도 (일부 개별 기사는 접근 가능)
```

### Simon Willison
```
WebSearch: 'site:simonwillison.net claude code 2026'
→ 제목·날짜·스니펫 확인
→ 직접 WebFetch 가끔 성공하므로 개별 URL 재시도
```

### Hacker News
```
WebSearch: 'site:news.ycombinator.com "claude code" OR "codex" 2026'
→ 결과에서 날짜 포함 항목만 추출 (URL item?id= 패턴)
→ 개별 item URL WebFetch 시도 (항목별로 접근 가능할 수 있음)
```

---

## 날짜 검증 방법

접근 가능한 소스는 직접 날짜 확인:
- Atom 피드: `<updated>` 또는 `<published>` 태그
- CHANGELOG.md: 버전 헤더 날짜
- npm registry: `time` 필드

WebSearch 스니펫은 Google 날짜 표시로 1차 필터 후 본문 확인.
