# Architecture

## System Design

The system follows a modular, rule-based architecture with four core components:

### 1. Intent Parser (`intent_parser.py`)

**Responsibility**: Parses policy intent from JSON configuration.

**Components**:
- `PolicyIntent`: Data structure representing parsed policy rules
- `load_policy_intent()`: JSON file loader
- `matches_target_group()`: District classification logic

**Design decisions**:
- Policy intent is immutable after parsing
- Target group matching uses explicit criteria evaluation
- No external dependencies beyond standard library

### 2. Drift Detector (`drift_detector.py`)

**Responsibility**: Compares implementation data against policy intent to identify violations.

**Components**:
- `DriftResult`: Represents a single drift instance
- `classify_district()`: Maps districts to target groups
- `check_metric_constraint()`: Evaluates metric values against thresholds
- `detect_metric_drift()`: Identifies metric-based violations
- `detect_temporal_drift()`: Identifies temporal inconsistency
- `detect_all_drift()`: Orchestrates full detection process

**Detection logic**:
- Metric drift: Compares actual values against constraint thresholds
- Temporal drift: Calculates variance across months for districts
- Severity calculation: Based on deviation magnitude from thresholds

**Design decisions**:
- Deterministic rule-based evaluation
- Separate functions for metric and temporal analysis
- Severity levels (low/medium/high) based on percentage deviation

### 3. Explanation Generator (`explain.py`)

**Responsibility**: Converts drift results into human-readable text.

**Components**:
- `explain_drift()`: Generates explanation for single drift
- `generate_summary()`: Creates aggregate statistics
- `format_drift_report()`: Assembles complete report

**Design decisions**:
- Text-only output suitable for terminal
- Context-aware explanations based on constraint type
- Structured summary with counts and categorizations

### 4. Main CLI (`main.py`)

**Responsibility**: Entry point and data loading.

**Components**:
- `load_implementation_data()`: CSV file parser
- `main()`: Orchestrates execution flow

**Design decisions**:
- Simple file path resolution relative to script location
- Error handling for missing files
- Minimal output formatting

## Data Flow

1. **Input**: Policy intent JSON and implementation CSV
2. **Parsing**: Policy intent loaded into `PolicyIntent` object
3. **Classification**: Districts matched to target groups
4. **Detection**: Implementation data evaluated against constraints
5. **Explanation**: Drift results formatted as text report
6. **Output**: Terminal display of findings

## Constraints and Rules

The system evaluates three constraint types:

1. **Minimum Coverage**: Ensures priority districts meet coverage thresholds
2. **Temporal Consistency**: Limits variance in metrics across time periods
3. **Resource Allocation**: Verifies fund utilization meets minimum requirements

Each constraint specifies:
- Metric to evaluate
- Threshold value
- Target group applicability

## Extensibility

The architecture supports adding new constraint types by:
- Extending constraint definitions in JSON
- Adding evaluation logic in `check_metric_constraint()`
- Adding explanation templates in `explain_drift()`

No changes required to core detection flow.

