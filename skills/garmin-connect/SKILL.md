---
name: garmin-connect
description: >
  Retrieve, analyse, and reason about personal health, training, well-being, and fitness data
  from Garmin Connect using the python-garminconnect library and the shared garmin_client package
  at ~/.garmin.

  Use this skill when the user asks to:
  - fetch or display health data (steps, heart rate, sleep, HRV, stress, body battery, SpO2, respiration, hydration)
  - analyse training or activity data (cycling, running, workouts, training load, training effect, HR zones)
  - query fitness metrics (VO2max, lactate threshold, intensity minutes, floors, calories)
  - write code that fetches data from Garmin Connect
  - debug Garmin Connect authentication (429 errors, rate limiting, token issues, browser cookies)
  - set up or install the garmin_client package
---

# Garmin Connect Skill

Provides access to personal health, training, and fitness data via `python-garminconnect` and the
shared `garmin_client` package installed at `~/.garmin`.

## Setup

```bash
pip install -e ~/.garmin
```

```python
from garmin_client import get_client
from datetime import date

client = get_client()   # loads ~/.garmin/tokens.json; auths on first run via env vars
```

Required env vars (first run only):
- `GARMIN_CONNECT_USER` — Garmin account email
- `GARMIN_CONNECT_PASSWORD` — Garmin account password

`GARMIN_TOKEN_PATH` overrides the default `~/.garmin/tokens.json`.

## Fetching Data

All methods take a date string `"YYYY-MM-DD"`. Use `date.today().isoformat()` for today.

```python
today = date.today().isoformat()

# Core wellness
stats  = client.get_stats(today)                 # 93-key daily summary (steps, HR, stress, BB, SpO2…)
hr     = client.get_heart_rates(today)           # resting HR, min/max, 7-day avg, per-2-min timeline
sleep  = client.get_sleep_data(today)            # deep/light/REM/awake, SpO2, respiration, HRV, score
hrv    = client.get_hrv_data(today)              # weekly avg, last-night avg, status, feedback phrase
stress = client.get_stress_data(today)           # avg/max stress, per-3-min timeline
bb     = client.get_body_battery(today)          # charged/drained, per-reading timeline (0–100)
steps  = client.get_steps_data(today)            # 15-min step buckets with activity level
hydra  = client.get_hydration_data(today)        # intake vs goal (ml)

# Training
acts   = client.get_activities(0, 20)            # recent activities (paginated)
splits = client.get_activity_splits(activity_id) # lap/interval splits
zones  = client.get_activity_hr_in_timezones(activity_id)  # HR zone breakdown

# Profile
prof   = client.get_user_profile()              # gender, weight, height, VO2max, LT HR/speed
```

For full field descriptions and all available fields: see `references/api.md`.

## Analysing Data

When the user asks to analyse or summarise data, fetch the relevant endpoint(s) and reason directly
over the returned dicts/lists. Key patterns:

**Daily snapshot:**
```python
s = client.get_stats(today)
print(s["totalSteps"], s["restingHeartRate"], s["bodyBatteryMostRecentValue"], s["averageStressLevel"])
```

**Sleep quality:**
```python
sl = client.get_sleep_data(today)
dto = sl.get("dailySleepDTO", {})
deep  = (dto.get("deepSleepSeconds") or 0) / 3600
light = (dto.get("lightSleepSeconds") or 0) / 3600
rem   = (dto.get("remSleepSeconds") or 0) / 3600
total = deep + light + rem
```

**HRV status:**
```python
hrv = client.get_hrv_data(today)
summary = hrv.get("hrvSummary", {})
print(summary.get("status"), summary.get("weeklyAvg"), summary.get("lastNightAvg"))
```

**Recent training load:**
```python
acts = client.get_activities(0, 10)
for a in acts:
    print(a["startTimeLocal"], a["activityType"]["typeKey"],
          a["distance"]/1000, a.get("activityTrainingLoad"))
```

**Body battery trend (intraday):**
```python
bb = client.get_body_battery(today)[0]
readings = bb["bodyBatteryValuesArray"]   # [[epoch_ms, value], ...]
# readings[-1][1] = current value
```

## Auth Issues

If authentication fails (429, token errors, library login failures): see `references/auth-troubleshooting.md`.

Quick reference:
- **429 on login** — Rate limit or library bug (`impersonate="safari"`). Use `get_client()`, never `client.login()`.
- **Tokens expire** — Access token: ~28h, auto-refreshed. Refresh token: effectively permanent.
- **403 after auth** — `display_name` not set, or token stale. `get_client()` handles both.
- **Browser cookies → 403** — IP-bound session cookie. Cannot be reused from a different host.
