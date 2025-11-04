# ZenoCoin Analytics Dashboard

A comprehensive analytics dashboard for ZenoCoin rewards program analysis, featuring monthly customer-level metrics, ROI calculations, and behavioral impact analysis.

## Features

### 📊 Executive Summary
- Key performance metrics and program health indicators
- Real-time ROI tracking
- Monthly trends visualization

### 💰 Monthly Spend Analysis  
- Customer spending patterns by ZenoCoin usage
- Comparative analysis between ZC and non-ZC users
- Spend distribution visualizations

### 👥 Customer Segmentation
- Behavioral segmentation based on spending and frequency
- High-value customer identification
- Segment migration analysis

### 📈 Retention & Frequency
- 7-day and 30-day retention comparisons
- Purchase frequency patterns
- Retention lift analysis

### 🆕 New User Cohorts
- ZC-acquired vs NonZC-acquired customer analysis
- Order progression tracking
- Lifetime value comparisons
- ROI calculations for acquisition strategies

### 🔄 ZC Adoption Impact
- Before/After adoption behavior analysis
- Time-based evolution tracking
- Individual customer transformation metrics
- Post-adoption retention impact

### 💵 ROI Calculator
- Advanced impact modeling with ML predictions
- Scenario planning with single input variable
- Confidence intervals and risk assessment
- Detailed KPI documentation

### 📉 Trends & Patterns
- Monthly trend analysis
- Growth trajectory visualization
- Seasonal patterns identification

## Installation

```bash
# Clone the repository
git clone https://github.com/prsuman1/zenocoinv2.git
cd zenocoinv2

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run zenocoin_monthly_app.py
```

## Key Metrics

- **Current Redemption Rate**: 21%
- **Average Monthly Spend Lift**: +74.2% for ZC users
- **7-Day Retention Lift**: +8.9% for ZC users
- **30-Day Retention Lift**: +11.6% for ZC users
- **New User LTV Lift**: +59.5% for ZC-acquired customers

## Data Requirements

The dashboard requires transaction-level data with the following fields:
- `patient-id`: Customer identifier
- `bill_date`: Transaction date
- `revenue-value`: Transaction amount
- `eligibility_flag`: ZenoCoin eligibility indicator
- `first-bill-date`: Customer's first transaction date
- Various discount fields for ZenoCoin usage tracking

## Technologies

- **Streamlit**: Interactive web application
- **Pandas**: Data processing and analysis
- **Plotly**: Interactive visualizations
- **Scikit-learn**: Machine learning models
- **NumPy/SciPy**: Statistical analysis

## Theme Support

The dashboard includes both light and dark mode themes with a toggle switch for user preference.

## License

Proprietary - All rights reserved
