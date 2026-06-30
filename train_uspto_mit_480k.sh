#!/usr/bin/env bash
set -euo pipefail
export data_path=${data_path:-USPTO_MIT_480K_NAG2G}
export task_name=${task_name:-NAG2G_unimolplus_uspto_mit_480k}
export use_class=${use_class:-false}
export dict_name=${dict_name:-dict_20230310.txt}
export batch_size=${batch_size:-16}
export update_freq=${update_freq:-1}
# 120k matches the USPTO-50K default and is a conservative starting point for 480K; override for sweeps.
export total_steps=${total_steps:-120000}
export warmup_steps=${warmup_steps:-12000}
bash train.sh
