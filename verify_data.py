#!/usr/bin/env python3
"""
Zonalyss Data Verifier
----------------------
Validates metrics CSVs and GeoJSON shapes for a given geographic level (communes or quartiers/IRIS).
- Checks required columns
- Reports nulls/duplicates
- Verifies CSV↔GeoJSON merge coverage via zone_id
- Summarizes score distributions per dataset
- Optional: write a Markdown report to /reports/

Usage:
  python verify_data.py --level communes --root .
  python verify_data.py --level quartiers --root . --save-report
"""

from __future__ import annotations
import argparse
from pathlib import Path
import json
import sys
import pandas as pd

REQUIRED_METRIC_COLS = [
    "zone_id",        # INSEE code (commune) or IRIS/quartier id
    "zone_name",
    "score"
]

DATASETS = ["apartments", "houses", "desks"]

def read_geojson(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to read GeoJSON at {path}: {e}")

def geo_features_to_index(geo: dict) -> pd.DataFrame:
    # Extract properties into a DataFrame; geometry not needed for schema checks
    feats = geo.get("features", [])
    props = [f.get("properties", {}) for f in feats]
    df = pd.DataFrame(props)
    # Normalize common property names to zone_id / zone_name if present
    rename_map = {}
    if "INSEE_COM" in df.columns and "zone_id" not in df.columns:
        rename_map["INSEE_COM"] = "zone_id"
    if "NOM_COM" in df.columns and "zone_name" not in df.columns:
        rename_map["NOM_COM"] = "zone_name"
    if rename_map:
        df = df.rename(columns=rename_map)
    return df

def check_required_cols(df: pd.DataFrame, cols: list[str]) -> list[str]:
    return [c for c in cols if c not in df.columns]

def summarize_nulls(df: pd.DataFrame, cols: list[str]) -> dict:
    return {c: int(df[c].isna().sum()) for c in cols if c in df.columns}

def summarize_duplicates(df: pd.DataFrame, key: str) -> int:
    if key not in df.columns:
        return -1
    return int(df.duplicated(subset=[key]).sum())

def summarize_score(df: pd.DataFrame, score_col: str = "score") -> dict:
    if score_col not in df.columns or df[score_col].dropna().empty:
        return {}
    s = df[score_col].dropna()
    q = s.quantile([0, 0.25, 0.5, 0.75, 1.0]).to_dict()
    return {
        "count": int(s.shape[0]),
        "min": float(s.min()),
        "p25": float(q[0.25]),
        "median": float(q[0.5]),
        "p75": float(q[0.75]),
        "max": float(s.max()),
        "mean": float(s.mean())
    }

def merge_coverage(geo_idx: pd.DataFrame, metrics: pd.DataFrame) -> dict:
    if "zone_id" not in geo_idx.columns or "zone_id" not in metrics.columns:
        return {"error": "zone_id not in both tables"}
    g_ids = set(geo_idx["zone_id"].astype(str))
    m_ids = set(metrics["zone_id"].astype(str))
    matched = len(g_ids & m_ids)
    return {
        "geo_unique": len(g_ids),
        "metrics_unique": len(m_ids),
        "matched": matched,
        "geo_coverage_%": round(100 * matched / max(1, len(g_ids)), 2),
        "metrics_coverage_%": round(100 * matched / max(1, len(m_ids)), 2),
        "missing_in_metrics": len(g_ids - m_ids),
        "missing_in_geo": len(m_ids - g_ids),
    }

def verify_dataset(root: Path, level: str, ds: str) -> dict:
    out = {"dataset": ds, "errors": [], "warnings": [], "info": {}}

    geo_path = root / f"data/{level}/geo/{level}.geojson"
    metrics_path = root / f"data/{level}/metrics_{ds}.csv"

    if not geo_path.exists():
        out["errors"].append(f"GeoJSON not found: {geo_path}")
        return out
    if not metrics_path.exists():
        out["errors"].append(f"Metrics CSV not found: {metrics_path}")
        return out

    geo = read_geojson(geo_path)
    geo_idx = geo_features_to_index(geo)

    # Schema checks
    missing_geo = check_required_cols(geo_idx, ["zone_id", "zone_name"])
    if missing_geo:
        out["errors"].append(f"GeoJSON properties missing columns: {missing_geo}")

    try:
        df = pd.read_csv(metrics_path)
    except Exception as e:
        out["errors"].append(f"Failed loading metrics CSV: {e}")
        return out

    missing_metrics = check_required_cols(df, REQUIRED_METRIC_COLS)
    if missing_metrics:
        out["errors"].append(f"Metrics missing required columns: {missing_metrics}")

    # Nulls, duplicates
    out["info"]["nulls"] = summarize_nulls(df, list(set(REQUIRED_METRIC_COLS + ["income","employment_rate","pop_growth","avg_price_m2","rent_index","vacancy_rate"])))
    dups = summarize_duplicates(df, "zone_id")
    if dups > 0:
        out["warnings"].append(f"Found {dups} duplicate zone_id rows in metrics.")

    # Score distribution
    out["info"]["score_stats"] = summarize_score(df, "score")

    # Merge coverage
    out["info"]["merge"] = merge_coverage(geo_idx, df)

    # Soft bounds check for score
    if "score" in df.columns:
        if (df["score"].dropna() < 0).any() or (df["score"].dropna() > 100).any():
            out["warnings"].append("Scores outside [0,100] detected.")

    return out

def build_report(results: list[dict], level: str) -> str:
    lines = [f"# Zonalyss Data Verification — {level.title()}",
             ""]
    for r in results:
        lines.append(f"## Dataset: {r['dataset']}")
        if r["errors"]:
            lines.append("**Errors:**")
            for e in r["errors"]:
                lines.append(f"- {e}")
        if r["warnings"]:
            lines.append("**Warnings:**")
            for w in r["warnings"]:
                lines.append(f"- {w}")
        lines.append("**Summary:**")
        merge = r.get("info", {}).get("merge", {})
        score = r.get("info", {}).get("score_stats", {})
        nulls = r.get("info", {}).get("nulls", {})
        lines.append(f"- Merge coverage: {json.dumps(merge, ensure_ascii=False)}")
        lines.append(f"- Score stats: {json.dumps(score, ensure_ascii=False)}")
        if nulls:
            nz = {k:v for k,v in nulls.items() if v>0}
            lines.append(f"- Nulls (non-zero): {json.dumps(nz, ensure_ascii=False)}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Zonalyss data verification")
    parser.add_argument("--root", type=str, default=".", help="Repo root path")
    parser.add_argument("--level", type=str, default="communes", choices=["communes","quartiers"], help="Geographic level to validate")
    parser.add_argument("--save-report", action="store_true", help="Save markdown report to /reports")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    level = args.level

    results = []
    for ds in DATASETS:
        res = verify_dataset(root, level, ds)
        results.append(res)

    # Print console report
    print("="*72)
    print(f"Zonalyss Verification — Level: {level}")
    print("="*72)
    had_errors = False
    for r in results:
        print(f"\n--- Dataset: {r['dataset']} ---")
        if r["errors"]:
            had_errors = True
            print("Errors:")
            for e in r["errors"]:
                print("  -", e)
        if r["warnings"]:
            print("Warnings:")
            for w in r["warnings"]:
                print("  -", w)
        merge = r.get("info", {}).get("merge", {})
        score = r.get("info", {}).get("score_stats", {})
        nulls = r.get("info", {}).get("nulls", {})
        print("Summary:")
        print("  - Merge coverage:", json.dumps(merge, ensure_ascii=False))
        print("  - Score stats:", json.dumps(score, ensure_ascii=False))
        nz = {k:v for k,v in nulls.items() if v>0}
        print("  - Nulls (non-zero):", json.dumps(nz, ensure_ascii=False))

    # Save report if requested
    if args.save_report:
        reports_dir = root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        md = build_report(results, level)
        out_path = reports_dir / f"verification_{level}.md"
        out_path.write_text(md, encoding="utf-8")
        print(f"\nSaved report to: {out_path}")

    # Exit code indicates overall status
    if had_errors:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
