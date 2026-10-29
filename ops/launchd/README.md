# 30-day Kraken REST pull (DEC-061)

This is the user's step. The coordinator does not install the job.

The job runs `capture.py daily` once a day at 00:15 UTC. Each run makes three keyless calls (Kraken `OHLC` for XBTUSD and ETHUSD, and `AssetPairs`), after a robots check and with polite pauses (DEC-044). The job stops pulling by itself 30 days after its first run (DEC-057).

## Why the code is copied first

macOS privacy controls block background agents from reading `~/Documents`. This repository is under `~/Documents`, so the job runs a copy of the code from outside it.

## Install

```sh
CODE=~/gladiator-capture        # a copy of the capture code, outside ~/Documents
DATA=~/gladiator-data           # captured data, outside the repository (DEC-030)
REPO=<path to this repository>

mkdir -p "$CODE" "$DATA/rest-daily"
rsync -a --delete "$REPO/src" "$REPO/capture.py" "$CODE/"
sed -e "s#CODE_PATH#$CODE#g" -e "s#DATA_PATH#$DATA#g" \
    "$REPO/ops/launchd/com.gladiator.rest-daily.plist" > ~/Library/LaunchAgents/com.gladiator.rest-daily.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.gladiator.rest-daily.plist

# Check it once, now, instead of waiting for 00:15
launchctl kickstart -k gui/$(id -u)/com.gladiator.rest-daily
tail "$DATA/rest-daily/daily-summary.jsonl" "$DATA/rest-daily/launchd.err.log"
```

**Clock change.** `StartCalendarInterval` uses local time. London is on UTC until the last Sunday of March, so `Hour 0, Minute 15` is 00:15 UTC for the whole 30-day window.

**Python.** The job uses `/usr/bin/python3` (Apple's). It verifies TLS against the system certificates. The python.org build on this Mac lacks CA certificates.

## Remove

```sh
launchctl bootout gui/$(id -u)/com.gladiator.rest-daily
rm ~/Library/LaunchAgents/com.gladiator.rest-daily.plist
```

The collected data stays in `$DATA/rest-daily`.
