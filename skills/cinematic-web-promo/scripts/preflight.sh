#!/usr/bin/env bash
set -u

browser_mode="auto"
beats_mode="auto"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --browser) browser_mode="${2:-}"; shift 2 ;;
    --beats) beats_mode="${2:-}"; shift 2 ;;
    *) echo "Usage: preflight.sh [--browser auto|native|playwright] [--beats auto|required|skip]" >&2; exit 2 ;;
  esac
done
[[ "$browser_mode" =~ ^(auto|native|playwright)$ ]] || { echo "Invalid --browser mode: $browser_mode" >&2; exit 2; }
[[ "$beats_mode" =~ ^(auto|required|skip)$ ]] || { echo "Invalid --beats mode: $beats_mode" >&2; exit 2; }

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "$script_dir/.." && pwd)"
failed=0

check_command() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "PASS  $1: $(command -v "$1")"
  else
    echo "MISS  $1"
    failed=1
  fi
}

check_command node
check_command python3
check_command pnpm
if [[ -n "${FFMPEG_BIN:-}" && -x "${FFMPEG_BIN}" ]]; then
  echo "PASS  ffmpeg: $FFMPEG_BIN"
else
  check_command ffmpeg
fi
if [[ -n "${FFPROBE_BIN:-}" && -x "${FFPROBE_BIN}" ]]; then
  echo "PASS  ffprobe: $FFPROBE_BIN"
else
  check_command ffprobe
fi

if command -v node >/dev/null 2>&1; then
  node_major="$(node -p 'Number(process.versions.node.split(".")[0])')"
  if [[ "$node_major" -lt 20 ]]; then
    echo "MISS  Node 20+ required (found $(node -v))"
    failed=1
  fi
fi

case "$browser_mode" in
  native)
    echo "PASS  Browser mode: host-native browser/computer tool"
    ;;
  auto)
    if [[ "${CWP_NATIVE_BROWSER:-0}" == "1" ]]; then
      echo "PASS  Browser mode: host-native capability declared by CWP_NATIVE_BROWSER=1"
    elif (cd "$script_dir" && node -e "import('playwright')" >/dev/null 2>&1); then
      echo "PASS  Browser mode: Playwright module"
    else
      echo "WARN  No Playwright module detected; use a host-native browser or install it."
      echo "      Setup: cd \"$script_dir\" && npm ci && npx playwright install chromium"
    fi
    ;;
  playwright)
    if (cd "$script_dir" && node -e "import('playwright')" >/dev/null 2>&1); then
      echo "PASS  Browser mode: Playwright module"
    else
      echo "MISS  Playwright module required by --browser playwright"
      echo "      Setup: cd \"$script_dir\" && npm ci && npx playwright install chromium"
      failed=1
    fi
    ;;
esac

if command -v python3 >/dev/null 2>&1; then
  if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    echo "MISS  Python 3.10+ required (found $(python3 --version 2>&1))"
    failed=1
  fi
  if [[ "$beats_mode" == "skip" ]]; then
    echo "PASS  Beat analysis skipped by request"
  elif python3 -c 'import librosa, numpy, scipy' >/dev/null 2>&1; then
    echo "PASS  Python beat-analysis packages"
  elif [[ "$beats_mode" == "required" ]]; then
    echo "MISS  Python beat-analysis packages required by --beats required"
    echo "      Setup: python3 -m venv .venv && .venv/bin/pip install -r \"$script_dir/requirements.txt\""
    failed=1
  else
    echo "WARN  Beat-analysis packages are absent; install them before beat-synced music work."
    echo "      Setup: python3 -m venv .venv && .venv/bin/pip install -r \"$script_dir/requirements.txt\""
  fi
  if python3 "$script_dir/shotcraft_router.py" --help >/dev/null 2>&1; then
    echo "PASS  Shotcraft recipe router"
  else
    echo "MISS  Shotcraft recipe router cannot start"
    failed=1
  fi
  if python3 "$script_dir/shotcraft_router.py" --source embedded --recipe tape-scroll-fixed-pointer --json >/dev/null 2>&1; then
    echo "PASS  Embedded Shotcraft snapshot"
  else
    echo "MISS  Embedded Shotcraft snapshot integrity/routing check"
    failed=1
  fi
fi

for required in \
  "$skill_dir/SKILL.md" \
  "$skill_dir/agents/openai.yaml" \
  "$skill_dir/scripts/package-lock.json" \
  "$skill_dir/scripts/install_skill.ps1" \
  "$skill_dir/scripts/shotcraft_router.py" \
  "$skill_dir/scripts/sync_shotcraft_snapshot.py" \
  "$skill_dir/references/platform-codex.md" \
  "$skill_dir/references/platform-claude-code.md" \
  "$skill_dir/references/platform-workbuddy.md" \
  "$skill_dir/references/shotcraft-router.md" \
  "$skill_dir/assets/remotion-starter/package.json" \
  "$skill_dir/assets/remotion-starter/pnpm-lock.yaml" \
  "$skill_dir/assets/media-license-manifest.json" \
  "$skill_dir/assets/shotcraft-snapshot/SNAPSHOT.json" \
  "$skill_dir/assets/shotcraft-snapshot/repo/LICENSE" \
  "$skill_dir/assets/shotcraft-snapshot/repo/gallery/api/library.json"; do
  if [[ -f "$required" ]]; then
    echo "PASS  ${required#"$skill_dir/"}"
  else
    echo "MISS  ${required#"$skill_dir/"}"
    failed=1
  fi
done

echo "INFO  Starter setup: cd \"$skill_dir/assets/remotion-starter\" && pnpm install --frozen-lockfile"

if [[ "$failed" -ne 0 ]]; then
  echo "Preflight incomplete. Resolve missing required items."
  exit 1
fi

echo "Preflight passed: $skill_dir"
