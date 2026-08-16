#!/bin/sh
set -eu

apk add --no-cache curl >/dev/null

for i in $(seq 1 10); do
  ACTUAL=$(curl -sf https://hdmi-switch.morrisons.site/version | grep -o '"commit_sha":"[^"]*"' | cut -d'"' -f4)
  if [ "$ACTUAL" = "$CI_COMMIT_SHA" ]; then
    echo "PASS: deployed commit_sha matches $CI_COMMIT_SHA"
    exit 0
  fi
  echo "attempt $i: got '$ACTUAL', expected '$CI_COMMIT_SHA', retrying..."
  sleep 9
done

echo "FAIL: deployed commit_sha never matched $CI_COMMIT_SHA after 10 attempts"
exit 1
