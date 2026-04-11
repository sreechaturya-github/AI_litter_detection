from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.litterguard.pipeline import (
    LitterGuardPipeline,
    build_dashboard_js,
    build_operator_report,
    load_events,
    save_incidents,
)


def main() -> None:
    root = Path(__file__).parent
    events_path = root / "sample_data" / "events.json"
    output_dir = root / "output"

    pipeline = LitterGuardPipeline()
    events = load_events(events_path)
    incidents = pipeline.process_events(events)

    save_incidents(output_dir / "incidents.json", incidents)
    (output_dir / "operator_report.md").write_text(build_operator_report(incidents))
    (output_dir / "dashboard_data.js").write_text(build_dashboard_js(incidents))

    print(f"Processed {len(events)} events")
    print(f"Escalated {len(incidents)} incidents")
    print(f"Saved incident outputs to {output_dir}")


if __name__ == "__main__":
    main()
