# 출처별 접근 방법 맵

> 마지막 검증일: 2026-07-01
> ✅ = WebFetch 직접 접근 가능 | ⚠️ = WebSearch 우회 필요 | ❌ = 완전 차단

---

## GitHub Actions 수집기 안정성 진단 (2026-07-01)

`scripts/collect_community_news.py`는 GitHub Actions(데이터센터 IP)에서 RSS/Atom을
직접 페치한다. 실측 재현 결과 소스별 특성:

| 구분 | 소스 | 원인 | 대응 |
|------|------|------|------|
| ⚠️ 구조적 | Reddit 미인증 `.rss` | 데이터센터 IP + 요청당 rate limit(429) 즉시 소진 → 실행마다 일부만 통과 | throttle(8s)+429 지수백오프 재시도. **완전 해결 불가**(부분 수집 허용) |
| ✅ 해결됨 | hada.io | `news.hada.io/rss` → 301→403. **정답은 `/rss/news`(Atom)** | URL·type 수정 완료 |
| ✅ 해결됨 | Product Hunt | `published`가 며칠 전 → 24h 필터 탈락. `updated`가 최신 | published·updated 중 **최신 시각 사용**으로 수정 |
| ✅ 해결됨 | Google News(한국어) | URL 내 한글 → urllib ascii 인코딩 실패 | `urllib.parse.quote`로 percent-encode |
| ℹ️ 정상 | Hugging Face Blog | 저빈도 블로그라 24h 내 0건인 날 존재 | 에러 아님 |

**결론**: Reddit을 제외하면 현 GitHub Actions 구성으로 안정 수집 가능.
Reddit 안정성이 중요하면 로컬 cron(주거 IP) 전환 또는 OAuth API(100 QPM) 고려.

### tier / category 메타
각 소스는 `tier`(community|official)·`category`(뉴스 카테고리 SSOT) 메타를 가지며,
JSON의 소스·아이템 양쪽에 부여된다. Obsidian Routine이 커뮤니티성 정보와
공식·전문 매체를 구분하고 카테고리 분류 힌트로 사용한다.

### Google News RSS 패턴 (한국어 카테고리 확장의 핵심)
`https://news.google.com/rss/search?q={키워드}+when:{N}d&hl=ko&gl=KR&ceid=KR:ko`
- `when:3d` 등 시간 필터 작동. 임의 한국어 주제를 즉석 피드화.
- 한계: 원문 아닌 집계 링크 + 제목·스니펫만 → 중복 제거 필요.

---

## 왜 차단되는가?

이 브리핑은 Claude Code **원격 클라우드 환경**에서 실행된다.
모든 아웃바운드 요청은 `127.0.0.1:41039` 보안 프록시를 경유하며, 이 프록시가
GitHub·npm·공식 문서 외 소셜/커뮤니티 도메인을 egress 정책으로 차단한다.

**영향 범위**: reddit.com, simonwillison.net, news.ycombinator.com,
hnrss.org, hn.algolia.com, news.hada.io 등 개인 블로그·커뮤니티 사이트 전체.
RSS 피드(.rss, .atom)도 같은 도메인이므로 동일하게 차단됨.

**중요**: WebSearch 도구는 Anthropic 내부 경로를 사용하므로 프록시 차단과 무관하게 동작.
→ **B·C 카테고리 소스는 WebSearch만 사용 가능**

---

## 1차 공식 출처 (A 카테고리)

### Claude Code (Anthropic)

| 용도 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| 릴리즈 목록 | `https://github.com/anthropics/claude-code/releases.atom` | ✅ | WebFetch 직접 |
| 전체 변경로그 | `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | ✅ | WebFetch 직접 |
| What's New | `https://code.claude.com/docs/en/whats-new` | ✅ | WebFetch 직접 |
| Changelog | `https://code.claude.com/docs/en/changelog` | ✅ | WebFetch 직접 |
| npm 패키지 | `https://registry.npmjs.org/@anthropic-ai/claude-code` | ✅ | WebFetch 직접 |
| Platform 릴리즈 | `https://platform.claude.com/docs/en/release-notes/overview` | ✅ | WebFetch 직접 |
| Best Practices | `https://code.claude.com/docs/en/best-practices` | ✅ | WebFetch 직접 (팁 소스) |
| 뉴스 인덱스 | `https://www.anthropic.com/news` | ⚠️ | WebSearch 필수 |
| 개별 뉴스 기사 | `https://www.anthropic.com/news/*` | ⚠️ | WebSearch snippet 활용 |
| 엔지니어링 블로그 | `https://www.anthropic.com/engineering` | ⚠️ | WebSearch 필수 |

### Claude Apps 릴리즈 노트 (Trusted Devices 등 앱 기능)

| 용도 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| Claude Apps 릴리즈 | `https://support.claude.com/en/articles/12138966-release-notes` | ⚠️ | WebSearch 필수 (403 차단) |

### OpenAI Codex

| 용도 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| 릴리즈 목록 | `https://github.com/openai/codex/releases.atom` | ✅ | WebFetch 직접 |
| 뉴스 인덱스 | `https://openai.com/index/` | ⚠️ | WebSearch 필수 |
| Developer changelog | `https://developers.openai.com/codex/changelog` | ⚠️ | WebSearch 필수 |

---

## 2차 실무 출처 (B 카테고리) — WebSearch 전용

| 출처 | RSS/Atom URL | 프록시 상태 | 접근 방법 |
|------|-------------|-----------|-----------|
| Simon Willison 블로그 | `simonwillison.net/atom/everything/` | ❌ 차단 | `WebSearch site:simonwillison.net` |
| Hacker News 프론트 | `news.ycombinator.com/rss` | ❌ 차단 | `WebSearch site:news.ycombinator.com` |
| HN Algolia API | `hn.algolia.com/api/v1/search_by_date` | ❌ 차단 | WebSearch fallback |
| hnrss.org (대안) | `hnrss.org/frontpage` | ❌ 차단 | WebSearch fallback |
| Reddit r/ClaudeAI | `reddit.com/r/ClaudeAI/.rss` | ❌ 차단 | `WebSearch site:reddit.com/r/ClaudeAI` |
| Reddit r/LocalLLaMA | `reddit.com/r/LocalLLaMA/.rss` | ❌ 차단 | `WebSearch site:reddit.com/r/LocalLLaMA` |

---

## 3차 한국어 출처 (C 카테고리) — WebSearch 전용

| 출처 | URL | 상태 | 접근 방법 |
|------|-----|------|-----------|
| GeekNews (하다) | `https://news.hada.io/rss/news` (Atom) | ✅ 직접 | 수집기가 직접 페치 (`/rss`는 403, `/rss/news`가 정답) |

---

## WebSearch 최적화 전략

### 날짜 지정 쿼리 패턴 (가장 중요)

```
오늘: 2026-06-29, 어제: 2026-06-28
```

```
# Anthropic 공식 뉴스 (날짜 지정)
WebSearch: 'site:anthropic.com "June 28" OR "June 29" 2026'
→ 스니펫 날짜·내용 추출 → 개별 URL WebFetch 재시도

# Claude App 릴리즈 노트 (Trusted Devices 등)
WebSearch: 'site:support.claude.com release notes "June 2026"'

# Claude Code 업데이트 (날짜 지정)
WebSearch: 'Claude Code update release "June 28" OR "June 29" 2026'

# Simon Willison (날짜 지정)
WebSearch: 'site:simonwillison.net claude "June 28" OR "June 29" 2026'
→ 결과 없으면: 'simonwillison.net claude code june 2026'

# HN 오늘자 Claude 관련
WebSearch: 'site:news.ycombinator.com claude 2026-06-28 OR 2026-06-29'

# Reddit ClaudeAI 최신
WebSearch: 'site:reddit.com/r/ClaudeAI claude code june 28 29 2026'

# GeekNews 한국어
WebSearch: 'site:news.hada.io claude anthropic june 2026'
```

### WebSearch 결과 신뢰도 판정

| 결과 유형 | 신뢰도 | 처리 방법 |
|----------|--------|----------|
| 공식 도메인 스니펫 (anthropic.com, openai.com) | 높음 | URL 추출 후 WebFetch 재시도 |
| 뉴스 스니펫 (날짜 명시됨) | 중간 | 스니펫 출처 명시하고 사용 |
| "X days ago" 상대 날짜 | 낮음 | 날짜 계산 후 24h 필터 적용 |
| 날짜 없음 | 제외 | 즉시 폐기 |
| 3차 요약 사이트 (Medium, TechTimes 등) | 제외 | 즉시 폐기 |

---

## 날짜 검증 방법

**WebFetch 접근 가능 소스 (신뢰)**:
- Atom 피드: `<published>` 또는 `<updated>` 태그 직접 확인
- CHANGELOG.md: 버전 헤더 날짜 (`## 2026-06-29`)
- Platform release notes: `### June 29, 2026` 헤더 패턴

**WebSearch 스니펫 소스 (주의)**:
- Google 검색결과 날짜 표시는 오류 있을 수 있음
- 가능하면 해당 URL을 WebFetch로 재확인
- "1 day ago" 형식은 오늘 날짜 기준으로 계산

---

## 로컬 실행 전환 시 추가 가능한 소스

> 이 브리핑을 로컬 머신에서 Claude Code cron으로 실행하면 아래 소스 전부 접근 가능.

```
✅ reddit.com/r/ClaudeAI/new/.rss?limit=25
✅ reddit.com/r/LocalLLaMA/new/.rss?limit=25
✅ simonwillison.net/atom/everything/
✅ hnrss.org/newest?q=claude+code&points=20
✅ news.hada.io/rss
✅ Playwright + Chrome 프로필로 인증 필요 사이트 접근
```
