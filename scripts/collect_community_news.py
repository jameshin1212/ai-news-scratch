#!/usr/bin/env python3
"""
커뮤니티·공식 뉴스 수집기 — GitHub Actions에서 실행 (완전한 인터넷 접근)
수집 범위: Reddit, Hacker News, 공식 매체(Verge/TechCrunch/Ars 등), 국내(GeekNews/
          VentureSquare/Platum/knews 집계), Google News RSS(한국어 카테고리).
각 소스는 tier(community|official)·category 메타를 가짐.
출력: data/daily-community.json (Claude Code Routine이 읽음)

⚠️ Reddit 미인증 .rss 는 데이터센터 IP(GitHub Actions)에서 rate limit(429)에 걸리기 쉬움.
   → Reddit 요청 사이 throttle + 429 지수백오프 재시도로 완화(완전 해결은 아님).
   상세 진단: source-access-map.md 참고.
"""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import sys
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/atom+xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Reddit은 고유 UA를 요구하며, 브라우저 UA보다 봇-형식 UA에 덜 공격적임.
REDDIT_UA = "web:ai-news-scratch:v1.0 (by /u/jameshin1212)"
REDDIT_THROTTLE_SEC = 8     # Reddit 요청 사이 간격 (rate limit 완화)
MAX_RETRIES = 3             # 429 시 지수백오프 재시도 횟수

# tier: "community" = 커뮤니티성 정보(개인·토론·투표 기반, 검증 필요)
#       "official"  = 공식·전문 매체(1차 소스·저널리즘)
# category: 뉴스 카테고리 목록 SSOT와 매핑 (Obsidian Routine이 분류 힌트로 사용)
SOURCES = {
    # ── 커뮤니티 소스 (Reddit / Hacker News) ──
    "reddit_ClaudeAI": {
        "url": "https://www.reddit.com/r/ClaudeAI/new/.rss?limit=30",
        "type": "atom", "tier": "community", "category": "AI",
        "label": "Reddit r/ClaudeAI",
    },
    "reddit_LocalLLaMA": {
        "url": "https://www.reddit.com/r/LocalLLaMA/new/.rss?limit=30",
        "type": "atom", "tier": "community", "category": "AI",
        "label": "Reddit r/LocalLLaMA",
    },
    "reddit_technology": {
        "url": "https://www.reddit.com/r/technology/top/.rss?limit=25&t=day",
        "type": "atom", "tier": "community", "category": "IT·Tech",
        "label": "Reddit r/technology",
    },
    "reddit_startups": {
        "url": "https://www.reddit.com/r/startups/top/.rss?limit=25&t=day",
        "type": "atom", "tier": "community", "category": "창업·스타트업",
        "label": "Reddit r/startups",
    },
    # 사용자 요청 채널: SideProject / iosapps / ObsidianMD (멀티 결합 = 1요청)
    "reddit_makers": {
        "url": "https://www.reddit.com/r/SideProject+iosapps+ObsidianMD.rss?limit=40",
        "type": "atom", "tier": "community", "category": "New App",
        "label": "Reddit r/SideProject+iosapps+ObsidianMD",
    },
    "hn_frontpage": {
        "url": "https://news.ycombinator.com/rss",
        "type": "rss", "tier": "community", "category": "IT·Tech",
        "label": "Hacker News",
    },
    "hn_ask": {
        "url": "https://hnrss.org/newest?points=100",
        "type": "rss", "tier": "community", "category": "IT·Tech",
        "label": "Hacker News (100+ points)",
    },
    "producthunt": {
        "url": "https://www.producthunt.com/feed",
        "type": "atom", "tier": "community", "category": "New App",
        "label": "Product Hunt",
    },
    # ── 공식·전문 매체 소스 ──
    "simonwillison": {
        "url": "https://simonwillison.net/atom/everything/",
        "type": "atom", "tier": "official", "category": "AI",
        "label": "Simon Willison",
    },
    "hada_io": {
        # 정답 피드는 /rss/news (Atom). /rss 는 301→403.
        "url": "https://news.hada.io/rss/news",
        "type": "atom", "tier": "official", "category": "IT·Tech",
        "label": "GeekNews (하다)",
    },
    "verge": {
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "atom", "tier": "official", "category": "IT·Tech",
        "label": "The Verge",
    },
    "techcrunch": {
        "url": "https://techcrunch.com/feed/",
        "type": "rss", "tier": "official", "category": "IT·Tech",
        "label": "TechCrunch",
    },
    # ── 소스 확장 (2026-07-01, 카테고리 커버리지 균형) ──
    "huggingface": {
        "url": "https://huggingface.co/blog/feed.xml",
        "type": "atom", "tier": "official", "category": "AI",
        "label": "Hugging Face Blog",
    },
    "venturesquare": {
        "url": "https://www.venturesquare.net/feed",
        "type": "rss", "tier": "official", "category": "창업·스타트업",
        "label": "VentureSquare",
    },
    "platum": {
        "url": "https://platum.kr/feed",
        "type": "rss", "tier": "official", "category": "창업·스타트업",
        "label": "Platum",
    },
    "knews_tech": {
        "url": "https://akngs.github.io/knews-rss/categories/tech.xml",
        "type": "rss", "tier": "official", "category": "IT·Tech",
        "label": "knews-rss (국내 Tech 집계)",
    },
    "fourohfour_media": {
        "url": "https://www.404media.co/rss/",
        "type": "rss", "tier": "official", "category": "IT·Tech",
        "label": "404 Media",
    },
    "ars_technica": {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "type": "rss", "tier": "official", "category": "IT·Tech",
        "label": "Ars Technica",
    },
    "art_newspaper": {
        "url": "https://www.theartnewspaper.com/rss.xml",
        "type": "rss", "tier": "official", "category": "예술",
        "label": "The Art Newspaper",
    },
    "rollingstone_music": {
        "url": "https://www.rollingstone.com/music/feed/",
        "type": "rss", "tier": "official", "category": "연예",
        "label": "Rolling Stone Music",
    },
    # ── Google News RSS (한국어 카테고리 커버리지, when:Nd 신선도 필터) ──
    "gnews_ai_kr": {
        "url": "https://news.google.com/rss/search?q=(생성형+AI+OR+LLM+OR+AI+에이전트)+when:3d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "AI",
        "label": "Google News AI (한국어)",
    },
    "gnews_ent_kr": {
        "url": "https://news.google.com/rss/search?q=(K-pop+OR+드라마+OR+영화+OR+컴백)+when:2d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "연예",
        "label": "Google News 연예 (한국어)",
    },
    "gnews_art_kr": {
        "url": "https://news.google.com/rss/search?q=(전시+OR+비엔날레+OR+아트페어+OR+미술관)+when:7d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "예술",
        "label": "Google News 예술 (한국어)",
    },
    "gnews_culture_kr": {
        "url": "https://news.google.com/rss/search?q=(출판+OR+라이프스타일+OR+트렌드+OR+전시회)+when:7d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "문화",
        "label": "Google News 문화 (한국어)",
    },
    # ── 정치 (2026-07-01) — 국내/국외 서브카테고리 ──
    "gnews_politics_kr": {
        "url": "https://news.google.com/rss/search?q=정치+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "정치", "subcategory": "국내",
        "label": "Google News 정치 국내 (한국어)",
    },
    "gnews_politics_intl_kr": {
        "url": "https://news.google.com/rss/search?q=(국제+OR+트럼프+OR+미국정치)+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "정치", "subcategory": "국외",
        "label": "Google News 정치 국외 (한국어)",
    },
    "bbc_politics": {
        "url": "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "type": "rss", "tier": "official", "category": "정치", "subcategory": "국외",
        "label": "BBC Politics",
    },
    # ── 스포츠 (2026-07-01) — 축구/농구/E-Sport 서브카테고리 ──
    "gnews_football_kr": {
        "url": "https://news.google.com/rss/search?q=(축구+OR+손흥민+OR+K리그)+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "스포츠", "subcategory": "축구",
        "label": "Google News 축구 (한국어)",
    },
    "bbc_football": {
        "url": "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "type": "rss", "tier": "official", "category": "스포츠", "subcategory": "축구",
        "label": "BBC Sport Football",
    },
    "gnews_basketball_kr": {
        "url": "https://news.google.com/rss/search?q=(NBA+OR+KBL+OR+농구)+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "스포츠", "subcategory": "농구",
        "label": "Google News 농구 (한국어)",
    },
    "bbc_basketball": {
        # ESPN NBA RSS는 item 1개+EST 타임존 파싱 실패로 제외. BBC가 안정적.
        "url": "https://feeds.bbci.co.uk/sport/basketball/rss.xml",
        "type": "rss", "tier": "official", "category": "스포츠", "subcategory": "농구",
        "label": "BBC Basketball",
    },
    "gnews_esports_kr": {
        "url": "https://news.google.com/rss/search?q=(e스포츠+OR+LCK+OR+롤드컵+OR+발로란트)+when:1d&hl=ko&gl=KR&ceid=KR:ko",
        "type": "rss", "tier": "official", "category": "스포츠", "subcategory": "E-Sport",
        "label": "Google News e스포츠 (한국어)",
    },
    "dotesports": {
        "url": "https://dotesports.com/feed",
        "type": "rss", "tier": "official", "category": "스포츠", "subcategory": "E-Sport",
        "label": "Dot Esports",
    },
}

KEYWORDS = [
    "claude", "anthropic", "codex", "openai", "llm", "ai coding",
    "mcp", "agentic", "claude code", "cursor", "copilot",
    "클로드", "앤트로픽", "코덱스",
]


def encode_url(url: str) -> str:
    """URL의 비ASCII 문자(한글 쿼리 등)를 percent-encode. 이미 인코딩된 부분은 보존."""
    return urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")


def fetch_url(url: str, timeout: int = 15, is_reddit: bool = False) -> bytes | None:
    url = encode_url(url)
    headers = dict(HEADERS)
    if is_reddit:
        headers["User-Agent"] = REDDIT_UA
    for attempt in range(MAX_RETRIES):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            # 429/503 은 rate limit → 지수백오프 후 재시도
            if e.code in (429, 503) and attempt < MAX_RETRIES - 1:
                wait = REDDIT_THROTTLE_SEC * (2 ** attempt)
                print(f"  HTTP {e.code} (retry {attempt + 1}/{MAX_RETRIES} in {wait}s): {url}",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  HTTP {e.code}: {url}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  Error ({type(e).__name__}): {url} — {e}", file=sys.stderr)
            return None
    return None


def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    date_str = date_str.strip()
    # ISO 8601 (Atom)
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%f%z"):
        try:
            dt = datetime.strptime(date_str[:25], fmt[:len(date_str[:25])])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass
    # Try Z suffix
    if date_str.endswith("Z"):
        try:
            dt = datetime.fromisoformat(date_str[:-1]).replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass
    # Try fromisoformat directly
    try:
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        pass
    # RFC 822 (RSS 2.0 pubDate)
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    return None


def is_relevant(title: str, summary: str = "") -> bool:
    """Claude/AI 코딩 도구 관련 여부 필터 (HN·Reddit에만 적용)"""
    text = (title + " " + summary).lower()
    return any(kw in text for kw in KEYWORDS)


def parse_atom(xml_bytes: bytes, source_label: str, cutoff: datetime, filter_relevance: bool) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(xml_bytes)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        if not entries:
            # Try without namespace
            entries = root.findall(".//entry")
            ns = {}

        for entry in entries:
            def _text(tag):
                el = entry.find(f"atom:{tag}", ns) if ns else entry.find(tag)
                return (el.text or "").strip() if el is not None else ""

            title = _text("title")
            summary = _text("summary") or _text("content")
            link_el = entry.find("atom:link", ns) if ns else entry.find("link")
            url = ""
            if link_el is not None:
                url = link_el.get("href", "") or link_el.text or ""

            # published·updated 중 더 최근 시각을 사용.
            # (Product Hunt 등은 published가 며칠 전이고 updated만 최신)
            dt_pub = parse_date(_text("published"))
            dt_upd = parse_date(_text("updated"))
            dt = max((d for d in (dt_pub, dt_upd) if d is not None), default=None)
            if dt is None or dt < cutoff:
                continue
            if filter_relevance and not is_relevant(title, summary):
                continue

            items.append({
                "title": title,
                "url": url,
                "summary": summary[:400],
                "date": dt.isoformat(),
                "source": source_label,
            })
    except ET.ParseError as e:
        print(f"  XML parse error: {e}", file=sys.stderr)
    return items


def parse_rss(xml_bytes: bytes, source_label: str, cutoff: datetime, filter_relevance: bool) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(xml_bytes)
        channel = root.find("channel")
        entries = channel.findall("item") if channel is not None else root.findall(".//item")

        for item in entries:
            def _text(tag):
                el = item.find(tag)
                return (el.text or "").strip() if el is not None else ""

            title = _text("title")
            url = _text("link") or _text("guid")
            summary = _text("description")
            pub_date = _text("pubDate")

            # Strip HTML tags from summary
            summary = re.sub(r"<[^>]+>", "", summary)[:400]

            dt = parse_date(pub_date)
            if dt is None or dt < cutoff:
                continue
            if filter_relevance and not is_relevant(title, summary):
                continue

            items.append({
                "title": title,
                "url": url,
                "summary": summary,
                "date": dt.isoformat(),
                "source": source_label,
            })
    except ET.ParseError as e:
        print(f"  XML parse error: {e}", file=sys.stderr)
    return items


def main():
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    result = {
        "collected_at": now.isoformat(),
        "cutoff": cutoff.isoformat(),
        "sources": {},
    }

    prev_reddit = False  # Reddit 소스 연속 호출 사이 throttle
    for key, cfg in SOURCES.items():
        is_reddit = key.startswith("reddit_")
        if is_reddit and prev_reddit:
            time.sleep(REDDIT_THROTTLE_SEC)  # Reddit rate limit 완화
        prev_reddit = is_reddit

        print(f"Fetching {cfg['label']} ...", file=sys.stderr)
        raw = fetch_url(cfg["url"], is_reddit=is_reddit)

        meta = {
            "label": cfg["label"],
            "tier": cfg.get("tier", "community"),
            "category": cfg.get("category", "기타"),
        }
        if cfg.get("subcategory"):
            meta["subcategory"] = cfg["subcategory"]
        if raw is None:
            result["sources"][key] = {**meta, "error": "fetch_failed", "items": []}
            continue

        filter_relevance = key in ("hn_frontpage",)  # HN만 키워드 필터 적용
        if cfg["type"] == "atom":
            items = parse_atom(raw, cfg["label"], cutoff, filter_relevance)
        else:
            items = parse_rss(raw, cfg["label"], cutoff, filter_relevance)

        # 각 아이템에도 tier·category·subcategory 부여 (Routine 분류 힌트)
        for it in items:
            it["tier"] = meta["tier"]
            it["category"] = meta["category"]
            if meta.get("subcategory"):
                it["subcategory"] = meta["subcategory"]

        print(f"  → {len(items)} items within 24h", file=sys.stderr)
        result["sources"][key] = {**meta, "items": items}

    output_path = "data/daily-community.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total = sum(len(v.get("items", [])) for v in result["sources"].values())
    n_official = sum(len(v.get("items", [])) for v in result["sources"].values()
                     if v.get("tier") == "official")
    n_community = total - n_official
    print(f"\n✅ Saved {total} items to {output_path} "
          f"(official: {n_official}, community: {n_community})")

    # Print summary (tier 표기)
    for key, data in result["sources"].items():
        items = data.get("items", [])
        err = data.get("error", "")
        status = f"ERROR: {err}" if err else f"{len(items)} items"
        tier = data.get("tier", "?")[:4]
        print(f"  [{tier}] {data.get('label', key)}: {status}")


if __name__ == "__main__":
    main()
