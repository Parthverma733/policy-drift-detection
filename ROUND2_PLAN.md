# Round 2 Implementation Plan

## Current Prototype Scope (Round 1)

The current prototype demonstrates the core concept of policy–implementation drift detection in a controlled, minimal setup. It includes:

- Policy intent parsing from structured JSON
- Implementation data loading from CSV
- Rule-based metric drift detection
- Temporal drift detection across time periods
- Text-based, explainable reporting via command line

The prototype is intentionally limited in scope to validate the core idea rather than completeness or scale.

## Planned Technical Direction (Round 2)

### Detection Methodology

The system will continue to use deterministic, rule-based evaluation rather than statistical or predictive modeling.

Planned enhancements include:

**Policy-Driven Rules**

- Policy intent will define target groups, constraints, and thresholds declaratively.
- Adding or modifying rules will not require changes to detection logic.

**Expanded Constraint Evaluation**

- Minimum and maximum threshold checks
- Temporal consistency checks across longer periods
- Cross-district comparison to identify outliers in implementation behavior

**Severity Classification Refinement**

- Severity levels (low / medium / high) derived from deviation magnitude
- Thresholds configurable through policy intent rather than hardcoded values

### System Design Principles

The following principles will guide Round-2 development:

- **Deterministic**: Identical inputs always produce identical outputs
- **Explainable**: Every detected drift is linked to a specific policy rule
- **Rule-based**: No machine learning or probabilistic inference
- **Minimal Dependencies**: Focus on transparency and maintainability

These principles are essential for governance-facing systems.

## Planned Extensions to Data Handling

### Policy Intent

Policy intent will be extended to support:

- Multiple constraint types per scheme
- Configurable severity thresholds
- Scheme metadata for multi-scheme execution

### Implementation Data

Implementation data handling will be extended to:

- Support longer time windows
- Validate schema consistency
- Handle missing or incomplete records gracefully

## Identified Limitations (Current)

The current prototype has the following limitations, which Round-2 will address:

- Single policy scheme per execution
- Fixed input schema
- Synthetic demonstration data
- No cross-scheme or cross-period trend analysis

These constraints are intentional in Round-1 and form the basis for planned expansion.

## Planned Enhancements

In Round-2, the system will focus on:

### Multi-Scheme Support

Process multiple policy schemes within a single execution pipeline.

### Trend-Level Drift Analysis

Identify repeated or systematic drift patterns across districts and time.

### Exportable Outputs

Enable structured export (CSV/JSON) for downstream analysis or audit workflows.

### Input Validation and Error Handling

Ensure robustness against malformed policy intent or implementation data.

## Evaluation Readiness

The Round-2 system will emphasize:

- Clear separation of components
- Predictable and reproducible behavior
- Human-readable explanations suitable for decision-makers
- Incremental enhancement over the Round-1 prototype

The focus remains on policy–implementation alignment, not on automation of decision-making.
