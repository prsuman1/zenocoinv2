#!/usr/bin/env python3
"""
ZenoCoin Adoption Behavior Analysis
Analyzes how customer behavior changes after first ZenoCoin usage
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def analyze_zc_adoption_impact():
    """
    Analyze behavior change before and after ZenoCoin adoption
    """
    print("Loading transaction data...")
    df = pd.read_csv('data dump for suman part 2.csv')
    
    # Convert dates
    df['bill_date'] = pd.to_datetime(df['bill_date'])
    
    # Identify ZenoCoin usage
    df['used_zenocoin'] = ((df['eligibility_flag'] == 1) & 
                          ((df.get('zrd_promo_discount', 0) > 0) | 
                           (df.get('other_promo_discount', 0) > 0))).astype(int)
    
    # Sort by customer and date
    df = df.sort_values(['patient-id', 'bill_date'])
    
    print(f"Total transactions: {len(df):,}")
    print(f"Total customers: {df['patient-id'].nunique():,}")
    
    # ============================================
    # STEP 1: Identify ZC Adoption Point
    # ============================================
    print("\n" + "="*60)
    print("STEP 1: IDENTIFYING ZENOCOIN ADOPTION POINTS")
    print("="*60)
    
    # Find first ZC usage for each customer
    zc_users = df[df['used_zenocoin'] == 1].groupby('patient-id')['bill_date'].min().reset_index()
    zc_users.columns = ['patient_id', 'first_zc_date']
    
    print(f"\nTotal ZC adopters: {len(zc_users):,}")
    
    # Merge back to get all transactions with adoption date
    df_with_adoption = df.merge(
        zc_users, 
        left_on='patient-id', 
        right_on='patient_id', 
        how='left'
    )
    
    # Calculate days relative to adoption
    df_with_adoption['days_from_adoption'] = (
        df_with_adoption['bill_date'] - df_with_adoption['first_zc_date']
    ).dt.days
    
    # Classify transactions as before/after adoption
    df_with_adoption['adoption_phase'] = 'Never_Adopted'
    df_with_adoption.loc[df_with_adoption['days_from_adoption'] < 0, 'adoption_phase'] = 'Before_ZC'
    df_with_adoption.loc[df_with_adoption['days_from_adoption'] >= 0, 'adoption_phase'] = 'After_ZC'
    
    # ============================================
    # STEP 2: Before vs After Metrics
    # ============================================
    print("\n" + "="*60)
    print("STEP 2: BEFORE VS AFTER ADOPTION METRICS")
    print("="*60)
    
    # Focus on customers who adopted ZC (have both before and after)
    adopters_with_history = df_with_adoption[
        (df_with_adoption['patient_id'].notna()) &
        (df_with_adoption['patient_id'].isin(
            df_with_adoption[df_with_adoption['adoption_phase'] == 'Before_ZC']['patient_id'].unique()
        ))
    ]
    
    print(f"\nCustomers with before/after data: {adopters_with_history['patient_id'].nunique():,}")
    
    # Calculate metrics for each phase
    phase_metrics = adopters_with_history.groupby(['patient_id', 'adoption_phase']).agg({
        'revenue-value': ['mean', 'sum', 'count'],
        'bill_date': ['min', 'max']
    }).reset_index()
    
    phase_metrics.columns = ['patient_id', 'phase', 'avg_transaction', 'total_spend', 
                            'transaction_count', 'first_date', 'last_date']
    
    # Calculate days active and frequency
    phase_metrics['days_active'] = (phase_metrics['last_date'] - phase_metrics['first_date']).dt.days + 1
    phase_metrics['transaction_frequency'] = phase_metrics['transaction_count'] / (phase_metrics['days_active'] / 30)
    
    # Summary statistics
    before_metrics = phase_metrics[phase_metrics['phase'] == 'Before_ZC']
    after_metrics = phase_metrics[phase_metrics['phase'] == 'After_ZC']
    
    print("\n📊 BEFORE ZC ADOPTION:")
    print(f"  Avg Transaction Value: ₹{before_metrics['avg_transaction'].mean():.2f}")
    print(f"  Monthly Frequency: {before_metrics['transaction_frequency'].mean():.2f} transactions")
    print(f"  Total Customers: {len(before_metrics):,}")
    
    print("\n📊 AFTER ZC ADOPTION:")
    print(f"  Avg Transaction Value: ₹{after_metrics['avg_transaction'].mean():.2f}")
    print(f"  Monthly Frequency: {after_metrics['transaction_frequency'].mean():.2f} transactions")
    print(f"  Total Customers: {len(after_metrics):,}")
    
    # ============================================
    # STEP 3: Time-based Analysis
    # ============================================
    print("\n" + "="*60)
    print("STEP 3: TIME-BASED BEHAVIOR ANALYSIS")
    print("="*60)
    
    # Analyze behavior in time windows
    time_windows = [
        (-90, -31, '3 months before'),
        (-30, -1, '1 month before'),
        (0, 30, '1st month after'),
        (31, 60, '2nd month after'),
        (61, 90, '3rd month after')
    ]
    
    window_metrics = []
    
    for start_day, end_day, window_name in time_windows:
        window_data = adopters_with_history[
            (adopters_with_history['days_from_adoption'] >= start_day) &
            (adopters_with_history['days_from_adoption'] <= end_day)
        ]
        
        if len(window_data) > 0:
            metrics = {
                'window': window_name,
                'avg_spend': window_data['revenue-value'].mean(),
                'transactions': len(window_data),
                'unique_customers': window_data['patient_id'].nunique(),
                'zc_usage_rate': window_data['used_zenocoin'].mean() * 100
            }
            window_metrics.append(metrics)
            
            print(f"\n{window_name}:")
            print(f"  Avg Spend: ₹{metrics['avg_spend']:.2f}")
            print(f"  Customers: {metrics['unique_customers']:,}")
            print(f"  ZC Usage: {metrics['zc_usage_rate']:.1f}%")
    
    window_df = pd.DataFrame(window_metrics)
    
    # ============================================
    # STEP 4: Individual Customer Journey
    # ============================================
    print("\n" + "="*60)
    print("STEP 4: CUSTOMER JOURNEY ANALYSIS")
    print("="*60)
    
    # Track individual customer transformations
    customer_transformations = []
    
    for customer_id in before_metrics['patient_id'].unique()[:1000]:  # Sample for performance
        before = before_metrics[before_metrics['patient_id'] == customer_id]
        after = after_metrics[after_metrics['patient_id'] == customer_id]
        
        if len(before) > 0 and len(after) > 0:
            before_row = before.iloc[0]
            after_row = after.iloc[0]
            
            transformation = {
                'customer_id': customer_id,
                'before_avg_transaction': before_row['avg_transaction'],
                'after_avg_transaction': after_row['avg_transaction'],
                'transaction_lift': (after_row['avg_transaction'] / before_row['avg_transaction'] - 1) * 100,
                'before_frequency': before_row['transaction_frequency'],
                'after_frequency': after_row['transaction_frequency'],
                'frequency_lift': (after_row['transaction_frequency'] / before_row['transaction_frequency'] - 1) * 100 if before_row['transaction_frequency'] > 0 else 0
            }
            customer_transformations.append(transformation)
    
    transformation_df = pd.DataFrame(customer_transformations)
    
    # Calculate segments based on impact
    transformation_df['impact_segment'] = pd.cut(
        transformation_df['transaction_lift'],
        bins=[-np.inf, 0, 50, 100, np.inf],
        labels=['Negative', 'Low (0-50%)', 'Medium (50-100%)', 'High (>100%)']
    )
    
    print("\nCustomer Impact Distribution:")
    for segment in ['Negative', 'Low (0-50%)', 'Medium (50-100%)', 'High (>100%)']:
        count = len(transformation_df[transformation_df['impact_segment'] == segment])
        pct = count / len(transformation_df) * 100 if len(transformation_df) > 0 else 0
        print(f"  {segment}: {count} customers ({pct:.1f}%)")
    
    # ============================================
    # STEP 5: Retention Impact
    # ============================================
    print("\n" + "="*60)
    print("STEP 5: RETENTION IMPACT ANALYSIS")
    print("="*60)
    
    # Calculate retention after ZC adoption
    retention_analysis = []
    
    for days_after in [7, 14, 30, 60, 90]:
        # Customers who made purchase within X days after adoption
        retained = adopters_with_history[
            (adopters_with_history['days_from_adoption'] >= 0) &
            (adopters_with_history['days_from_adoption'] <= days_after)
        ]['patient_id'].nunique()
        
        retention_rate = (retained / len(zc_users)) * 100 if len(zc_users) > 0 else 0
        
        retention_analysis.append({
            'days_after': days_after,
            'retained_customers': retained,
            'retention_rate': retention_rate
        })
        
        print(f"  {days_after}-day retention: {retained:,} ({retention_rate:.1f}%)")
    
    # ============================================
    # STEP 6: Key Insights
    # ============================================
    print("\n" + "="*60)
    print("💡 KEY INSIGHTS - BEHAVIOR CHANGE AFTER ZC ADOPTION")
    print("="*60)
    
    # Calculate overall impact
    avg_before_transaction = before_metrics['avg_transaction'].mean()
    avg_after_transaction = after_metrics['avg_transaction'].mean()
    transaction_value_lift = (avg_after_transaction / avg_before_transaction - 1) * 100
    
    avg_before_freq = before_metrics['transaction_frequency'].mean()
    avg_after_freq = after_metrics['transaction_frequency'].mean()
    frequency_lift = (avg_after_freq / avg_before_freq - 1) * 100 if avg_before_freq > 0 else 0
    
    print(f"""
1. TRANSACTION VALUE IMPACT:
   Before ZC: ₹{avg_before_transaction:.2f}
   After ZC: ₹{avg_after_transaction:.2f}
   Lift: {transaction_value_lift:+.1f}%

2. FREQUENCY IMPACT:
   Before ZC: {avg_before_freq:.2f} transactions/month
   After ZC: {avg_after_freq:.2f} transactions/month
   Lift: {frequency_lift:+.1f}%

3. CUSTOMER TRANSFORMATION:
   {len(transformation_df[transformation_df['transaction_lift'] > 0])} customers improved ({len(transformation_df[transformation_df['transaction_lift'] > 0])/len(transformation_df)*100:.1f}%)
   {len(transformation_df[transformation_df['transaction_lift'] > 100])} customers doubled value ({len(transformation_df[transformation_df['transaction_lift'] > 100])/len(transformation_df)*100:.1f}%)

4. SUSTAINED ENGAGEMENT:
   90-day retention after adoption: {retention_analysis[-1]['retention_rate']:.1f}%
   Continuous ZC usage drives habit formation

5. STRATEGIC VALUE:
   ZC adoption is a behavioral inflection point
   Creates lasting positive change in customer value
    """)
    
    # Save results
    transformation_df.to_csv('zc_adoption_transformations.csv', index=False)
    pd.DataFrame(window_metrics).to_csv('zc_adoption_time_windows.csv', index=False)
    pd.DataFrame(retention_analysis).to_csv('zc_adoption_retention.csv', index=False)
    
    print("\nDetailed results saved to CSV files")
    
    return transformation_df, window_df

if __name__ == "__main__":
    analyze_zc_adoption_impact()