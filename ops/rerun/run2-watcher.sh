#!/bin/bash
# DEC-070 rerun watcher (TASK-P02-010).
#
# Waits for the first 7-day live capture (DEC-064) to exit, checks that it
# finished cleanly, copies origin/master into a separate code directory, runs
# the offline tests there and only then starts the 7-day rerun. Any failed
# check is logged and the rerun is NOT started.
#
# Usage (user-approved 2026-11-04): copy this file to
# ~/gladiator-data/run2-watcher/ and run it detached under caffeinate:
#   nohup caffeinate -i -s /bin/bash ~/gladiator-data/run2-watcher/run2-watcher.sh <first-run-pid> \
#     >/dev/null 2>&1 &
# Stop it before the first run ends with: kill <watcher pid>  (nothing else is touched).
set -u

FIRST_PID="${1:?first-run python pid required}"
FIRST_OUT="$HOME/gladiator-data/live-7d"
REPO="${GLADIATOR_REPO:-$HOME/dev/Programming/2026/GLADIATOR}"
CODE="$HOME/gladiator-capture-run2"
OUT="$HOME/gladiator-data/live-7d-run2"
LOG="$HOME/gladiator-data/run2-watcher/watcher.log"
FIX_COMMIT=c2b2aa8c01fef7315c0856765179c63ab130e9e0   # head of PR #33 (contains #32)
SECONDS_7D="${RUN_SECONDS:-604800}"   # override only for dry runs

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"; }
abort() { log "ABORT ($1): $2; rerun not started"; exit "$1"; }

mkdir -p "$(dirname "$LOG")"
log "armed by pid $$; waiting for first run pid $FIRST_PID"

ps -p "$FIRST_PID" -o command= | grep -q -- "capture.py live --out $FIRST_OUT " \
  || abort 1 "pid $FIRST_PID is not the first run's capture"

while kill -0 "$FIRST_PID" 2>/dev/null; do sleep 60; done
log "first run pid $FIRST_PID exited"
sleep 10

[ -s "$FIRST_OUT/live-summary.jsonl" ] \
  || abort 2 "$FIRST_OUT/live-summary.jsonl missing or empty, so the first run did not finish cleanly"
log "first run summary present ($(wc -c < "$FIRST_OUT/live-summary.jsonl" | tr -d ' ') bytes)"

[ -e "$CODE" ] && abort 3 "$CODE already exists"
[ -e "$OUT" ] && abort 3 "$OUT already exists"

git -C "$REPO" fetch -q origin master || abort 4 "git fetch of origin/master failed"
REV=$(git -C "$REPO" rev-parse origin/master) || abort 4 "cannot resolve origin/master"
if git -C "$REPO" merge-base --is-ancestor "$FIX_COMMIT" "$REV"; then FIXES=yes; else FIXES=no; fi

mkdir -p "$CODE" || abort 5 "cannot create $CODE"
git -C "$REPO" archive "$REV" | tar -x -C "$CODE" || abort 5 "git archive of $REV failed"
echo "$REV" > "$CODE/REVISION"
log "code copied from origin/master $REV to $CODE; PR #33 fixes included: $FIXES"

( cd "$CODE" && /usr/bin/python3 -I -B -m unittest discover -s tests ) >> "$LOG" 2>&1 \
  || abort 6 "offline tests failed on $REV"
log "offline tests passed on $REV"

mkdir -p "$OUT" || abort 7 "cannot create $OUT"
cd "$CODE" || abort 7 "cannot enter $CODE"
log "starting rerun: caffeinate -i -s /usr/bin/python3 -I -B $CODE/capture.py live --out $OUT --seconds $SECONDS_7D (pid $$ after exec)"
exec caffeinate -i -s /usr/bin/python3 -I -B "$CODE/capture.py" live --out "$OUT" --seconds "$SECONDS_7D" > "$OUT/run.log" 2>&1
