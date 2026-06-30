#!/usr/bin/env bash
set -euo pipefail
RAW_DIR=${RAW_DIR:-data/uspto_mit_480k/raw}
CSV_DIR=${CSV_DIR:-data/uspto_mit_480k/csv}
OUT_DIR=${OUT_DIR:-USPTO_MIT_480K_NAG2G}
LIMIT=${LIMIT:-}
FORCE=${FORCE:-0}
DICT_NAME=${DICT_NAME:-dict_20230310.txt}
mkdir -p "${CSV_DIR}" "${OUT_DIR}"
convert_args=(--raw-dir "${RAW_DIR}" --out-dir "${CSV_DIR}")
if [ -n "${LIMIT}" ]; then convert_args+=(--limit "${LIMIT}"); fi
python data_preprocess/convert_uspto_mit_480k.py "${convert_args[@]}"
if [ ! -f "${OUT_DIR}/${DICT_NAME}" ]; then
  if [ -f "USPTO50K_brief_20230227/${DICT_NAME}" ]; then
    cp "USPTO50K_brief_20230227/${DICT_NAME}" "${OUT_DIR}/${DICT_NAME}"
  else
    echo "ERROR: ${OUT_DIR}/${DICT_NAME} is missing. Copy ${DICT_NAME} from the USPTO-50K dataset directory into ${OUT_DIR}/ before training." >&2
    exit 1
  fi
fi
for split in train valid test; do
  lmdb_path="${OUT_DIR}/${split}.lmdb"
  if [ -f "${lmdb_path}" ] && [ "${FORCE}" != "1" ]; then
    echo "Skipping existing ${lmdb_path}; set FORCE=1 to rebuild."
  else
    rm -f "${lmdb_path}"
    (cd data_preprocess && python lmdb_preprocess.py "../${CSV_DIR}/${split}.csv" "../${lmdb_path}")
  fi
done
echo "Dataset ready: ${OUT_DIR}"
find "${OUT_DIR}" -maxdepth 1 -type f -printf '%p %s bytes\n' | sort
