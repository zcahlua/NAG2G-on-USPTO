import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONVERTER = ROOT / "data_preprocess" / "convert_uspto_mit_480k.py"
FIXTURE = ROOT / "tests" / "fixtures" / "uspto_mit_480k"


def run_converter(out_dir, *extra):
    subprocess.run(
        [sys.executable, str(CONVERTER), "--raw-dir", str(FIXTURE), "--out-dir", str(out_dir), *extra],
        check=True,
        cwd=ROOT,
    )


def rows(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))


def test_converter_outputs_headers_rejections_and_deterministic_ids(tmp_path):
    run_converter(tmp_path)
    for split in ("train", "valid", "test"):
        csv_rows = rows(tmp_path / f"{split}.csv")
        assert csv_rows[0] == ["class", "id", "rxn_smiles"]
        assert csv_rows[1][1] == f"USPTO_MIT_{split}_000000001"
        assert csv_rows[2][1] == f"USPTO_MIT_{split}_000000002"
        assert csv_rows[1][0] == "0"
        rejected = (tmp_path / f"rejected_{split}.tsv").read_text(encoding="utf-8")
        assert "missing reactants>>product separator" in rejected


def test_limit_applies_to_accepted_rows(tmp_path):
    run_converter(tmp_path, "--limit", "1")
    train_rows = rows(tmp_path / "train.csv")
    assert len(train_rows) == 2
    assert train_rows[1][1] == "USPTO_MIT_train_000000001"
