# 출처별 접근 방법 맵

> 마지막 검증일: 2026-05-26  
> ✅ = WebFetch 직접 접근 가능 | ⚠️ = WebSearch 우회 | ❌ = 차단됨

---

## 핵심 원칙

**WebFetch는 GitHub/Raw/code.claude.com만 신뢰 가능**  
그 외 모든 미디어 사이트(TechCrunch, Verge, Anthropic.com 포함)는 거의 항상 403.  
→ **WebSearch가 주력 수집 도구**다. 스니펫 날짜+내용으로 1차 검증 후 개별 URL WebFetch 재시도.

---

## 1. Atom 피드 (WebFetch ✅ — 날짜 확인 최신호)

| 소스 | URL |
|------|-----|
| Claude Code 릴리즈 | `https://github.com/anthropics/claude-code/releases.atom` |
| OpenAI Codex 릴리즈 | `https://github.com/openai/codex/releases.atom` |

→ `<published>` 태그로 정확한 날짜 확인.

---

## 2. Raw 구조화 데이터 (WebFetch ✅)

| 소스 | URL |
|------|-----|
| Claude Code CHANGELOG | `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` |
| Claude Code 변경로그 페이지 | `https://code.claude.com/docs/en/changelog` |
| Claude Code What's New | `https://code.claude.com/docs/en/whats-new` |
| Claude Code 모범 사례 | `https://code.claude.com/docs/en/best-practices` |
| npm 패키지 메타 | `https://registry.npmjs.org/@anthropic-ai/claude-code` |

---

## 3. 빠른 미디어 소스 — WebSearch 우회 전략

### 3-1. 해외 속보 미디어 (WebSearch 전용)

검색이 실패하면 다음 쿼리를 순서대로 시도:

```
# 1순위: 정확한 날짜 검색
WebSearch: "claude code" OR "anthropic" site:techcrunch.com OR site:venturebeat.com OR site:bleepingcomputer.com "May 25" OR "May 26" 2026

# 2순위: 최근 24h 포괄 검색  
WebSearch: anthropic claude code release announcement May 2026 -site:youtube.com

# 3순위: 시만 윌리슨 최신 글
WebSearch: site:simonwillison.net claude OR codex 2026 May

# 4순위: InfoQ, The Verge, Ars Technica, MIT Tech Review
WebSearch: "claude code" OR "anthropic" site:infoq.com OR site:theverge.com OR site:arstechnica.com 2026
```

**신뢰도 순위:**
1. TechCrunch, MIT Technology Review, InfoQ — 높음
2. VentureBeat, Ars Technica, The Verge — 높음
3. BleepingComputer, CyberSecurityNews — 보안 이슈 한정 신뢰
4. TechTimes, 3차 요약 블로그 — **제외**
5. Medium (공식 계정 아닌 경우) — **제외**

### 3-2. Simon Willison (빠른 AI 인사이트)

```
WebSearch: site:simonwillison.net "May 25" OR "May 26" 2026
```
→ AI 코딩 도구·에이전트 관련 포스트만 선별 (AI 정책, 윤리 등 제외).

### 3-3. Hacker News

```
WebSearch: site:news.ycombinator.com "claude code" OR "codex" OR "anthropic" 2026
```
→ 스니펫에서 날짜 + 핵심 논점 추출. 24h 이내 항목만.

---

## 4. 한국어 — GeekNews (news.hada.io)

news.hada.io 본체는 403 차단. **WebSearch만 사용.**

```
# 최신 Claude/AI 코딩 항목 탐색
WebSearch: site:news.hada.io claude OR anthropic OR codex 2026

# 오늘 날짜 한정 (날짜 표기가 되어 있을 때)
WebSearch: news.hada.io 클로드 코드 앤트로픽 2026년 5월 25일 OR 26일

# 토픽 ID 기반 최신 항목 (최근 ID = 2만9천번대)
WebSearch: news.hada.io/topic?id=297 OR news.hada.io/topic?id=298 claude OR anthropic OR codex
```

→ 검색 결과 스니펫에서 제목, URL, 내용 추출. 날짜는 게시글 상단 시각 기준.

---

## 5. 날짜 검증 기준

| 소스 유형 | 날짜 확인 방법 |
|----------|--------------|
| GitHub Atom 피드 | `<published>` 태그 (UTC → KST +9h 변환) |
| CHANGELOG.md | 버전 헤더 날짜 |
| npm registry | `time.[버전]` 필드 |
| WebSearch 스니펫 | Google 날짜 표시 (상대적: "3 hours ago", "May 26") |
| URL 패턴 | `/2026/05/25/`, `20260525` 등 날짜 포함 URL |

---

## 6. 접근 불가 확정 목록 (WebSearch fallback 전환)

```
❌ anthropic.com/news          → WebSearch site:anthropic.com
❌ anthropic.com/engineering   → WebSearch site:anthropic.com engineering
❌ claude.com/blog             → WebSearch site:anthropic.com blog
❌ openai.com/index/           → WebSearch site:openai.com codex
❌ simonwillison.net (개별 URL) → WebSearch site:simonwillison.net
❌ techcrunch.com              → WebSearch site:techcrunch.com
❌ venturebeat.com             → WebSearch site:venturebeat.com
❌ theverge.com                → WebSearch
❌ news.hada.io                → WebSearch site:news.hada.io
❌ reddit.com                  → 접근 자체 불가, 제외
❌ hn.algolia.com API          → WebSearch fallback
```
