#!/bin/bash
# 로컬 매시간 뉴스 수집 러너 (launchd에서 호출)
# GitHub Actions schedule이 매시간 실행을 자주 누락해, 로컬 cron으로 대체.
# 수집 → data/daily-community.json 갱신 → pull(rebase) → commit → push.
#
# ⚠️ 로컬 python은 3.9라 스크립트의 `X | None` 문법을 못 돌린다. python3.12 필수.
# ⚠️ push는 개인 계정(jameshin1212) 자격증명 필요. gh/git credential이 개인이어야 함.
set -uo pipefail

REPO="/Users/jamie/Jamie_Dev/ai-news-scratch"
PYTHON="/opt/homebrew/bin/python3.12"
LOG="$HOME/Library/Logs/ai-news-collect.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

log "=== collect start ==="

# 로컬 변경/원격 갱신 충돌 방지: 먼저 최신화
git -C "$REPO" fetch origin main >>"$LOG" 2>&1
git -C "$REPO" rebase origin/main >>"$LOG" 2>&1 || {
    log "rebase 실패 — abort 후 중단"; git -C "$REPO" rebase --abort >>"$LOG" 2>&1; exit 1
}

# 수집 (스크립트는 상대경로 data/ 에 기록하므로 레포 루트에서 실행)
( cd "$REPO" && "$PYTHON" scripts/collect_community_news.py ) >>"$LOG" 2>&1
rc=$?
if [ $rc -ne 0 ]; then log "수집 스크립트 실패 (rc=$rc)"; exit $rc; fi

# 변경 없으면 종료
if git -C "$REPO" diff --quiet -- data/daily-community.json; then
    log "데이터 변경 없음 — 커밋 생략"
    log "=== collect end (no change) ==="
    exit 0
fi

git -C "$REPO" add data/daily-community.json >>"$LOG" 2>&1
git -C "$REPO" commit -m "chore: daily community news data $(date -u '+%Y-%m-%d %H:%M UTC') (local)" >>"$LOG" 2>&1
git -C "$REPO" push origin main >>"$LOG" 2>&1 || { log "push 실패"; exit 1; }

log "=== collect end (pushed) ==="
