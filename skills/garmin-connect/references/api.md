# Garmin Connect API Reference

All methods are on the `Garmin` instance returned by `get_client()`.
All `date` arguments: `str` in `"YYYY-MM-DD"` format.

## Table of Contents
1. [Daily Stats & Summary](#daily-stats--summary)
2. [Heart Rate](#heart-rate)
3. [Sleep](#sleep)
4. [HRV](#hrv)
5. [Stress](#stress)
6. [Body Battery](#body-battery)
7. [Steps & Activity Breakdown](#steps--activity-breakdown)
8. [Respiration](#respiration)
9. [Hydration](#hydration)
10. [Activities](#activities)
11. [User Profile](#user-profile)

---

## Daily Stats & Summary

### `get_stats(date) → dict`
93-key daily wellness summary. The most comprehensive single-call endpoint.

Key fields:
| Field | Type | Description |
|---|---|---|
| `totalSteps` | int | Total steps for the day |
| `totalDistanceMeters` | int | Total distance (m) |
| `activeKilocalories` | float | Active calories burned |
| `bmrKilocalories` | float | Basal metabolic rate calories |
| `restingHeartRate` | int | Resting HR (bpm) |
| `minHeartRate` / `maxHeartRate` | int | Day HR range |
| `lastSevenDaysAvgRestingHeartRate` | int | 7-day resting HR average |
| `averageStressLevel` | int | 0–100 stress score |
| `maxStressLevel` | int | Peak stress score |
| `highlyActiveSeconds` | int | Seconds in high activity |
| `moderateIntensityMinutes` | int | WHO moderate minutes |
| `vigorousIntensityMinutes` | int | WHO vigorous minutes |
| `floorsAscended` / `floorsDescended` | float | Floors |
| `bodyBatteryMostRecentValue` | int | Current body battery (0–100) |
| `bodyBatteryHighestValue` | int | Peak body battery |
| `bodyBatteryLowestValue` | int | Lowest body battery |
| `bodyBatteryChargedValue` | int | BB charged during sleep |
| `averageSpo2` / `lowestSpo2` | int\|null | Blood oxygen (needs Pulse Ox enabled) |
| `avgWakingRespirationValue` | float | Breaths/min while awake |
| `highestRespirationValue` | float | Max breaths/min |
| `dailyStepGoal` | int | Step goal |
| `sedentarySeconds` | int | Sedentary time |
| `sleepingSeconds` | int | Time asleep |
| `calendarDate` | str | Date of record |

### `get_stats_and_body(date) → dict`
Same as `get_stats` but adds body composition fields (104 keys):
- `weight`, `bmi`, `bodyFat`, `bodyWater`, `boneMass`, `muscleMass`, `visceralFat`, `metabolicAge`
- These are null unless a body composition scale is linked to the account.

---

## Heart Rate

### `get_heart_rates(date) → dict`

| Field | Description |
|---|---|
| `restingHeartRate` | Resting HR (bpm) |
| `minHeartRate` | Day minimum |
| `maxHeartRate` | Day maximum |
| `lastSevenDaysAvgRestingHeartRate` | 7-day average |
| `heartRateValues` | `[[epoch_ms, bpm], ...]` — per-2-minute HR timeline |

---

## Sleep

### `get_sleep_data(date) → dict`
`date` is the **morning** date (day you woke up).

Key fields inside `dailySleepDTO`:
| Field | Description |
|---|---|
| `sleepStartTimestampLocal` | Sleep start (local) |
| `sleepEndTimestampLocal` | Wake time (local) |
| `deepSleepSeconds` | Deep sleep duration |
| `lightSleepSeconds` | Light sleep duration |
| `remSleepSeconds` | REM sleep duration |
| `awakeSleepSeconds` | Awake during sleep window |
| `averageSpO2Value` | Average blood oxygen |
| `averageRespirationValue` | Avg breaths/min during sleep |
| `avgSleepStress` | Average stress during sleep |
| `sleepScores` | Overall sleep score (dict) |

Top-level extras:
- `sleepLevels` — list of `{startGMT, endGMT, activityLevel}` segments
- `sleepHeartRate` — `[{value, startGMT}, ...]` per-minute HR during sleep
- `sleepStress` — per-minute stress during sleep
- `sleepBodyBattery` — per-minute body battery during sleep
- `avgOvernightHrv` — average overnight HRV (ms)
- `hrvStatus` — e.g. `"BALANCED"`, `"LOW"`, `"UNBALANCED"`
- `bodyBatteryChange` — BB gained/lost overnight
- `restingHeartRate` — resting HR computed from sleep

---

## HRV

### `get_hrv_data(date) → dict`
`date` is the **morning** date.

Key fields inside `hrvSummary`:
| Field | Description |
|---|---|
| `weeklyAvg` | 7-day HRV average (ms) |
| `lastNightAvg` | Last night average HRV (ms) |
| `lastNight5MinHigh` | Best 5-min HRV window last night |
| `status` | `"BALANCED"` / `"LOW"` / `"UNBALANCED"` |
| `feedbackPhrase` | Human-readable status message |

Top-level extras:
- `hrvReadings` — `[{hrvValue, readingTimeGMT}, ...]` per-measurement readings
- `startTimestampLocal` / `endTimestampLocal` — measurement window

---

## Stress

### `get_stress_data(date) → dict`

| Field | Description |
|---|---|
| `avgStressLevel` | Average stress (0–100) |
| `maxStressLevel` | Peak stress |
| `stressValuesArray` | `[[epoch_ms, level], ...]` — per-3-min timeline |
| `bodyBatteryValuesArray` | `[[epoch_ms, status, value, version], ...]` |

Stress interpretation: 0–25 = rest/low, 26–50 = medium, 51–75 = high, 76–100 = very high. `-1` = no data/activity.

---

## Body Battery

### `get_body_battery(date) → list[dict]`
Returns a list (typically 1 item per day).

| Field | Description |
|---|---|
| `charged` | BB gained (typically during sleep) |
| `drained` | BB spent during the day |
| `bodyBatteryValuesArray` | `[[epoch_ms, value], ...]` — timeline |
| `bodyBatteryDynamicFeedbackEvent` | Most recent feedback event |

Body battery 0–100: <25 drained, 25–50 low, 50–75 moderate, 75–100 high.

---

## Steps & Activity Breakdown

### `get_steps_data(date) → list[dict]`
Returns ~96 items (15-min buckets).

| Field | Description |
|---|---|
| `startGMT` / `endGMT` | Bucket window |
| `steps` | Steps in this window |
| `primaryActivityLevel` | `"sedentary"` / `"active"` / `"highly_active"` / `"sleeping"` |

---

## Respiration

### `get_respiration_data(date) → dict`
Breaths per minute timeline. Needs respiratory data enabled on watch.

---

## Hydration

### `get_hydration_data(date) → dict`

| Field | Description |
|---|---|
| `valueInML` | Total intake (ml) — null if nothing logged |
| `goalInML` | Daily hydration goal |
| `sweatLossInML` | Estimated sweat loss |

---

## Activities

### `get_activities(start, limit) → list[dict]`
Paginated activity list. `start=0, limit=20` for most recent 20.

Key fields per activity:
| Field | Description |
|---|---|
| `activityId` | Unique activity ID |
| `activityName` | User-set name |
| `startTimeLocal` | Local start datetime string |
| `activityType.typeKey` | e.g. `"cycling"`, `"running"`, `"swimming"` |
| `distance` | Distance (meters) |
| `duration` | Moving time (seconds) |
| `calories` | Calories burned |
| `averageHR` / `maxHR` | Heart rate stats |
| `averageSpeed` | m/s |
| `elevationGain` / `elevationLoss` | Meters |
| `aerobicTrainingEffect` | 0–5 aerobic TE score |
| `anaerobicTrainingEffect` | 0–5 anaerobic TE score |
| `trainingEffectLabel` | e.g. `"AEROBIC_BASE"`, `"TEMPO"` |
| `activityTrainingLoad` | Training load score |
| `hrTimeInZone_1..5` | Seconds in each HR zone |
| `moderateIntensityMinutes` | WHO moderate min contribution |
| `vigorousIntensityMinutes` | WHO vigorous min contribution |
| `differenceBodyBattery` | BB impact of this activity |

### `get_activity_splits(activity_id) → dict`
Lap/interval splits for a specific activity.

### `get_activity_hr_in_timezones(activity_id) → list`
HR zone distribution for a specific activity.

---

## User Profile

### `get_user_profile() → dict`
Inside `userData`:
| Field | Description |
|---|---|
| `gender` | `"MALE"` / `"FEMALE"` |
| `weight` | Weight in grams (divide by 1000 for kg) |
| `height` | Height in cm |
| `vo2MaxRunning` | VO2max from running |
| `vo2MaxCycling` | VO2max from cycling (null if not measured) |
| `lactateThresholdHeartRate` | LT heart rate (bpm) |
| `lactateThresholdSpeed` | LT speed (m/s) |
| `availableTrainingDays` | List of training day names |
| `preferredLongTrainingDays` | Long session day preference |

Inside `userSleep`:
- `sleepTime` — seconds from midnight (e.g. 79200 = 22:00)
- `wakeTime` — seconds from midnight (e.g. 21600 = 06:00)
