#!/usr/bin/env python3
"""
Calculate 7-day and 30-day retention rates for ZenoCoin users vs non-users
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_retention_rates():
    # Load transaction data
    print("Loading transaction data...")
    df = pd.read_csv('data dump for suman part 2.csv')
    
    # Convert date column
    df['date'] = pd.to_datetime(df['bill_date'])
    
    # Identify ZenoCoin transactions - check if zenocoin columns exist
    zenocoin_cols = [col for col in df.columns if 'zenocoin' in col.lower() or 'zeno' in col.lower()]
    if zenocoin_cols:
        # Use any zenocoin-related column to identify usage
        df['used_zenocoin'] = (df[zenocoin_cols].sum(axis=1) > 0).astype(int)
    else:
        # Use eligibility and promo as proxy
        df['used_zenocoin'] = ((df['eligibility_flag'] == 1) & (df['zrd_promo_discount'] > 0)).astype(int)
    
    # Get customer-level data
    customer_dates = df.groupby('patient-id').agg({
        'date': ['min', 'max'],
        'used_zenocoin': 'max'
    }).reset_index()
    customer_dates.columns = ['patient_id', 'first_date', 'last_date', 'is_zc_user']
    
    # For each customer, check if they returned within 7 and 30 days
    print("Calculating retention rates...")
    
    retention_data = []
    
    for _, customer in customer_dates.iterrows():
        customer_id = customer['patient_id']
        customer_df = df[df['patient-id'] == customer_id].sort_values('date')
        
        # Get unique transaction dates
        transaction_dates = customer_df['date'].dt.date.unique()
        
        if len(transaction_dates) > 1:
            first_date = transaction_dates[0]
            
            # Check 7-day retention
            returned_7d = any((d - first_date).days <= 7 and (d - first_date).days > 0 
                            for d in transaction_dates)
            
            # Check 30-day retention  
            returned_30d = any((d - first_date).days <= 30 and (d - first_date).days > 0 
                             for d in transaction_dates)
            
            retention_data.append({
                'patient_id': customer_id,
                'is_zc_user': customer['is_zc_user'],
                'returned_7d': returned_7d,
                'returned_30d': returned_30d
            })
    
    retention_df = pd.DataFrame(retention_data)
    
    # Calculate retention rates
    print("\n=== RETENTION ANALYSIS ===\n")
    
    # Overall retention
    for user_type in [0, 1]:
        label = "ZenoCoin Users" if user_type == 1 else "Non-ZC Users"
        subset = retention_df[retention_df['is_zc_user'] == user_type]
        
        if len(subset) > 0:
            retention_7d = subset['returned_7d'].mean() * 100
            retention_30d = subset['returned_30d'].mean() * 100
            
            print(f"{label}:")
            print(f"  7-Day Retention: {retention_7d:.1f}%")
            print(f"  30-Day Retention: {retention_30d:.1f}%")
            print(f"  Sample Size: {len(subset):,} customers")
            print()
    
    # Calculate lift
    zc_retention = retention_df[retention_df['is_zc_user'] == 1]
    non_zc_retention = retention_df[retention_df['is_zc_user'] == 0]
    
    if len(zc_retention) > 0 and len(non_zc_retention) > 0:
        zc_7d = zc_retention['returned_7d'].mean() * 100
        non_zc_7d = non_zc_retention['returned_7d'].mean() * 100
        zc_30d = zc_retention['returned_30d'].mean() * 100
        non_zc_30d = non_zc_retention['returned_30d'].mean() * 100
        
        print("=== RETENTION LIFT ===")
        print(f"7-Day Retention Lift: {(zc_7d/non_zc_7d - 1)*100:.1f}%")
        print(f"30-Day Retention Lift: {(zc_30d/non_zc_30d - 1)*100:.1f}%")
    
    # Save retention data
    retention_summary = pd.DataFrame([
        {'metric': '7_day_retention_zc', 'value': zc_7d},
        {'metric': '7_day_retention_non_zc', 'value': non_zc_7d},
        {'metric': '30_day_retention_zc', 'value': zc_30d},
        {'metric': '30_day_retention_non_zc', 'value': non_zc_30d},
        {'metric': '7_day_lift', 'value': (zc_7d/non_zc_7d - 1)*100},
        {'metric': '30_day_lift', 'value': (zc_30d/non_zc_30d - 1)*100}
    ])
    
    retention_summary.to_csv('retention_comparison.csv', index=False)
    print("\nRetention data saved to retention_comparison.csv")
    
    return retention_summary

if __name__ == "__main__":
    calculate_retention_rates()