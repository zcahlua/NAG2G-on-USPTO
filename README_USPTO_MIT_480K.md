# Running NAG2G on USPTO-MIT / USPTO-480K

This guide describes the added workflow for training and validating the existing NAG2G implementation on the USPTO-MIT / USPTO-480K single-step retrosynthesis split from the original WLN release. The NAG2G architecture is unchanged; this workflow only adds download, conversion, preprocessing, training, and validation wrappers.

- Dataset page: https://github.com/wengong-jin/nips17-rexgen/blob/master/USPTO/data.zip
- Direct download link: https://github.com/wengong-jin/nips17-rexgen/raw/master/USPTO/data.zip

## Setup

```bash
git clone https://github.com/zcahlua/NAG2G-on-USPTO
cd NAG2G-on-USPTO

git clone https://github.com/dptech-corp/Uni-Core
cd Uni-Core
pip install .
cd -

cd unimol_plus
pip install .
cd -

pip install rdchiral transformers tokenizers omegaconf rdkit lmdb pandas tqdm
```

## Download and preprocess data

```bash
bash scripts/download_uspto_mit_480k.sh
bash scripts/preprocess_uspto_mit_480k.sh
```

For a quick converter/preprocessing smoke test, limit the number of accepted rows per split:

```bash
LIMIT=100 bash scripts/preprocess_uspto_mit_480k.sh
```

The converter expects the USPTO-MIT source lines to contain an atom-mapped reaction SMILES followed by a whitespace-delimited reaction-center field. Only the first field is written to NAG2G CSV files; atom maps are preserved for the existing NAG2G preprocessing step. Raw `dev` or `val` split names are mapped to NAG2G `valid`.

USPTO-MIT has no reaction class labels, so the generated CSV files use `class=0` for every row and the training wrapper sets `use_class=false`.

The preprocessing wrapper writes the dataset directory expected by the loader:

```text
USPTO_MIT_480K_NAG2G/
  dict_20230310.txt
  train.lmdb
  valid.lmdb
  test.lmdb
```

If `dict_20230310.txt` is not available in the output directory or `USPTO50K_brief_20230227/`, the script fails with a clear error. Copy the dictionary from the USPTO-50K dataset bundle before rerunning.

## Train

```bash
bash train_uspto_mit_480k.sh
```

Defaults can be overridden via environment variables, for example:

```bash
total_steps=200000 batch_size=8 update_freq=2 bash train_uspto_mit_480k.sh
```

The wrapper defaults to `total_steps=120000` as a conservative starting point matching the original script; adjust it for full USPTO-480K training sweeps and available GPU memory.

## Validate

```bash
bash valid_uspto_mit_480k.sh outputs/<run>/checkpoint_last.pt
```

You can also call the generic script explicitly:

```bash
bash valid.sh outputs/<run>/checkpoint_last.pt umit
```

## Files not to commit

Do not commit downloaded raw data, generated CSVs, LMDBs, checkpoints, logs, or model outputs. The repository `.gitignore` covers `data/`, `USPTO_MIT_480K_NAG2G/`, `*.lmdb`, `*.zip`, `outputs/`, `logs/`, `*.pt`, and generated USPTO-MIT CSV outputs.
