#!/usr/bin/env bash
set -euo pipefail
DATA_ROOT=${DATA_ROOT:-data/uspto_mit_480k/raw}
USPTO_MIT_URL=${USPTO_MIT_URL:-https://github.com/wengong-jin/nips17-rexgen/raw/master/USPTO/data.zip}
ZIP_PATH="${DATA_ROOT}/data.zip"
mkdir -p "${DATA_ROOT}"
if [ ! -s "${ZIP_PATH}" ]; then
  if command -v curl >/dev/null 2>&1; then
    curl -L --retry 3 -o "${ZIP_PATH}" "${USPTO_MIT_URL}"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "${ZIP_PATH}" "${USPTO_MIT_URL}"
  else
    echo "ERROR: curl or wget is required." >&2; exit 1
  fi
else
  echo "Using existing ${ZIP_PATH}"
fi
unzip -o -q "${ZIP_PATH}" -d "${DATA_ROOT}"
for split in train test; do
  find "${DATA_ROOT}" -type f \( -iname "${split}" -o -iname "${split}.txt" -o -iname "${split}.csv" -o -iname "${split}.tsv" \) | head -n 1 | grep -q . || { echo "ERROR: missing ${split} split under ${DATA_ROOT}" >&2; exit 1; }
done
find "${DATA_ROOT}" -type f \( -iname "dev" -o -iname "dev.txt" -o -iname "valid" -o -iname "valid.txt" -o -iname "val" -o -iname "val.txt" \) | head -n 1 | grep -q . || { echo "ERROR: missing dev/valid/val split under ${DATA_ROOT}" >&2; exit 1; }
find "${DATA_ROOT}" -maxdepth 3 -print | sort
