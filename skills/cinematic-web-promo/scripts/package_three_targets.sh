#!/usr/bin/env bash
set -euo pipefail

force_flag=()
if [[ "${1:-}" == "--force" ]]; then
  force_flag=(--force)
  shift
fi

output_dir="${1:-}"
if [[ -z "$output_dir" ]]; then
  echo "Usage: package_three_targets.sh [--force] /absolute/output-directory" >&2
  exit 2
fi
[[ "$output_dir" = /* ]] || { echo "Output directory must be absolute." >&2; exit 2; }

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$output_dir"

package_one() {
  local output="$1"
  if [[ ${#force_flag[@]} -gt 0 ]]; then
    "$script_dir/install_skill.sh" --force package "$output"
  else
    "$script_dir/install_skill.sh" package "$output"
  fi
}

package_one "$output_dir/cinematic-web-promo-codex.zip"
package_one "$output_dir/cinematic-web-promo-claude-code.zip"
package_one "$output_dir/cinematic-web-promo-workbuddy.zip"

(
  cd "$output_dir"
  shasum -a 256 \
    cinematic-web-promo-codex.zip \
    cinematic-web-promo-claude-code.zip \
    cinematic-web-promo-workbuddy.zip \
    > cinematic-web-promo-SHA256SUMS.txt
)

echo "Created three-host packages in: $output_dir"
