#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  install_skill.sh [--force] codex-user
  install_skill.sh [--force] codex-project [project-root]
  install_skill.sh [--force] claude-user
  install_skill.sh [--force] claude-project [project-root]
  install_skill.sh [--force] workbuddy-package [output.zip]
  install_skill.sh [--force] codebuddy-project [workspace-root]
  install_skill.sh [--force] custom /absolute/skills-root

Aliases: codex=codex-user, claude=claude-user, workbuddy=workbuddy-package.
EOF
  exit 2
}

force=0
if [[ "${1:-}" == "--force" ]]; then
  force=1
  shift
fi

target="${1:-}"
arg="${2:-}"
[[ -n "$target" ]] || usage

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_dir="$(cd "$script_dir/.." && pwd)"
skill_name="cinematic-web-promo"
package_temp_dir=""

cleanup() {
  if [[ -n "$package_temp_dir" && -d "$package_temp_dir" ]]; then
    rm -rf -- "$package_temp_dir"
  fi
}
trap cleanup EXIT

backup_existing() {
  local existing="$1"
  if [[ ! -e "$existing" ]]; then
    return
  fi
  if [[ "$force" -ne 1 ]]; then
    echo "Destination exists: $existing (pass --force to back it up and replace it)" >&2
    exit 1
  fi
  local backup="${existing}.backup.$(date +%Y%m%d%H%M%S)"
  mv "$existing" "$backup"
  echo "Backed up existing destination to: $backup"
}

install_to_root() {
  local root="$1"
  [[ "$root" = /* ]] || { echo "Skill root must resolve to an absolute path: $root" >&2; exit 2; }
  local destination="$root/$skill_name"
  mkdir -p "$root"
  if [[ "$(cd "$(dirname "$destination")" 2>/dev/null && pwd -P)/$(basename "$destination")" == "$source_dir" ]]; then
    echo "Source and destination are the same skill directory; nothing to install." >&2
    exit 1
  fi
  backup_existing "$destination"
  cp -R "$source_dir" "$destination"
  rm -rf -- "$destination/.git"
  echo "Installed: $destination"
}

package_skill() {
  local output="${1:-$PWD/${skill_name}-workbuddy.zip}"
  [[ "$output" = /* ]] || output="$PWD/$output"
  mkdir -p "$(dirname "$output")"
  backup_existing "$output"
  package_temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/cwp-package.XXXXXX")"
  cp -R "$source_dir" "$package_temp_dir/$skill_name"
  find "$package_temp_dir/$skill_name" -name '.DS_Store' -delete
  (
    cd "$package_temp_dir"
    COPYFILE_DISABLE=1 zip -qr "$output" "$skill_name" \
      -x '*/.git/*' '*/node_modules/*' '*/.venv/*' '*/__pycache__/*' '*.pyc'
  )
  echo "Packaged: $output"
}

case "$target" in
  codex|codex-user)
    install_to_root "${CODEX_SKILLS_HOME:-$HOME/.agents/skills}"
    ;;
  codex-project)
    project_root="${arg:-$PWD}"
    project_root="$(cd "$project_root" && pwd -P)"
    install_to_root "$project_root/.agents/skills"
    ;;
  claude|claude-user)
    install_to_root "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
    ;;
  claude-project)
    project_root="${arg:-$PWD}"
    project_root="$(cd "$project_root" && pwd -P)"
    install_to_root "$project_root/.claude/skills"
    ;;
  workbuddy|workbuddy-package|package)
    package_skill "$arg"
    ;;
  codebuddy-project)
    project_root="${arg:-$PWD}"
    project_root="$(cd "$project_root" && pwd -P)"
    install_to_root "$project_root/.codebuddy/skills"
    ;;
  custom)
    [[ -n "$arg" && "$arg" = /* ]] || usage
    install_to_root "$arg"
    ;;
  /*)
    install_to_root "$target"
    ;;
  *)
    usage
    ;;
esac
