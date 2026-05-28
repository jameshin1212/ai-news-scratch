# 출처별 접근 방법 맵

> 마지막 검증일: 2026-05-28 (전수 테스트 완료)
> ✅ = WebFetch 직접 접근 가능 | ⚠️ = 부분 가능 | ❌ = 차단됨 | 🚫 = 시스템 레벨 차단

---

## 1차 공식 출처

### Claude Code (Anthropic)

| 용도 | URL | 상태 | 접근 방법 | 비고 |
|------|-----|------|-----------|------|
| 릴리즈 Atom 피드 | `https://github.com/anthropics/claude-code/releases.atom` | ✅ | WebFetch 직접 | 날짜·내용 가장 신뢰 |
| CHANGELOG.md | `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | ✅ | WebFetch 직접 | |
| Changelog 페이지 | `https://code.claude.com/docs/en/changelog` | ✅ | WebFetch 직접 | |
| What's New 페이지 | `https://code.claude.com/docs/en/whats-new` | ✅ | WebFetch 직접 | 주간 다이제스트 |
| Best Practices | `https://code.claude.com/docs/en/best-practices` | ✅ | WebFetch 직접 | 팁 섹션 상시 소스 |
| npm 최신 버전 | `https://registry.npmjs.org/@anthropic-ai/claude-code/latest` | ⚠️ | WebFetch 직접 | 버전명 확인 가능, **날짜 필드 불안정** — 릴리즈 날짜는 Atom 피드 우선 사용 |
| 뉴스 인덱스 | `https://www.anthropic.com/news` | ❌ 403 | WebSearch fallback | |
| 엔지니어링 블로그 | `https://www.anthropic.com/engineering` | ❌ 403 | WebSearch fallback | |
| 공식 블로그 | `https://www.claude.com/blog` | ❌ 403 | WebSearch fallback | |

### OpenAI Codex

| 용도 | URL | 상태 | 접근 방법 | 비고 |
|------|-----|------|-----------|------|
| 릴리즈 Atom 피드 | `https://github.com/openai/codex/releases.atom` | ✅ | WebFetch 직접 | 날짜·내용 가장 신뢰 |
| Codex 뉴스 인덱스 | `https://openai.com/index/` | ❌ 403 | WebSearch fallback | |
| Developer Changelog | `https://developers.openai.com/codex/changelog` | ❌ 403 | WebSearch fallback | |

---

## 2차 실무 출처

| 출처 | URL | 상태 | 접근 방법 | 비고 |
|------|-----|------|-----------|------|
| Simon Willison 블로그 | `https://simonwillison.net/` | ❌ 403 | `WebSearch site:simonwillison.net` | |
| Simon Willison Atom | `https://simonwillison.net/atom.xml` | ❌ 403 | WebSearch fallback | |
| Hacker News | `https://news.ycombinator.com/` | ❌ 403 | `WebSearch site:news.ycombinator.com` | |
| HN Algolia API | `https://hn.algolia.com/api/v1/search_by_date?...` | ❌ 403 | WebSearch fallback | API 인증 필요로 추정 |
| Reddit r/ClaudeAI | `https://www.reddit.com/r/ClaudeAI/new.json` | 🚫 시스템 차단 | WebSearch fallback | Claude Code 레벨 차단 |
| Reddit r/LocalLLaMA | `https://www.reddit.com/r/LocalLLaMA/new.json` | 🚫 시스템 차단 | WebSearch fallback | Claude Code 레벨 차단 |

---

## 한국어 커뮤니티 출처 (🟨 KR 섹션)

### GeekNews (news.hada.io)

| URL | 상태 | 비고 |
|-----|------|------|
| `https://news.hada.io/new` | ❌ 403 | |
| `https://news.hada.io/rss` | ❌ 403 | |
| `https://news.hada.io/atom` | ❌ 403 | |
| `https://news.hada.io/topic?id=N` | ❌ 403 | |
| `https://news.hada.io/past?day=YYYY-MM-DD` | ❌ 403 | |

**접근 전략 (우선순위순)**

1. `WebSearch "news.hada.io" claude code OR AI 코딩 "날짜"` — 제한적 효과
2. **사용자가 Slack(#technews)에서 붙여넣은 GeekNews 내용 직접 처리** — 가장 신뢰
3. 원본 출처 URL(HN item, 원문 블로그 등)을 대신 사용 — URL 없으면 항목 제외

**필터 기준 (포함 대상)**
- Claude Code, Anthropic, OpenAI Codex, AI 코딩 도구 관련 항목만

---

## WebSearch 우회 전략

### Anthropic 뉴스
```
WebSearch: 'site:anthropic.com "May 27" OR "May 28" 2026'
→ 스니펫 날짜 확인 → 해당 URL WebFetch 재시도
```

### OpenAI Codex
```
WebSearch: 'openai codex "May 27" OR "May 28" 2026 release'
→ 스니펫 날짜 확인
```

### Simon Willison
```
WebSearch: 'site:simonwillison.net claude code 2026'
→ URL 패턴 /YYYY/Mon/DD/ 으로 날짜 직접 확인
→ 개별 URL WebFetch 재시도 (403 반환됨, WebSearch 스니펫 활용)
```

### Hacker News
```
WebSearch: 'site:news.ycombinator.com "claude code" OR "codex" 2026'
→ item?id= URL 패턴 확인
```

### Reddit (차단됨 — WebSearch 대체)
```
WebSearch: 'site:reddit.com r/ClaudeAI "claude code" 2026'
WebSearch: 'site:reddit.com r/LocalLLaMA "claude code" OR "codex" 2026'
```

---

## 날짜 검증 방법

| 소스 유형 | 날짜 필드 | 신뢰도 |
|-----------|-----------|--------|
| GitHub Atom 피드 | `<published>` 태그 | ★★★ 최고 |
| CHANGELOG.md 헤더 | 버전 옆 날짜 문자열 | ★★★ 최고 |
| npm `/latest` 엔드포인트 | `_time` 내부 필드 | ★☆☆ 낮음 — Atom 피드 우선 |
| WebSearch 스니펫 | Google 날짜 표시 | ★★☆ 중간 — 1차 필터용 |
| WebSearch 결과 URL | simonwillison.net/YYYY/Mon/DD/ 패턴 | ★★★ 최고 |
