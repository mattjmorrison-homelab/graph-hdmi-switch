#!/bin/sh
set -eu

apk add --no-cache curl >/dev/null

# Argo CD Image Updater only polls the registry every ~2 minutes, plus sync
# and rollout time on top of that — so this needs a budget comfortably
# longer than one poll cycle, not just a few seconds of slack.
for i in $(seq 1 20); do
  ACTUAL=$(curl -sf https://graph-hdmi-switch.morrisons.site/version | grep -o '"commit_sha":"[^"]*"' | cut -d'"' -f4)
  if [ "$ACTUAL" = "$CI_COMMIT_SHA" ]; then
    echo "PASS: deployed commit_sha matches $CI_COMMIT_SHA"
    exit 0
  fi
  echo "attempt $i: got '$ACTUAL', expected '$CI_COMMIT_SHA', retrying..."
  sleep 15
done

echo "FAIL: deployed commit_sha never matched $CI_COMMIT_SHA after 20 attempts"
exit 1
