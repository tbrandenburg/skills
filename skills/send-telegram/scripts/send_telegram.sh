#!/usr/bin/env bash
set -euo pipefail

: "${TELEGRAM_BOT_TOKEN:?Env var TELEGRAM_BOT_TOKEN is required}"
: "${TELEGRAM_CHAT_ID:?Env var TELEGRAM_CHAT_ID is required}"

API="https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage"

# Telegram max is 4096; keep margin
MAX_LEN="${MAX_LEN:-3900}"

DISABLE_WEB_PAGE_PREVIEW="${DISABLE_WEB_PAGE_PREVIEW:-true}"
DISABLE_NOTIFICATION="${DISABLE_NOTIFICATION:-false}"

read_input() {
  if [[ $# -gt 0 ]]; then
    printf '%s' "$*"
  else
    cat
  fi
}

send_chunk() {
  local chunk="$1"
  local resp

  resp="$(
    curl -sS --fail \
      --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
      --data-urlencode "text=${chunk}" \
      --data-urlencode "parse_mode=HTML" \
      --data-urlencode "disable_web_page_preview=${DISABLE_WEB_PAGE_PREVIEW}" \
      --data-urlencode "disable_notification=${DISABLE_NOTIFICATION}" \
      "$API"
  )" || {
    echo "ERROR: curl request failed" >&2
    exit 2
  }

  if ! printf '%s' "$resp" | grep -q '"ok"[[:space:]]*:[[:space:]]*true'; then
    echo "ERROR: Telegram API returned failure:" >&2
    printf '%s\n' "$resp" >&2
    exit 3
  fi
}

# Split text into raw chunks (no headers yet)
paginate_raw() {
  local text="$1"
  local buf=""
  local line=""
  RAW_CHUNKS=()

  while IFS= read -r line || [[ -n "$line" ]]; do
    local candidate
    if [[ -z "$buf" ]]; then
      candidate="$line"
    else
      candidate="${buf}"$'\n'"${line}"
    fi

    if (( ${#candidate} <= MAX_LEN )); then
      buf="$candidate"
      continue
    fi

    if [[ -n "$buf" ]]; then
      RAW_CHUNKS+=("$buf")
      buf=""
    fi

    if (( ${#line} <= MAX_LEN )); then
      buf="$line"
    else
      local remaining="$line"
      while (( ${#remaining} > MAX_LEN )); do
        RAW_CHUNKS+=("${remaining:0:MAX_LEN}")
        remaining="${remaining:MAX_LEN}"
      done
      buf="$remaining"
    fi
  done <<< "$text"

  if [[ -n "$buf" ]]; then
    RAW_CHUNKS+=("$buf")
  fi
}

send_with_headers() {
  local total="${#RAW_CHUNKS[@]}"
  local i=1

  for chunk in "${RAW_CHUNKS[@]}"; do
    local payload

    if (( total > 1 )); then
      # Add header only when there are multiple chunks
      local header="(${i}/${total})"
      payload="${header}"$'\n'"${chunk}"
    else
      # Single chunk - no header needed
      payload="${chunk}"
    fi

    send_chunk "$payload"
    ((i++))
  done
}

main() {
  local msg
  msg="$(read_input "$@")"

  if [[ -z "$msg" ]]; then
    echo "ERROR: message is empty" >&2
    exit 1
  fi

  paginate_raw "$msg"
  send_with_headers
}

main "$@"