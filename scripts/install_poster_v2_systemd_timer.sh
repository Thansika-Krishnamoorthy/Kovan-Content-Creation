#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
unit_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

mkdir -p "$unit_dir"
cp "$project_dir/systemd/kovan-v2-poster-api.service" "$unit_dir/"
cp "$project_dir/systemd/kovan-v2-poster-schedule.service" "$unit_dir/"
cp "$project_dir/systemd/kovan-v2-poster-schedule.timer" "$unit_dir/"

systemctl --user daemon-reload
systemctl --user enable kovan-v2-poster-api.service
systemctl --user restart kovan-v2-poster-api.service
systemctl --user enable --now kovan-v2-poster-schedule.timer
systemctl --user reset-failed kovan-v2-poster-schedule.service 2>/dev/null || true

systemctl --user status kovan-v2-poster-api.service --no-pager
systemctl --user list-timers kovan-v2-poster-schedule.timer --no-pager
printf 'Kovan V2 animated poster services installed.\n'
