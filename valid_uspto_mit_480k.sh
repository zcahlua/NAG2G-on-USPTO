#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: bash valid_uspto_mit_480k.sh /path/to/checkpoint.pt" >&2
  exit 1
fi
export data_path=${data_path:-USPTO_MIT_480K_NAG2G}
bash valid.sh "$1" umit
