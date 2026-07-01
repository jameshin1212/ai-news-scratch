#!/usr/bin/env python3
"""
커뮤니티 뉴스 수집기 — GitHub Actions에서 실행 (완전한 인터넷 접근)
수집 범위: Reddit, Hacker News, Simon Willison, GeekNews(hada.io)
출력: data/daily-community.json (Claude Code Routine이 읽음)
"""

import json
import urllib.request
import urllib.error
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

SOURCES = {
    "reddit_ClaudeAI": {
        "url": "https://www.reddit.com/r/ClaudeAI/new/.rss?limit=30",
        "type": "atom",
        "label": "Reddit r/ClaudeAI",
    },
    "reddit_LocalLLaMA": {
        "url": "https://www.reddit.com/r/LocalLLaMA/new/.rss?limit=30",
        "type": "atom",
        "label": "Reddit r/LocalLLaMA",
    },
    "hn_frontpage": {
        "url": "https://news.ycombinator.com/rss",
        "type": "rss",
        "label": "Hacker News",
    },
    "simonwillison": {
        "url": "https://simonwillison.net/atom/everything/",
        "type": "atom",
        "label": "Simon Willison",
    },
    "hada_io": {
        "url": "https://news.hada.io/rss",
        "type": "rss",
        "label": "GeekNews (하다)",
    },
    # ── AI/Tech 신뢰 소스 확장 (2026-06-30, 소스 화이트리스트 = 품질 1차 필터) ──
    "hn_ask": {
        "url": "https://hnrss.org/newest?points=100",
        "type": "rss",
        "label": "Hacker News (100+ points)",
    },
    "verge": {
        "url": "https://www.theverge.com/rss/index.xml",
        "type": "atom",
        "label": "The Verge",
    },
    "techcrunch": {
        "url": "https://techcrunch.com/feed/",
        "type": "rss",
        "label": "TechCrunch",
    },
    "reddit_technology": {
        "url": "https://www.reddit.com/r/technology/top/.rss?limit=25&t=day",
        "type": "atom",
        "label": "Reddit r/technology",
    },
    "reddit_startups": {
        "url": "https://www.reddit.com/r/startups/top/.rss?limit=25&t=day",
        "type": "atom",
        "label": "Reddit r/startups",
    },
    "producthunt": {
        "url": "https://www.producthunt.com/feed",
        "type": "atom",
        "label": "Product Hunt",
    },
}

KEYWORDS = [
    "claude", "anthropic", "codex", "openai", "llm", "ai coding",
    "mcp", "agentic", "claude code", "cursor", "copilot",
    "클로드", "앤트로픽", "코덱스",
]


def fetch_url(url: str, timeout: int = 15) -> bytes | None:
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error ({type(e).__name__}): {url} — {e}", file=sys.stderr)
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

            pub_date = _text("published") or _text("updated")
            dt = parse_date(pub_date)
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

    for key, cfg in SOURCES.items():
        print(f"Fetching {cfg['label']} ...", file=sys.stderr)
        raw = fetch_url(cfg["url"])
        if raw is None:
            result["sources"][key] = {"error": "fetch_failed", "items": []}
            continue

        filter_relevance = key in ("hn_frontpage",)  # HN만 키워드 필터 적용
        if cfg["type"] == "atom":
            items = parse_atom(raw, cfg["label"], cutoff, filter_relevance)
        else:
            items = parse_rss(raw, cfg["label"], cutoff, filter_relevance)

        print(f"  → {len(items)} items within 24h", file=sys.stderr)
        result["sources"][key] = {"label": cfg["label"], "items": items}

    output_path = "data/daily-community.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    total = sum(len(v.get("items", [])) for v in result["sources"].values())
    print(f"\n✅ Saved {total} items to {output_path}")

    # Print summary
    for key, data in result["sources"].items():
        items = data.get("items", [])
        err = data.get("error", "")
        status = f"ERROR: {err}" if err else f"{len(items)} items"
        print(f"  {data.get('label', key)}: {status}")


if __name__ == "__main__":
    main()
