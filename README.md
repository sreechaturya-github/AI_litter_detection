# LitterGuard

LitterGuard is a lightweight prototype for AI-based litter and unattended-item detection in monitored public and private spaces. It follows the case study's core idea:

- use existing CCTV-style event streams
- apply cheap filtering first
- escalate only likely incidents for multimodal review
- produce actionable incident alerts and operator summaries

This repository is structured as a hackathon-ready MVP with no third-party dependencies.

## What it does

The prototype simulates:

1. `Lightweight filtering`
   - motion checks
   - region-of-interest validation
   - new-object appearance detection
   - stationary timers
   - person-object separation
2. `Selective AI review`
   - a Gemma-style review prompt payload
   - a local heuristic reviewer used offline for the demo
3. `Action layer`
   - incident JSON export
   - operator summary report
   - static dashboard HTML

## Project layout

- [`src/litterguard/models.py`](/Users/chaturya/Documents/New%20project/src/litterguard/models.py)
- [`src/litterguard/pipeline.py`](/Users/chaturya/Documents/New%20project/src/litterguard/pipeline.py)
- [`run_demo.py`](/Users/chaturya/Documents/New%20project/run_demo.py)
- [`sample_data/events.json`](/Users/chaturya/Documents/New%20project/sample_data/events.json)
- [`dashboard/index.html`](/Users/chaturya/Documents/New%20project/dashboard/index.html)
- [`tests/test_pipeline.py`](/Users/chaturya/Documents/New%20project/tests/test_pipeline.py)

## Run the demo

```bash
python3 run_demo.py
```

This generates:

- [`output/incidents.json`](/Users/chaturya/Documents/New%20project/output/incidents.json)
- [`output/operator_report.md`](/Users/chaturya/Documents/New%20project/output/operator_report.md)
- [`output/dashboard_data.js`](/Users/chaturya/Documents/New%20project/output/dashboard_data.js)

Then open the dashboard in a browser or serve the directory locally:

```bash
python3 -m http.server 8000
```

Open [dashboard/index.html](/Users/chaturya/Documents/New%20project/dashboard/index.html) and refresh after running the demo.

## MVP assumptions

- Input is a structured event stream derived from CCTV preprocessing rather than raw video.
- Multimodal review is represented by a local offline reviewer so the repo remains runnable without API keys.
- The review payload is intentionally shaped so a future Gemma integration can replace the heuristic reviewer with minimal changes.

## Next step for hackathon submission

- swap the heuristic reviewer for a Gemma 4 or Gemma-family multimodal inference endpoint
- attach actual event frame thumbnails
- record a short demo walkthrough
- add a benchmark set showing reduction in footage sent for heavy review
