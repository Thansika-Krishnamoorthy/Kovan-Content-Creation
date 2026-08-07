#!/usr/bin/env bash
set -euo pipefail

UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$UNIT_DIR"

cp "$PROJECT_DIR/systemd/"*.service "$UNIT_DIR/"
cp "$PROJECT_DIR/systemd/"*.timer "$UNIT_DIR/"

systemctl --user daemon-reload

systemctl --user restart kovan-poster-schedule.timer
systemctl --user list-timers kovan-poster-schedule.timer --no-pager
echo "Systemd services installed successfully."

# cp "/home/thansika/Documents/Content creation/systemd/kovan-poster-schedule.timer" ~/.config/systemd/user/kovan-poster-schedule.timer && systemctl --user daemon-reload && systemctl --user restart kovan-poster-schedule.timer