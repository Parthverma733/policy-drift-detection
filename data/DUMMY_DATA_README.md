# Dummy Datasets Documentation

This directory contains comprehensive dummy datasets and policy files for testing the Policy Drift Detection system.

## Dataset Files

### Education Policy Datasets

1. **`dummy_education_implementation_q1_2024.csv`**
   - 10 districts (D001-D010)
   - 3 months of data (Jan-Mar 2024)
   - Mix of high and low performing districts
   - Contains districts with varying literacy rates (48.3% - 85.2%)
   - Good for testing baseline drift detection

2. **`dummy_education_implementation_q2_2024.csv`**
   - Continuation from Q1 with some new districts
   - 3 months of data (Apr-Jun 2024)
   - Includes districts D001-D005 from Q1 plus new districts D011-D012
   - Useful for temporal analysis and trend detection

3. **`dummy_education_with_drift_issues.csv`**
   - 5 districts with intentional drift issues
   - ED001: Very low coverage (48-55%), high variance (38-52%)
   - ED002: High variance issues (18-35%)
   - ED003: Low fund utilization (39-45%), below threshold
   - ED004: Consistent performer (good for baseline)
   - ED005: Declining coverage trend (82.5% → 74.1%)
   - Perfect for testing drift detection accuracy

### Health Policy Datasets

4. **`dummy_health_implementation_2024.csv`**
   - 10 health districts (H001-H010)
   - 3 months of data (Jan-Mar 2024)
   - Wide range: Urban (86.7% literacy) to Tribal (46.5% literacy)
   - Coverage: 48.7% - 95.1%
   - Fund utilization: 33.9% - 92.8%
   - Good for testing domain-specific drift detection

5. **`dummy_health_with_compliance.csv`**
   - 5 well-managed districts
   - All districts meeting policy thresholds
   - Low variance (2.5% - 10.8%)
   - High coverage (74.5% - 95.1%)
   - Good fund utilization (68.2% - 92.8%)
   - Useful for testing negative cases (no drift)

### Agriculture Policy Datasets

6. **`dummy_agriculture_implementation_2024.csv`**
   - 10 agriculture districts (A001-A010)
   - 3 months of data (Jan-Mar 2024)
   - Mix of commercial farms (80.3% literacy) to subsistence (48.9% literacy)
   - Coverage: 51.1% - 88.4%
   - Fund utilization: 35.4% - 81.9%
   - Monthly variance: 5.9% - 45.8%
   - Accounts for seasonal variations

### Infrastructure Policy Datasets

7. **`dummy_infrastructure_implementation_2024.csv`**
   - 10 infrastructure zones (I001-I010)
   - 3 months of data (Jan-Mar 2024)
   - Urban zones (83.5% literacy) to Remote areas (52.4% literacy)
   - Coverage: 55.8% - 95.1%
   - Fund utilization: 40.1% - 92.8%
   - Monthly variance: 2.5% - 36.2%
   - Includes various infrastructure types (roads, power, water, telecom)

## Policy Intent JSON Files

### Domain-Specific Policy Intents

1. **`policy_intent.json`** (Original - Education)
   - Basic education policy
   - Priority districts: literacy_rate < 65%
   - Coverage threshold: 75%
   - Variance threshold: 15%
   - Fund utilization: 60%

2. **`dummy_policy_intent_health.json`**
   - Health coverage policy
   - Priority districts: literacy_rate < 60%
   - Coverage thresholds: 80% (priority), 85% (standard)
   - Variance threshold: 12%
   - Fund utilization: 75% (priority), 80% (standard)

3. **`dummy_policy_intent_agriculture.json`**
   - Agriculture support policy
   - Priority districts: literacy_rate < 65%
   - Coverage thresholds: 70% (priority), 75% (standard)
   - Variance threshold: 20% (accounts for seasonality)
   - Fund utilization: 60% (priority), 65% (standard)

4. **`dummy_policy_intent_infrastructure.json`**
   - Infrastructure development policy
   - Three-tier system: priority (<65%), standard (65-85%), urban (>80%)
   - Coverage thresholds: 70%, 80%, 85% respectively
   - Variance threshold: 15%
   - Fund utilization: 70% (priority), 75% (standard)

5. **`dummy_policy_intent_education_strict.json`**
   - Strict education policy (high thresholds)
   - Priority districts: literacy_rate < 65%
   - Coverage thresholds: 90% (priority), 85% (standard)
   - Variance threshold: 8% (very strict)
   - Fund utilization: 92% (priority), 88% (standard)
   - Useful for testing with datasets that will have many drifts

## Policy Text Files (TXT Format)

1. **`dummy_health_policy.txt`**
   - Full policy document for health coverage
   - Can be parsed by PolicyParser
   - Contains all key elements: objectives, targets, constraints, temporal requirements

2. **`dummy_agriculture_policy.txt`**
   - Full policy document for agriculture support
   - Contains domain-specific language and requirements
   - Includes seasonal considerations

3. **`dummy_infrastructure_policy.txt`**
   - Full policy document for infrastructure development
   - Multi-tier target group definitions
   - Infrastructure-specific metrics

## CSV Data Format

All CSV files follow this structure:
```csv
district_id,district_name,literacy_rate,population,coverage_percentage,fund_utilization,month,monthly_variance
```

### Field Descriptions:
- **district_id**: Unique identifier (e.g., D001, H001, A001, I001)
- **district_name**: Human-readable district name
- **literacy_rate**: Literacy rate percentage (used for target group classification)
- **population**: District population (used for priority classification)
- **coverage_percentage**: Policy coverage percentage (primary metric)
- **fund_utilization**: Fund utilization percentage (resource allocation metric)
- **month**: Reporting month in YYYY-MM format
- **monthly_variance**: Month-over-month variance percentage (temporal consistency metric)

## Testing Scenarios

### Scenario 1: Basic Drift Detection
- Use: `dummy_education_implementation_q1_2024.csv` + `policy_intent.json`
- Expected: Drifts in D005, D006, D008, D010 (low coverage, high variance)

### Scenario 2: Temporal Analysis
- Use: `dummy_education_implementation_q1_2024.csv` + `dummy_education_implementation_q2_2024.csv` + `policy_intent.json`
- Expected: Temporal drift patterns across quarters

### Scenario 3: Strict Policy Testing
- Use: `dummy_education_with_drift_issues.csv` + `dummy_policy_intent_education_strict.json`
- Expected: Multiple drifts detected (ED001, ED002, ED003, ED005)

### Scenario 4: Health Domain
- Use: `dummy_health_implementation_2024.csv` + `dummy_policy_intent_health.json`
- Expected: Drifts in H002, H003, H006, H008, H009

### Scenario 5: Compliance Testing (No Drifts)
- Use: `dummy_health_with_compliance.csv` + `dummy_policy_intent_health.json`
- Expected: No or minimal drifts detected

### Scenario 6: Agriculture with Seasonality
- Use: `dummy_agriculture_implementation_2024.csv` + `dummy_policy_intent_agriculture.json`
- Expected: Some drifts, but higher variance threshold accounts for seasonality

### Scenario 7: Multi-Domain Comparison
- Run all domain datasets with their respective policy intents
- Compare drift patterns across domains

## Data Characteristics Summary

| Dataset | Districts | Months | Avg Coverage | Avg Utilization | Avg Variance | Drift Potential |
|---------|-----------|--------|--------------|-----------------|--------------|-----------------|
| Education Q1 2024 | 10 | 3 | 69.8% | 59.2% | 20.4% | Medium-High |
| Education Q2 2024 | 7 | 3 | 72.1% | 61.3% | 18.7% | Medium |
| Education with Issues | 5 | 3 | 63.8% | 47.8% | 30.5% | High |
| Health 2024 | 10 | 3 | 72.3% | 62.4% | 22.8% | High |
| Health Compliance | 5 | 3 | 86.6% | 81.8% | 6.4% | Low |
| Agriculture 2024 | 10 | 3 | 69.4% | 60.2% | 19.7% | Medium |
| Infrastructure 2024 | 10 | 3 | 74.2% | 66.8% | 16.9% | Medium |

## Notes

- All datasets use realistic but synthetic data
- District IDs follow domain prefixes (D=Education, H=Health, A=Agriculture, I=Infrastructure)
- Time periods are consistent (2024) for cross-domain analysis
- Variance values are calculated to represent realistic month-over-month fluctuations
- Some datasets intentionally contain drift issues for testing purposes
- Coverage and utilization percentages are designed to test threshold violations

## Usage Examples

### Upload via API:
```bash
# Upload education dataset
curl -X POST "http://localhost:8000/datasets/upload" \
  -F "file=@data/dummy_education_implementation_q1_2024.csv" \
  -F "policy_id=<policy_id>" \
  -F "region_level=district" \
  -F "time_range_start=2024-01" \
  -F "time_range_end=2024-03"
```

### Detect Drift:
```bash
# Run drift detection
curl -X POST "http://localhost:8000/drift/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "<policy_id>",
    "dataset_id": "<dataset_id>"
  }'
```
