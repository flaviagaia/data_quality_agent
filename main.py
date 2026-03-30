from __future__ import annotations

import json
from pathlib import Path

from src.agent import ask_data_quality_agent
from src.sample_data import ensure_sample_data


def main() -> None:
    ensure_sample_data()
    result = ask_data_quality_agent(
        record_id="DQ-1002",
        user_question="Esse registro está consistente para uso analítico ou precisa de tratamento antes?",
    )
    output_path = Path(__file__).resolve().parent / "data" / "processed" / "data_quality_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Data Quality Agent")
    print(f"runtime_mode: {result['runtime_mode']}")
    print(f"record_id: {result['record_id']}")
    print(f"issue_count: {result['validation']['issue_count']}")
    print(f"issues: {', '.join(result['validation']['issues'])}")
    print(f"output_path: {output_path}")


if __name__ == "__main__":
    main()
