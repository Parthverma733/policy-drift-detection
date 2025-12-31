# Automated Detection of Policy–Implementation Drift in Government Schemes

A command-line tool that detects misalignment between policy intent and implementation data in government schemes.

## Overview

This system compares structured policy rules against district-level implementation outcomes to identify instances where implementation contradicts policy intent, even when data appears valid.

## Features

- Parses policy intent from structured JSON configuration
- Loads implementation data from CSV files
- Detects metric-based drift (coverage, resource allocation violations)
- Detects temporal drift (inconsistent implementation across time periods)
- Generates human-readable explanations for each detected drift

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

The tool reads policy intent from `data/policy_intent.json` and implementation data from `data/implementation_data.csv`, then outputs a drift detection report to the terminal.

## Project Structure

```
policy-drift-detection/
├── README.md
├── ARCHITECTURE.md
├── ROUND2_PLAN.md
├── data/
│   ├── policy_intent.json
│   └── implementation_data.csv
├── src/
│   ├── main.py
│   ├── intent_parser.py
│   ├── drift_detector.py
│   └── explain.py
└── requirements.txt
```

## Data Format

### Policy Intent (JSON)

Defines target groups, constraints, and metric thresholds:

- `target_groups`: District classification criteria
- `constraints`: Policy rules (minimum coverage, temporal consistency, resource allocation)
- `target_metrics`: Expected metric ranges

### Implementation Data (CSV)

District-level records with columns:
- `district_id`, `district_name`: District identifiers
- `literacy_rate`, `population`: Classification attributes
- `coverage_percentage`, `fund_utilization`, `monthly_variance`: Implementation metrics
- `month`: Time period identifier

## Output

The tool produces a text report containing:
- Summary statistics (total drifts, by type, by severity)
- Detailed explanations for each detected drift instance
- District and month identifiers for each violation

# policy-drift-detection
# policy-drift-detection
# policy-drift-detection
# policy-drift-detection
