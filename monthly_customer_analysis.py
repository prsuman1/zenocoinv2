#!/usr/bin/env python3
"""
MONTHLY CUSTOMER LEVEL ANALYSIS
All metrics calculated at customer-month level
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("MONTHLY CUSTOMER LEVEL ANALYSIS - ZENOCOIN REWARDS")
print("="*80)

# Load data
print("\n1. Loading and preprocessing data...")
df = pd.read_csv('data dump for suman part 2.csv')
df['bill_date'] = pd.to_datetime(df['bill_date'])
df['first-bill-date'] = pd.to_datetime(df['first-bill-date'])
df['month'] = df['bill_date'].dt.to_period('M')

# Focus on gross transactions only
gross_df = df[df['bill-flag'] == 'gross'].copy()

# Identify ZenoCoin usage
gross_df['used_zenocoin'] = ((gross_df['zrd_promo_discount'] > 0) | 
                             (gross_df['freebee_cost'] > 0) | 
                             (gross_df['promo-code'].str.startswith('ZRD', na=False))).astype(int)

print(f"Total gross transactions: {len(gross_df):,}")
print(f"Date range: {gross_df['bill_date'].min()} to {gross_df['bill_date'].max()}")

# ==========================================
# MONTHLY CUSTOMER AGGREGATION
# ==========================================
print("\n2. Creating monthly customer aggregations...")

# Aggregate at customer-month level
monthly_customer = gross_df.groupby(['patient-id', 'month']).agg({
    'revenue-value': 'sum',  # Total monthly spend
    'id': 'count',  # Number of transactions in month
    'used_zenocoin': 'max',  # 1 if used ZC at least once in month
    'eligibility_flag': 'max',  # 1 if eligible at least once in month
    'zrd_promo_discount': 'sum',
    'freebee_cost': 'sum',
    'bill_date': ['min', 'max']
}).reset_index()

# Flatten column names
monthly_customer.columns = ['patient_id', 'month', 'monthly_spend', 'monthly_transactions', 
                           'used_zc_in_month', 'eligible_in_month', 'zrd_discount', 
                           'freebee_discount', 'first_date_month', 'last_date_month']

monthly_customer['total_zc_discount'] = monthly_customer['zrd_discount'] + monthly_customer['freebee_discount']

print(f"Total customer-months: {len(monthly_customer):,}")
print(f"Unique customers: {monthly_customer['patient_id'].nunique():,}")
print(f"Unique months: {monthly_customer['month'].nunique()}")

# ==========================================
# KEY MONTHLY METRICS
# ==========================================
print("\n3. MONTHLY CUSTOMER METRICS")
print("-"*40)

# Overall monthly statistics
total_customer_months = len(monthly_customer)
zc_customer_months = monthly_customer[monthly_customer['used_zc_in_month'] == 1]
non_zc_customer_months = monthly_customer[monthly_customer['used_zc_in_month'] == 0]

print(f"Customer-months with ZenoCoin: {len(zc_customer_months):,} ({len(zc_customer_months)/total_customer_months*100:.1f}%)")
print(f"Customer-months without ZenoCoin: {len(non_zc_customer_months):,}")

# Average monthly spend comparison
avg_monthly_spend_zc = zc_customer_months['monthly_spend'].mean()
avg_monthly_spend_non_zc = non_zc_customer_months['monthly_spend'].mean()
monthly_spend_lift = avg_monthly_spend_zc - avg_monthly_spend_non_zc
monthly_spend_lift_pct = (monthly_spend_lift / avg_monthly_spend_non_zc * 100) if avg_monthly_spend_non_zc > 0 else 0

print(f"\nMonthly Spend Analysis:")
print(f"  Avg monthly spend (ZC months): ₹{avg_monthly_spend_zc:,.0f}")
print(f"  Avg monthly spend (Non-ZC months): ₹{avg_monthly_spend_non_zc:,.0f}")
print(f"  Monthly spend lift: ₹{monthly_spend_lift:,.0f} ({monthly_spend_lift_pct:+.1f}%)")

# Monthly transaction frequency
avg_monthly_trans_zc = zc_customer_months['monthly_transactions'].mean()
avg_monthly_trans_non_zc = non_zc_customer_months['monthly_transactions'].mean()

print(f"\nMonthly Transaction Frequency:")
print(f"  Avg transactions/month (ZC): {avg_monthly_trans_zc:.1f}")
print(f"  Avg transactions/month (Non-ZC): {avg_monthly_trans_non_zc:.1f}")
print(f"  Frequency lift: +{(avg_monthly_trans_zc/avg_monthly_trans_non_zc - 1)*100:.1f}%")

# ==========================================
# JULY ONWARDS REDEMPTION (MONTHLY)
# ==========================================
print("\n4. POST-JULY REDEMPTION ANALYSIS (Monthly)")
print("-"*40)

july_onwards_monthly = monthly_customer[monthly_customer['month'] >= pd.Period('2025-07')]
july_eligible_months = july_onwards_monthly[july_onwards_monthly['eligible_in_month'] == 1]
july_redeemed_months = july_eligible_months[july_eligible_months['used_zc_in_month'] == 1]

monthly_redemption_rate = len(july_redeemed_months) / len(july_eligible_months) * 100 if len(july_eligible_months) > 0 else 0

print(f"Eligible customer-months (July+): {len(july_eligible_months):,}")
print(f"Redeemed customer-months: {len(july_redeemed_months):,}")
print(f"Monthly redemption rate: {monthly_redemption_rate:.1f}%")

# ==========================================
# CUSTOMER LIFETIME ANALYSIS (MONTHLY)
# ==========================================
print("\n5. CUSTOMER LIFETIME ANALYSIS")
print("-"*40)

# Aggregate by customer across all months
customer_lifetime = monthly_customer.groupby('patient_id').agg({
    'monthly_spend': 'sum',  # Total lifetime spend
    'monthly_transactions': 'sum',  # Total lifetime transactions
    'month': 'nunique',  # Number of active months
    'used_zc_in_month': 'max',  # Ever used ZC
    'total_zc_discount': 'sum'  # Total discounts received
}).reset_index()

customer_lifetime.columns = ['patient_id', 'total_spend', 'total_transactions', 
                            'active_months', 'is_zc_user', 'total_discounts']

# Calculate average monthly spend
customer_lifetime['avg_monthly_spend'] = customer_lifetime['total_spend'] / customer_lifetime['active_months']

# Split customers
zc_customers = customer_lifetime[customer_lifetime['is_zc_user'] == 1]
non_zc_customers = customer_lifetime[customer_lifetime['is_zc_user'] == 0]

print(f"ZenoCoin users (ever): {len(zc_customers):,} ({len(zc_customers)/len(customer_lifetime)*100:.1f}%)")
print(f"Non-ZenoCoin users: {len(non_zc_customers):,}")

print("\nLifetime Comparison:")
print(f"{'Metric':<30} {'ZC Users':>15} {'Non-ZC':>15} {'Lift':>10}")
print("-"*70)

metrics = [
    ('Avg Monthly Spend (₹)', 'avg_monthly_spend'),
    ('Total Lifetime Spend (₹)', 'total_spend'),
    ('Active Months', 'active_months'),
    ('Total Transactions', 'total_transactions'),
    ('Avg Trans/Month', lambda df: df['total_transactions'] / df['active_months'])
]

for name, col in metrics:
    if callable(col):
        zc_val = col(zc_customers).mean()
        non_zc_val = col(non_zc_customers).mean()
    else:
        zc_val = zc_customers[col].mean()
        non_zc_val = non_zc_customers[col].mean()
    
    lift = ((zc_val / non_zc_val - 1) * 100) if non_zc_val > 0 else 0
    
    if '₹' in name:
        print(f"{name:<30} {zc_val:>15,.0f} {non_zc_val:>15,.0f} {lift:>9.1f}%")
    else:
        print(f"{name:<30} {zc_val:>15.1f} {non_zc_val:>15.1f} {lift:>9.1f}%")

# ==========================================
# MONTHLY RETENTION ANALYSIS
# ==========================================
print("\n6. MONTHLY RETENTION ANALYSIS")
print("-"*40)

# For each customer who used ZC, check if they came back next month
retention_analysis = []

for customer_id in zc_customers['patient_id']:
    customer_months = monthly_customer[monthly_customer['patient_id'] == customer_id].sort_values('month')
    
    # Find first month with ZC use
    first_zc_month = customer_months[customer_months['used_zc_in_month'] == 1]['month'].min()
    
    if pd.notna(first_zc_month):
        # Check if they had activity in next month
        next_month = first_zc_month + 1
        had_next_month = any(customer_months['month'] == next_month)
        
        retention_analysis.append({
            'customer_id': customer_id,
            'first_zc_month': first_zc_month,
            'retained_next_month': had_next_month
        })

if retention_analysis:
    retention_df = pd.DataFrame(retention_analysis)
    monthly_retention = retention_df['retained_next_month'].mean() * 100
    print(f"Monthly retention after first ZC use: {monthly_retention:.1f}%")
else:
    monthly_retention = 0

# ==========================================
# ROI CALCULATION (MONTHLY BASED)
# ==========================================
print("\n7. ROI ANALYSIS (Monthly Customer Level)")
print("-"*40)

# Total investment
total_investment = monthly_customer['total_zc_discount'].sum()

# Incremental monthly value
incremental_monthly_spend = avg_monthly_spend_zc - avg_monthly_spend_non_zc
incremental_lifetime_value = zc_customers['total_spend'].mean() - non_zc_customers['total_spend'].mean()

# Calculate ROI
# Method 1: Based on incremental monthly spend
monthly_roi = (incremental_monthly_spend * len(zc_customer_months) - total_investment) / total_investment * 100 if total_investment > 0 else 0

# Method 2: Based on lifetime value
ltv_roi = (incremental_lifetime_value * len(zc_customers) - total_investment) / total_investment * 100 if total_investment > 0 else 0

print(f"Total ZenoCoin investment: ₹{total_investment:,.0f}")
print(f"Incremental monthly spend: ₹{incremental_monthly_spend:,.0f}")
print(f"Incremental lifetime value: ₹{incremental_lifetime_value:,.0f}")
print(f"\nMonthly-based ROI: {monthly_roi:.1f}%")
print(f"LTV-based ROI: {ltv_roi:.1f}%")

# ==========================================
# MONTH-BY-MONTH TRENDS
# ==========================================
print("\n8. MONTH-BY-MONTH TRENDS")
print("-"*40)

monthly_summary = monthly_customer.groupby('month').agg({
    'patient_id': 'nunique',  # MAU
    'monthly_spend': 'mean',  # Avg spend per customer
    'used_zc_in_month': 'sum',  # ZC users in month
    'eligible_in_month': 'sum',  # Eligible users in month
    'total_zc_discount': 'sum'  # Total discounts given
}).reset_index()

monthly_summary.columns = ['month', 'mau', 'avg_monthly_spend', 'zc_users', 'eligible_users', 'total_discounts']
monthly_summary['redemption_rate'] = monthly_summary['zc_users'] / monthly_summary['eligible_users'] * 100

print("Monthly Trends:")
print(monthly_summary.to_string(index=False))

# ==========================================
# SAVE PROCESSED DATA
# ==========================================
print("\n9. SAVING MONTHLY ANALYSIS DATA...")
print("-"*40)

# Save monthly customer data
monthly_customer.to_csv('monthly_customer_data.csv', index=False)

# Save customer lifetime data
customer_lifetime.to_csv('customer_lifetime_monthly.csv', index=False)

# Save summary metrics
summary_monthly = {
    'total_customers': len(customer_lifetime),
    'zc_customers': len(zc_customers),
    'avg_monthly_spend_zc': avg_monthly_spend_zc,
    'avg_monthly_spend_non_zc': avg_monthly_spend_non_zc,
    'monthly_spend_lift': monthly_spend_lift,
    'monthly_spend_lift_pct': monthly_spend_lift_pct,
    'monthly_redemption_rate': monthly_redemption_rate,
    'monthly_retention': monthly_retention,
    'total_investment': total_investment,
    'monthly_roi': monthly_roi,
    'ltv_roi': ltv_roi,
    'incremental_ltv': incremental_lifetime_value,
    'avg_active_months_zc': zc_customers['active_months'].mean(),
    'avg_active_months_non_zc': non_zc_customers['active_months'].mean()
}

pd.DataFrame([summary_monthly]).to_csv('summary_monthly_metrics.csv', index=False)

# Save monthly trends
monthly_summary.to_csv('monthly_trends.csv', index=False)

print("Monthly analysis complete! All data saved.")
print("="*80)