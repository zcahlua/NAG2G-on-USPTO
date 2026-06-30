#!/usr/bin/env python3
"""Convert USPTO-MIT/USPTO-480K WLN split text files to NAG2G CSV files."""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

HEADER = ["class", "id", "rxn_smiles"]
SPLIT_ALIASES = {
    "train": ("train",),
    "valid": ("valid", "val", "dev"),
    "test": ("test",),
}


@dataclass
class SplitStats:
    split: str
    source: Path
    total: int = 0
    accepted: int = 0
    rejected: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", required=True, help="Directory containing raw USPTO-MIT train/dev/test files")
    parser.add_argument("--out-dir", required=True, help="Directory for NAG2G train/valid/test CSV files")
    parser.add_argument("--class-value", default="0", help="Class value to write for every row (default: 0)")
    parser.add_argument("--limit", type=int, default=None, help="Optional accepted-row limit per split for smoke tests")
    parser.add_argument("--strict", action="store_true", help="Fail on malformed rows instead of writing rejected TSV rows")
    parser.add_argument("--dev-name", choices=("dev", "valid", "val"), default=None, help="Raw validation split name to use")
    return parser.parse_args()


def candidate_names(alias: str) -> list[str]:
    suffixes = ("", ".txt", ".csv", ".tsv")
    return [alias + suffix for suffix in suffixes]


def find_split_file(raw_dir: Path, aliases: Iterable[str]) -> Path:
    for alias in aliases:
        for name in candidate_names(alias):
            path = raw_dir / name
            if path.is_file():
                return path
    lower_to_path = {p.name.lower(): p for p in raw_dir.rglob("*") if p.is_file()}
    for alias in aliases:
        for name in candidate_names(alias):
            if name.lower() in lower_to_path:
                return lower_to_path[name.lower()]
    raise FileNotFoundError(f"Could not find split file for aliases {tuple(aliases)} under {raw_dir}")


def validate_rxn_smiles(value: str) -> str | None:
    if not value:
        return "empty reaction SMILES"
    if ">>" not in value:
        return "missing reactants>>product separator"
    if value.count(">") != 2:
        return "unsupported reaction separator; expected reactants>>product"
    reactants, product = value.split(">>", 1)
    if not reactants or not product:
        return "missing reactants or product"
    return None


def convert_split(raw_file: Path, out_dir: Path, split: str, class_value: str, limit: int | None, strict: bool) -> SplitStats:
    stats = SplitStats(split=split, source=raw_file)
    out_csv = out_dir / f"{split}.csv"
    rejected_tsv = out_dir / f"rejected_{split}.tsv"
    out_dir.mkdir(parents=True, exist_ok=True)

    with raw_file.open("r", encoding="utf-8") as src, out_csv.open("w", newline="", encoding="utf-8") as csv_fh, rejected_tsv.open("w", newline="", encoding="utf-8") as rej_fh:
        writer = csv.writer(csv_fh)
        writer.writerow(HEADER)
        rejected = csv.writer(rej_fh, delimiter="\t")
        rejected.writerow(["line_number", "reason", "line"])
        for line_number, line in enumerate(src, start=1):
            if limit is not None and stats.accepted >= limit:
                break
            stats.total += 1
            stripped = line.strip()
            first_field = stripped.split(maxsplit=1)[0] if stripped else ""
            reason = validate_rxn_smiles(first_field)
            if reason:
                stats.rejected += 1
                if strict:
                    raise ValueError(f"{raw_file}:{line_number}: {reason}: {line.rstrip()}")
                rejected.writerow([line_number, reason, line.rstrip("\n")])
                continue
            stats.accepted += 1
            rxn_id = f"USPTO_MIT_{split}_{stats.accepted:09d}"
            writer.writerow([class_value, rxn_id, first_field])
    return stats


def main() -> None:
    args = parse_args()
    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    valid_aliases = (args.dev_name,) if args.dev_name else SPLIT_ALIASES["valid"]
    split_files = {
        "train": find_split_file(raw_dir, SPLIT_ALIASES["train"]),
        "valid": find_split_file(raw_dir, valid_aliases),
        "test": find_split_file(raw_dir, SPLIT_ALIASES["test"]),
    }
    for split, raw_file in split_files.items():
        stats = convert_split(raw_file, out_dir, split, args.class_value, args.limit, args.strict)
        print(f"{split}: source={stats.source} total_lines={stats.total} accepted_rows={stats.accepted} rejected_rows={stats.rejected}")


if __name__ == "__main__":
    main()
