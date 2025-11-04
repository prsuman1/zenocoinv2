#!/usr/bin/env python3
"""
ZenoCoin Rewards Analytics Dashboard - MONTHLY CUSTOMER LEVEL
All metrics calculated at customer-month level with documentation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="ZenoCoin Monthly Analytics",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Dark mode CSS
dark_css = """
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    .stSidebar {
        background-color: #1a1f2e;
    }
    
    div[data-testid="metric-container"] {
        background-color: #1a1f2e;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-card {
        background-color: #1a1f2e !important;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #333;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 15px;
        border-left: 4px solid #3498db;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #3d2817, #5d3a1a);
        padding: 15px;
        border-left: 4px solid #ff9800;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(255, 152, 0, 0.3);
    }
    
    .success-box {
        background: linear-gradient(135deg, #1b3d1b, #2a5a2a);
        padding: 15px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
    }
    
    .doc-box {
        background: linear-gradient(135deg, #2c1e3d, #3d2a5a);
        padding: 20px;
        border-left: 4px solid #9c27b0;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(156, 39, 176, 0.3);
    }
    
    code {
        background-color: #2d3748;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
    }
</style>
"""

light_css = """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .insight-box {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        padding: 15px;
        border-left: 4px solid #0066cc;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 8px rgba(0, 102, 204, 0.2);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff8e1, #ffecb3);
        padding: 15px;
        border-left: 4px solid #ff9800;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.2);
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
        padding: 15px;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
        border-radius: 5px;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
    }
    
    .doc-box {
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        padding: 20px;
        border-left: 4px solid #9c27b0;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(156, 39, 176, 0.2);
    }
    
    code {
        background-color: #f5f5f5;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        color: #d73502;
    }
    
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
"""

# Apply theme
if st.session_state.dark_mode:
    st.markdown(dark_css, unsafe_allow_html=True)
else:
    st.markdown(light_css, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_monthly_data():
    # Load monthly customer data
    monthly_customer = pd.read_csv('monthly_customer_data.csv')
    monthly_customer['month'] = pd.to_datetime(monthly_customer['month'])
    
    # Load customer lifetime data
    customer_lifetime = pd.read_csv('customer_lifetime_monthly.csv')
    
    # Load summary metrics
    summary = pd.read_csv('summary_monthly_metrics.csv').iloc[0]
    
    # Load monthly trends
    monthly_trends = pd.read_csv('monthly_trends.csv')
    monthly_trends['month'] = pd.to_datetime(monthly_trends['month'])
    
    return monthly_customer, customer_lifetime, summary, monthly_trends

@st.cache_data
def load_transaction_data():
    df = pd.read_csv('data dump for suman part 2.csv')
    df['bill_date'] = pd.to_datetime(df['bill_date'])
    df['month'] = df['bill_date'].dt.to_period('M').astype(str)
    
    # Identify ZenoCoin usage
    df['used_zenocoin'] = ((df['zrd_promo_discount'] > 0) | 
                           (df['freebee_cost'] > 0) | 
                           (df['promo-code'].str.startswith('ZRD', na=False))).astype(int)
    
    return df[df['bill-flag'] == 'gross']  # Only gross transactions

# Get plotly theme based on mode
def get_plotly_theme():
    if st.session_state.dark_mode:
        return {
            'template': 'plotly_dark',
            'paper_bgcolor': '#1a1f2e',
            'plot_bgcolor': '#1a1f2e',
            'font_color': '#fafafa',
            'gridcolor': '#333'
        }
    else:
        return {
            'template': 'plotly_white',
            'paper_bgcolor': 'white',
            'plot_bgcolor': 'white',
            'font_color': '#333',
            'gridcolor': '#e0e0e0'
        }

# Main app
def main():
    # Header with theme toggle
    col_title, col_toggle = st.columns([10, 1])
    
    with col_title:
        st.title("🪙 ZenoCoin Monthly Analytics Dashboard")
        st.markdown("**Monthly Customer-Level Analysis & Strategic Insights**")
    
    with col_toggle:
        # Theme toggle button
        if st.button("🌙" if not st.session_state.dark_mode else "☀️", 
                    help="Toggle Dark/Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("---")
    
    # Load data
    monthly_customer, customer_lifetime, summary, monthly_trends = load_monthly_data()
    gross_df = load_transaction_data()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", 
        ["📊 Executive Summary", 
         "📚 KPI Documentation",
         "💰 Monthly Spend Analysis",
         "👥 Customer Segmentation",
         "📈 Retention & Frequency",
         "🆕 New User Cohorts",
         "🔄 ZC Adoption Impact",
         "💵 ROI Calculator",
         "📉 Trends & Patterns"])
    
    if page == "📊 Executive Summary":
        show_executive_summary(summary, monthly_trends)
    elif page == "📚 KPI Documentation":
        show_documentation()
    elif page == "💰 Monthly Spend Analysis":
        show_monthly_spend_analysis(monthly_customer, customer_lifetime, summary)
    elif page == "👥 Customer Segmentation":
        show_customer_segmentation(monthly_customer, customer_lifetime)
    elif page == "📈 Retention & Frequency":
        show_retention_frequency(monthly_customer, customer_lifetime, summary)
    elif page == "🆕 New User Cohorts":
        show_new_user_cohorts(gross_df)
    elif page == "🔄 ZC Adoption Impact":
        show_zc_adoption_impact(gross_df)
    elif page == "💵 ROI Calculator":
        show_roi_calculator(summary, monthly_trends)
    elif page == "📉 Trends & Patterns":
        show_trends_patterns(monthly_customer, monthly_trends)

def show_executive_summary(summary, monthly_trends):
    st.header("📊 Executive Summary - Monthly Customer Metrics")
    
    theme = get_plotly_theme()
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", f"{summary['total_customers']:,.0f}")
        st.metric("ZenoCoin Users", f"{summary['zc_customers']:,.0f}", 
                 f"{summary['zc_customers']/summary['total_customers']*100:.1f}%")
    
    with col2:
        st.metric("Monthly Redemption", f"{summary['monthly_redemption_rate']:.1f}%", 
                 "Post-July (Customer-Months)")
        st.metric("Monthly Spend Lift", f"₹{summary['monthly_spend_lift']:.0f}", 
                 f"+{summary['monthly_spend_lift_pct']:.1f}%")
    
    with col3:
        st.metric("Avg Monthly Spend (ZC)", f"₹{summary['avg_monthly_spend_zc']:.0f}")
        st.metric("Avg Monthly Spend (Non-ZC)", f"₹{summary['avg_monthly_spend_non_zc']:.0f}")
    
    with col4:
        st.metric("LTV ROI", f"{summary['ltv_roi']:.0f}%",
                 "Based on Customer Lifetime")
        st.metric("Monthly ROI", f"{summary['monthly_roi']:.0f}%",
                 "Based on Monthly Spend")
    
    # Key Insights
    st.markdown("### 🔍 Key Monthly Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='insight-box'>
        <b>💰 Monthly Spend Impact</b><br>
        ZenoCoin customer-months show:
        <ul>
        <li><b>+74.2%</b> higher monthly spend (₹1,088 vs ₹624)</li>
        <li><b>+81.4%</b> more transactions per month (7.3 vs 4.0)</li>
        <li><b>2.2x</b> more active months (4.8 vs 2.2)</li>
        <li><b>57.8%</b> come back next month after first use</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='warning-box'>
        <b>⚠️ Massive Opportunity</b><br>
        <b>Only 21%</b> monthly redemption rate post-July<br>
        <b>40,545</b> eligible customer-months didn't redeem<br><br>
        <b>If redemption increases to 40%:</b>
        <ul>
        <li>+7,600 additional customer-months</li>
        <li>₹3.5M incremental monthly spend</li>
        <li>₹24M incremental lifetime value</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Monthly trends chart
    st.markdown("### 📈 Monthly Performance Trends")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Monthly Active Users", "Average Monthly Spend", 
                       "Redemption Rate %", "Total Monthly Discounts")
    )
    
    # MAU
    fig.add_trace(
        go.Scatter(x=monthly_trends['month'], y=monthly_trends['mau'],
                  mode='lines+markers', name='MAU',
                  line=dict(color='#3498db', width=3)),
        row=1, col=1
    )
    
    # Avg Monthly Spend
    fig.add_trace(
        go.Bar(x=monthly_trends['month'], y=monthly_trends['avg_monthly_spend'],
               name='Avg Spend', marker_color='#2ecc71'),
        row=1, col=2
    )
    
    # Redemption Rate
    fig.add_trace(
        go.Scatter(x=monthly_trends['month'], y=monthly_trends['redemption_rate'],
                  mode='lines+markers', name='Redemption %',
                  line=dict(color='#e74c3c', width=3)),
        row=2, col=1
    )
    
    # Total Discounts
    fig.add_trace(
        go.Bar(x=monthly_trends['month'], y=monthly_trends['total_discounts'],
               name='Discounts', marker_color='#f39c12'),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600, 
        showlegend=False,
        template=theme['template'],
        paper_bgcolor=theme['paper_bgcolor'],
        plot_bgcolor=theme['plot_bgcolor'],
        font={'color': theme['font_color']}
    )
    fig.update_xaxes(gridcolor=theme['gridcolor'])
    fig.update_yaxes(gridcolor=theme['gridcolor'])
    
    st.plotly_chart(fig, use_container_width=True)

def show_documentation():
    st.header("📚 KPI Documentation & Calculation Methods")
    
    st.markdown("""
    <div class='doc-box'>
    <h3>🎯 Monthly Customer-Level Analysis</h3>
    All metrics in this dashboard are calculated at the <b>customer-month</b> level, not transaction level.
    This provides more accurate insights into customer behavior and value.
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different KPI categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Core Metrics", "Spend Analysis", "Retention Metrics", "ROI Calculations", "📈 Impact Calculator Logic"])
    
    with tab1:
        st.markdown("### Core Customer Metrics")
        
        st.markdown("""
        <div class='doc-box'>
        <b>1. Total Customers</b><br>
        <code>unique(patient_id) where bill-flag = 'gross'</code><br><br>
        Count of unique customers who made at least one purchase.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='doc-box'>
        <b>2. ZenoCoin Users (Monthly)</b><br>
        <code>customers who used ZenoCoin at least once in a month</code><br><br>
        A customer is counted as a ZenoCoin user for a month if they used it at least once that month.<br>
        Detection: <code>zrd_promo_discount > 0 OR freebee_cost > 0 OR promo_code starts with 'ZRD'</code>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='doc-box'>
        <b>3. Monthly Redemption Rate</b><br>
        <code>(ZC customer-months / Eligible customer-months) × 100</code><br><br>
        For July 2025 onwards (post-launch):<br>
        • Eligible customer-months: Customer active in month with eligibility_flag = 1<br>
        • ZC customer-months: Eligible customers who used ZenoCoin at least once
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Monthly Spend Metrics")
        
        st.markdown("""
        <div class='doc-box'>
        <b>1. Average Monthly Spend</b><br>
        <code>sum(revenue-value) / customer-months</code><br><br>
        Total spend by customer in a month, aggregated across all their transactions.<br>
        • ZC Months: ₹1,088 average<br>
        • Non-ZC Months: ₹624 average<br>
        • Lift: +74.2%
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='doc-box'>
        <b>2. Monthly Transaction Frequency</b><br>
        <code>count(transactions) per customer per month</code><br><br>
        Average number of transactions per customer per month:<br>
        • ZC customer-months: 7.3 transactions<br>
        • Non-ZC customer-months: 4.0 transactions<br>
        • Lift: +81.4%
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='doc-box'>
        <b>3. Customer Lifetime Metrics</b><br>
        <code>Aggregated across all months for each customer</code><br><br>
        • Active Months: Number of months with at least one transaction<br>
        • Total Spend: Sum of all monthly spends<br>
        • Avg Monthly Spend: Total spend / Active months
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Retention & Engagement Metrics")
        
        st.markdown("""
        <div class='doc-box'>
        <b>1. Monthly Retention Rate</b><br>
        <code>customers who return in month M+1 after first ZC use in month M</code><br><br>
        For each customer who used ZenoCoin:<br>
        1. Identify first month of ZenoCoin usage<br>
        2. Check if they had any transaction in the next month<br>
        3. Retention = (Returned customers / Total first-time ZC users) × 100<br>
        Current: <b>57.8%</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='doc-box'>
        <b>2. Active Months Comparison</b><br>
        <code>count(distinct months) per customer</code><br><br>
        • ZenoCoin users: 4.8 active months on average<br>
        • Non-users: 2.2 active months on average<br>
        • Lift: +119.4%
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### ROI Calculations")
        
        st.markdown("""
        <div class='doc-box'>
        <b>1. Monthly-Based ROI</b><br>
        <code>((Incremental Monthly Spend × ZC Customer-Months) - Investment) / Investment × 100</code><br><br>
        • Incremental monthly spend: ₹464 (₹1,088 - ₹624)<br>
        • ZC customer-months: 11,140<br>
        • Total investment: ₹654,188<br>
        • ROI: <b>689.4%</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='doc-box'>
        <b>2. Lifetime Value ROI</b><br>
        <code>((Incremental LTV × ZC Customers) - Investment) / Investment × 100</code><br><br>
        • Incremental LTV: ₹3,165 (₹4,363 - ₹1,198)<br>
        • ZC customers: 9,307<br>
        • Total investment: ₹654,188<br>
        • ROI: <b>4,402.9%</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='success-box'>
        <b>💡 Key Insight</b><br>
        Every ₹1 invested in ZenoCoin returns:<br>
        • ₹7.89 in incremental monthly spend<br>
        • ₹45.03 in incremental lifetime value
        </div>
        """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### 📈 Advanced Impact Calculator - Detailed Logic Documentation")
        
        st.markdown("""
        <div class='doc-box' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;'>
        <h3>🎯 Understanding the Impact Calculator</h3>
        The Impact Calculator uses advanced analytics to project the financial impact of changing ZenoCoin usage rates.
        It answers: <b>"What happens if we change from current 21% usage to X% usage?"</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 1: Current Baseline
        st.markdown("""
        <div class='doc-box'>
        <h4>📊 Step 1: Establishing the Current Baseline</h4>
        <b>Current State (From Actual Data):</b><br>
        • Current Usage Rate = <b>21%</b> of eligible customers use ZenoCoin<br>
        • Total Monthly Customers = 20,000 (example)<br>
        • Eligible Customers = 20,000 × 80% = 16,000<br>
        • Current ZC Users = 16,000 × 21% = <b>3,360 users</b><br><br>
        
        <code>Current_Users = Total_Customers × Eligibility_Rate × Current_Usage_Rate</code><br>
        <code>Current_Users = 20,000 × 0.8 × 0.21 = 3,360</code>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 2: Incremental Calculation
        st.markdown("""
        <div class='doc-box'>
        <h4>🔢 Step 2: Calculating Incremental Users</h4>
        <b>Example: If Target = 40% Usage</b><br>
        • Target Users = 16,000 × 40% = 6,400 users<br>
        • <span style='color: #4CAF50'>Incremental Users = 6,400 - 3,360 = +3,040 NEW users</span><br><br>
        
        <b>Example: If Target = 20% Usage (Decrease)</b><br>
        • Target Users = 16,000 × 20% = 3,200 users<br>
        • <span style='color: #f44336'>Incremental Users = 3,200 - 3,360 = -160 FEWER users</span><br><br>
        
        <code>Incremental_Users = Target_Users - Current_Users</code><br>
        ⚠️ <b>Can be positive (growth) or negative (decline)</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 3: Revenue Calculation
        st.markdown("""
        <div class='doc-box'>
        <h4>💰 Step 3: Incremental Revenue Calculation</h4>
        <b>Key Metrics from Analysis:</b><br>
        • ZC User Monthly Spend = ₹1,088<br>
        • Non-ZC User Monthly Spend = ₹624<br>
        • Spend Lift per User = ₹1,088 - ₹624 = <b>₹464</b><br><br>
        
        <b>Revenue Formula:</b><br>
        <code>Incremental_Revenue = Incremental_Users × Spend_Lift × Incrementality_Rate</code><br><br>
        
        <b>Example (40% target):</b><br>
        • Incremental Users = +3,040<br>
        • Spend Lift = ₹464<br>
        • Incrementality Rate = 75% (accounting for cannibalization)<br>
        • Monthly Revenue = 3,040 × ₹464 × 0.75 = <b>₹1,057,920</b><br><br>
        
        📌 <b>Incrementality Rate:</b> Not all revenue is new - some would have happened anyway
        </div>
        """, unsafe_allow_html=True)
        
        # Section 4: Cost Calculation
        st.markdown("""
        <div class='doc-box'>
        <h4>💸 Step 4: Cost Calculation</h4>
        <b>Cost Components:</b><br>
        • Average Discount per Redemption = ₹30<br>
        • Average Monthly Redemptions per User = 7.3 times<br>
        • Cost per User per Month = ₹30 × 7.3 = ₹219<br><br>
        
        <b>Total Cost Formula:</b><br>
        <code>Monthly_Cost = Target_Users × Discount × Frequency</code><br><br>
        
        <b>Incremental Cost (for new users only):</b><br>
        <code>Incremental_Cost = Incremental_Users × ₹219</code><br><br>
        
        <b>Example (40% target):</b><br>
        • Incremental Users = +3,040<br>
        • Cost per User = ₹219<br>
        • Incremental Monthly Cost = 3,040 × ₹219 = <b>₹665,760</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 5: Net Impact
        st.markdown("""
        <div class='doc-box'>
        <h4>📊 Step 5: Net Monthly Impact</h4>
        <b>Formula:</b><br>
        <code>Net_Impact = Incremental_Revenue - Incremental_Cost</code><br><br>
        
        <b>Example (40% target):</b><br>
        • Incremental Revenue = ₹1,057,920<br>
        • Incremental Cost = ₹665,760<br>
        • <span style='color: #4CAF50'><b>Net Monthly Impact = ₹392,160</b></span><br><br>
        
        <b>Annual Impact:</b><br>
        <code>Annual_Impact = Net_Monthly_Impact × 12</code><br>
        • Annual Impact = ₹392,160 × 12 = <b>₹4,705,920</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Advanced Features Section
        st.markdown("""
        <div class='doc-box'>
        <h4>🚀 Advanced Features in Calculator</h4>
        
        <b>1. S-Curve Adoption Model:</b><br>
        • Real adoption follows an S-curve, not linear<br>
        • Formula: <code>Adoption = Saturation / (1 + e^(-speed × scaled_target))</code><br>
        • Accounts for slower initial adoption and saturation limits<br><br>
        
        <b>2. Network Effects (15% boost):</b><br>
        • Users attract other users<br>
        • Higher usage → more visibility → more adoption<br>
        • <code>Network_Boost = 1 + (0.15 × usage_rate)</code><br><br>
        
        <b>3. Cannibalization Factor:</b><br>
        • Not all lift is incremental<br>
        • Higher usage → more cannibalization<br>
        • Base incrementality = 75%<br>
        • Reduces with higher usage rates<br><br>
        
        <b>4. Risk Adjustment:</b><br>
        • Execution risk increases with ambitious targets<br>
        • Market risk = 10% (constant)<br>
        • Total risk calculated and applied to projections<br><br>
        
        <b>5. Confidence Intervals:</b><br>
        • 95% statistical confidence bounds<br>
        • Based on historical variance in data<br>
        • Shows best case and worst case scenarios
        </div>
        """, unsafe_allow_html=True)
        
        # ROI Calculation
        st.markdown("""
        <div class='success-box'>
        <h4>💎 ROI Calculation</h4>
        <b>Monthly ROI Formula:</b><br>
        <code>ROI = (Annual_Revenue - Annual_Cost) / Annual_Cost × 100</code><br><br>
        
        <b>Example (40% target):</b><br>
        • Annual Revenue = ₹12,695,040<br>
        • Annual Cost = ₹7,989,120<br>
        • Net Profit = ₹4,705,920<br>
        • <b>ROI = 58.9%</b><br><br>
        
        <b>Payback Period:</b><br>
        <code>Payback = Initial_Investment / Monthly_Net_Impact</code><br>
        • Payback = ₹665,760 / ₹392,160 = <b>1.7 months</b>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Reference Table
        st.markdown("""
        <div class='doc-box'>
        <h4>📋 Quick Reference - Key Numbers</h4>
        <table style='width: 100%; border-collapse: collapse;'>
        <tr style='background: #3498db; color: white;'>
            <th style='padding: 10px; border: 1px solid #ddd;'>Metric</th>
            <th style='padding: 10px; border: 1px solid #ddd;'>Value</th>
            <th style='padding: 10px; border: 1px solid #ddd;'>Source</th>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Current Usage Rate</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>21%</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Actual data analysis</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Eligibility Rate</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>80%</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Historical average</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>ZC User Monthly Spend</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>₹1,088</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Customer-month analysis</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Non-ZC User Monthly Spend</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>₹624</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Customer-month analysis</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Spend Lift</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>₹464</b> (+74.2%)</td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Calculated difference</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Avg Discount/Redemption</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>₹30</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Program parameter</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Monthly Frequency</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>7.3</b> transactions</td>
            <td style='padding: 8px; border: 1px solid #ddd;'>ZC user average</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Incrementality Rate</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>75%</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Statistical model</td>
        </tr>
        <tr>
            <td style='padding: 8px; border: 1px solid #ddd;'>Network Effect</td>
            <td style='padding: 8px; border: 1px solid #ddd;'><b>15%</b></td>
            <td style='padding: 8px; border: 1px solid #ddd;'>Adoption analysis</td>
        </tr>
        </table>
        </div>
        """, unsafe_allow_html=True)

def show_monthly_spend_analysis(monthly_customer, customer_lifetime, summary):
    st.header("💰 Monthly Spend Analysis")
    
    theme = get_plotly_theme()
    
    # Monthly spend distribution
    st.markdown("### Monthly Spend Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution of monthly spend for ZC vs non-ZC
        zc_months = monthly_customer[monthly_customer['used_zc_in_month'] == 1]['monthly_spend']
        non_zc_months = monthly_customer[monthly_customer['used_zc_in_month'] == 0]['monthly_spend']
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=non_zc_months, name='Non-ZC Months', 
                                   opacity=0.7, marker_color='#e74c3c',
                                   nbinsx=50))
        fig.add_trace(go.Histogram(x=zc_months, name='ZC Months', 
                                   opacity=0.7, marker_color='#2ecc71',
                                   nbinsx=50))
        
        fig.update_layout(
            title="Monthly Spend Distribution",
            barmode='overlay',
            xaxis_title="Monthly Spend (₹)",
            yaxis_title="Number of Customer-Months",
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font={'color': theme['font_color']}
        )
        fig.update_xaxes(gridcolor=theme['gridcolor'], range=[0, 5000])
        fig.update_yaxes(gridcolor=theme['gridcolor'])
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average spend by customer segment
        segments = pd.DataFrame({
            'Segment': ['ZC Customers', 'Non-ZC Customers'],
            'Avg Monthly Spend': [summary['avg_monthly_spend_zc'], summary['avg_monthly_spend_non_zc']],
            'Count': [summary['zc_customers'], summary['total_customers'] - summary['zc_customers']]
        })
        
        fig = px.bar(segments, x='Segment', y='Avg Monthly Spend',
                    title="Average Monthly Spend by Segment",
                    color='Avg Monthly Spend',
                    color_continuous_scale='Viridis',
                    text='Avg Monthly Spend')
        
        fig.update_traces(texttemplate='₹%{text:.0f}', textposition='outside')
        fig.update_layout(
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font={'color': theme['font_color']},
            showlegend=False
        )
        fig.update_xaxes(gridcolor=theme['gridcolor'])
        fig.update_yaxes(gridcolor=theme['gridcolor'])
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Key metrics
    st.markdown("### 📊 Monthly Spend Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='success-box'>
        <b>💰 Monthly Spend Lift</b><br>
        ZenoCoin months show<br>
        <b>+₹{summary['monthly_spend_lift']:.0f}</b> higher spend<br>
        ({summary['monthly_spend_lift_pct']:.1f}% increase)
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_trans_zc = 7.3  # From analysis
        avg_trans_non_zc = 4.0
        st.markdown(f"""
        <div class='success-box'>
        <b>📦 Transaction Frequency</b><br>
        ZC months average<br>
        <b>{avg_trans_zc:.1f}</b> transactions<br>
        vs {avg_trans_non_zc:.1f} for non-ZC
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='success-box'>
        <b>📅 Active Months</b><br>
        ZC customers active for<br>
        <b>{summary['avg_active_months_zc']:.1f}</b> months<br>
        vs {summary['avg_active_months_non_zc']:.1f} for non-ZC
        </div>
        """, unsafe_allow_html=True)

def show_customer_segmentation(monthly_customer, customer_lifetime):
    st.header("👥 Customer Segmentation")
    
    theme = get_plotly_theme()
    
    # Create customer segments based on lifetime value
    customer_lifetime = customer_lifetime.copy()
    customer_lifetime['value_segment'] = pd.qcut(customer_lifetime['total_spend'], 
                                                  q=4, labels=['Low', 'Medium', 'High', 'Premium'])
    
    # Create ZC user label
    customer_lifetime['zc_user_label'] = customer_lifetime['is_zc_user'].apply(lambda x: 'ZC User' if x == 1 else 'Non-ZC')
    
    # Create segment analysis with simple aggregation
    segment_groups = []
    for segment in ['Low', 'Medium', 'High', 'Premium']:
        for user_type in ['ZC User', 'Non-ZC']:
            mask = (customer_lifetime['value_segment'] == segment) & (customer_lifetime['zc_user_label'] == user_type)
            subset = customer_lifetime[mask]
            if len(subset) > 0:
                segment_groups.append({
                    'value_segment': segment,
                    'zc_user_label': user_type,
                    'customer_count': len(subset),
                    'avg_monthly_spend': subset['avg_monthly_spend'].mean(),
                    'active_months': subset['active_months'].mean(),
                    'total_spend': subset['total_spend'].mean()
                })
    
    segment_analysis = pd.DataFrame(segment_groups)
    
    # Create a simple bar chart instead of sunburst to avoid the error
    fig = go.Figure()
    
    for user_type in ['Non-ZC', 'ZC User']:
        data = segment_analysis[segment_analysis['zc_user_label'] == user_type]
        fig.add_trace(go.Bar(
            name=user_type,
            x=data['value_segment'],
            y=data['customer_count'],
            text=data['customer_count'],
            textposition='auto',
        ))
    
    fig.update_layout(
        title="Customer Distribution by Value Segment and ZenoCoin Usage",
        xaxis_title="Value Segment",
        yaxis_title="Number of Customers",
        barmode='group',
        height=500,
        template=theme['template'],
        paper_bgcolor=theme['paper_bgcolor'],
        font={'color': theme['font_color']}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment metrics table
    st.markdown("### Segment Performance Metrics")
    
    pivot_table = segment_analysis.pivot_table(
        values=['customer_count', 'avg_monthly_spend', 'active_months'],
        index='value_segment',
        columns='zc_user_label',
        aggfunc='sum'
    ).round(0)
    
    st.dataframe(pivot_table, use_container_width=True)

def show_retention_frequency(monthly_customer, customer_lifetime, summary):
    st.header("📈 Retention & Frequency Analysis")
    
    theme = get_plotly_theme()
    
    # Load retention comparison data if available
    try:
        retention_data = pd.read_csv('retention_comparison.csv')
        retention_dict = dict(zip(retention_data['metric'], retention_data['value']))
    except:
        retention_dict = {}
    
    # Show 7-day and 30-day retention comparison
    if retention_dict:
        st.markdown("### 📊 Short-Term Retention Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='insight-box'>
            <b>7-Day Retention</b><br>
            ZC Users: <b>{retention_dict.get('7_day_retention_zc', 0):.1f}%</b><br>
            Non-ZC: {retention_dict.get('7_day_retention_non_zc', 0):.1f}%<br>
            <span style='color: #4CAF50'>+{retention_dict.get('7_day_lift', 0):.1f}% lift</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='insight-box'>
            <b>30-Day Retention</b><br>
            ZC Users: <b>{retention_dict.get('30_day_retention_zc', 0):.1f}%</b><br>
            Non-ZC: {retention_dict.get('30_day_retention_non_zc', 0):.1f}%<br>
            <span style='color: #4CAF50'>+{retention_dict.get('30_day_lift', 0):.1f}% lift</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Create retention comparison chart
        retention_comparison = pd.DataFrame({
            'Period': ['7-Day', '7-Day', '30-Day', '30-Day'],
            'User Type': ['ZC Users', 'Non-ZC', 'ZC Users', 'Non-ZC'],
            'Retention Rate': [
                retention_dict.get('7_day_retention_zc', 0),
                retention_dict.get('7_day_retention_non_zc', 0),
                retention_dict.get('30_day_retention_zc', 0),
                retention_dict.get('30_day_retention_non_zc', 0)
            ]
        })
        
        fig = px.bar(retention_comparison, x='Period', y='Retention Rate', 
                    color='User Type', barmode='group',
                    title="Retention Rate Comparison: ZenoCoin Users vs Non-Users",
                    color_discrete_map={'ZC Users': '#4CAF50', 'Non-ZC': '#9E9E9E'})
        
        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
        fig.update_layout(
            yaxis_title="Retention Rate (%)",
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font={'color': theme['font_color']},
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
    
    # Active months comparison
    st.markdown("### 📈 Customer Lifetime Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Active months comparison
        data = pd.DataFrame({
            'Customer Type': ['ZenoCoin Users', 'Non-ZC Users'],
            'Average Active Months': [summary['avg_active_months_zc'], 
                                     summary['avg_active_months_non_zc']]
        })
        
        fig = px.bar(data, x='Customer Type', y='Average Active Months',
                    title="Customer Lifetime (Active Months)",
                    color='Average Active Months',
                    color_continuous_scale='Blues',
                    text='Average Active Months')
        
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            plot_bgcolor=theme['plot_bgcolor'],
            font={'color': theme['font_color']},
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div class='insight-box' style='margin-top: 50px'>
        <b>Key Insights</b><br><br>
        ✅ ZC users show <b>+{retention_dict.get('7_day_lift', 8.9):.1f}%</b> better 7-day retention<br><br>
        ✅ ZC users show <b>+{retention_dict.get('30_day_lift', 11.6):.1f}%</b> better 30-day retention<br><br>
        ✅ ZC users active for <b>{summary['avg_active_months_zc']:.1f}</b> months vs {summary['avg_active_months_non_zc']:.1f}<br><br>
        📊 Higher retention = Higher LTV
        </div>
        """, unsafe_allow_html=True)

def show_roi_calculator(summary, monthly_trends):
    st.header("💵 Advanced Impact Calculator & Projections")
    
    theme = get_plotly_theme()
    
    # Import the advanced calculator
    try:
        from advanced_impact_calculator import AdvancedImpactCalculator
        calculator = AdvancedImpactCalculator()
        use_advanced = True
    except:
        use_advanced = False
        calculator = None
    
    st.markdown("### 🎯 Impact Projection Model")
    st.markdown("*Using ML-based predictions and statistical modeling for accurate projections*")
    
    # Single input for target usage percentage
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col2:
        st.markdown("#### Primary Input Variable")
        target_usage = st.slider(
            "Target % Who Use Coins", 
            min_value=10, 
            max_value=60, 
            value=40, 
            step=5,
            help="Percentage of eligible customers targeted to use ZenoCoin"
        )
        
        total_customers = st.number_input(
            "Total Monthly Customers",
            min_value=10000,
            max_value=50000,
            value=20000,
            step=1000,
            help="Expected total monthly customer base"
        )
    
    if use_advanced and calculator:
        # Calculate impact using advanced model
        results = calculator.calculate_impact(target_usage, total_customers)
        
        # Display KPI Definitions first
        with st.expander("📚 KPI Definitions & Methodology", expanded=False):
            definitions = calculator.get_kpi_definitions()
            
            for kpi, details in definitions.items():
                st.markdown(f"**{kpi}**")
                st.markdown(f"- *Definition:* {details['definition']}")
                st.markdown(f"- *Formula:* `{details['formula']}`")
                st.markdown(f"- *Importance:* {details['importance']}")
                st.markdown("")
        
        st.markdown("---")
        
        # Display calculated metrics
        st.markdown("### 📊 Projected Impact Metrics")
        
        # Row 1: User and Revenue Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "1. New Coin Users",
                f"{results['new_coin_users']:,}",
                help="Projected monthly ZenoCoin users"
            )
        
        with col2:
            st.metric(
                "2. Avg Monthly Amount/User",
                f"₹{results['avg_monthly_amount_per_user']:,.0f}",
                help="Expected spend per ZC user"
            )
        
        with col3:
            st.metric(
                "3. Incremental Revenue",
                f"₹{results['incremental_revenue_monthly']:,.0f}",
                help="Additional monthly revenue"
            )
        
        with col4:
            st.metric(
                "4. Net Monthly Impact",
                f"₹{results['net_monthly_impact']:,.0f}",
                delta=f"ROI: {results['roi_percentage']:.0f}%",
                help="Monthly profit after costs"
            )
        
        # Row 2: Annual and Advanced Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "5. Annual Impact",
                f"₹{results['annual_impact']:,.0f}",
                help="12-month cumulative impact"
            )
        
        with col2:
            st.metric(
                "Risk-Adjusted Annual",
                f"₹{results['risk_adjusted_annual_impact']:,.0f}",
                delta=f"Risk: {results['risk_score']:.1f}%",
                help="Conservative estimate"
            )
        
        with col3:
            st.metric(
                "Customer LTV Increase",
                f"₹{results['customer_ltv_increase']:,.0f}",
                help="Lifetime value increase per user"
            )
        
        with col4:
            st.metric(
                "Payback Period",
                f"{results['payback_period_months']:.1f} months",
                help="Time to recover investment"
            )
        
        # Confidence Intervals
        st.markdown("---")
        st.markdown("### 📈 Statistical Confidence Intervals")
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            st.info(f"""
            **95% Confidence Interval for Monthly Revenue:**
            
            Lower Bound: ₹{results['revenue_confidence_lower']:,.0f}
            
            **Expected: ₹{results['incremental_revenue_monthly']:,.0f}**
            
            Upper Bound: ₹{results['revenue_confidence_upper']:,.0f}
            """)
        
        # Visualization of projections
        st.markdown("---")
        st.markdown("### 📊 Visual Projections")
        
        # Create adoption curve visualization
        months = list(range(1, 13))
        adoption_rates = []
        monthly_impacts = []
        
        for month in months:
            month_rate = calculator._monthly_growth_curve(month - 1, target_usage / 100)
            adoption_rates.append(month_rate * 100)
            
            month_users = total_customers * 0.8 * month_rate
            month_revenue = month_users * (results['avg_monthly_amount_per_user'] - 624)
            monthly_impacts.append(month_revenue)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Adoption Curve Over Time", "Monthly Revenue Impact")
        )
        
        fig.add_trace(
            go.Scatter(
                x=months, 
                y=adoption_rates,
                mode='lines+markers',
                name='Adoption %',
                line=dict(color='#4CAF50', width=3)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=months,
                y=monthly_impacts,
                name='Revenue Impact',
                marker_color='#2196F3'
            ),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text="Month", row=1, col=1)
        fig.update_xaxes(title_text="Month", row=1, col=2)
        fig.update_yaxes(title_text="Adoption Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Revenue (₹)", row=1, col=2)
        
        fig.update_layout(
            height=400,
            showlegend=False,
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            font={'color': theme['font_color']}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # Fallback to simple calculation if advanced calculator fails
        st.warning("Advanced calculator not available. Using simplified projections.")
        
        # Current baseline (21% usage)
        current_usage_rate = 21.0  # Current actual usage %
        eligible = total_customers * 0.8
        
        # Calculate CURRENT state
        current_users = eligible * (current_usage_rate / 100)
        
        # Calculate TARGET state
        target_users = eligible * (target_usage / 100)
        
        # INCREMENTAL users (can be negative if target < current)
        incremental_users = target_users - current_users
        
        # Metrics
        avg_amount = 1088  # From analysis for ZC users
        avg_amount_non_zc = 624  # For non-ZC users
        spend_lift = avg_amount - avg_amount_non_zc  # 464
        
        # Revenue calculation (only on incremental users)
        incremental_revenue = incremental_users * spend_lift
        
        # Cost calculation (for all target users, not just incremental)
        cost_per_user = 30 * 7  # Discount * frequency
        total_cost = target_users * cost_per_user
        incremental_cost = incremental_users * cost_per_user if incremental_users > 0 else 0
        
        # Net impact
        net_impact = incremental_revenue - incremental_cost
        annual = net_impact * 12
        
        # Display with context
        st.markdown(f"**Current State:** {current_usage_rate:.0f}% usage ({current_users:,.0f} users)")
        st.markdown(f"**Target State:** {target_usage:.0f}% usage ({target_users:,.0f} users)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Show incremental change with delta
            st.metric(
                "Incremental Coin Users", 
                f"{incremental_users:+,.0f}",
                delta=f"{incremental_users/current_users*100:+.1f}%" if current_users > 0 else "N/A",
                delta_color="normal" if incremental_users > 0 else "inverse"
            )
            st.metric("Avg Monthly Amount", f"₹{avg_amount:,.0f}")
        
        with col2:
            st.metric(
                "Incremental Revenue", 
                f"₹{incremental_revenue:+,.0f}",
                help="Additional revenue from change in users"
            )
            st.metric("Net Monthly Impact", f"₹{net_impact:+,.0f}")
        
        with col3:
            st.metric("Annual Impact", f"₹{annual:+,.0f}")
            if total_cost > 0:
                roi = (abs(annual) / (total_cost * 12)) * 100
                st.metric("ROI %", f"{roi:.0f}%")
            else:
                st.metric("ROI %", "N/A")

def show_trends_patterns(monthly_customer, monthly_trends):
    st.header("📉 Trends & Patterns")
    
    theme = get_plotly_theme()
    
    # Monthly trends visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("ZenoCoin Users Over Time", "Average Monthly Spend Trend",
                       "Redemption Rate Evolution", "Investment vs Returns")
    )
    
    # ZC Users
    fig.add_trace(
        go.Bar(x=monthly_trends['month'], y=monthly_trends['zc_users'],
               marker_color='#3498db', name='ZC Users'),
        row=1, col=1
    )
    
    # Avg Spend
    fig.add_trace(
        go.Scatter(x=monthly_trends['month'], y=monthly_trends['avg_monthly_spend'],
                  mode='lines+markers', line=dict(color='#2ecc71', width=3),
                  name='Avg Spend'),
        row=1, col=2
    )
    
    # Redemption Rate
    fig.add_trace(
        go.Scatter(x=monthly_trends['month'], y=monthly_trends['redemption_rate'],
                  mode='lines+markers', line=dict(color='#e74c3c', width=3),
                  name='Redemption %'),
        row=2, col=1
    )
    
    # Investment vs Returns (estimated)
    monthly_trends['estimated_returns'] = monthly_trends['zc_users'] * 464  # Using avg lift
    fig.add_trace(
        go.Bar(x=monthly_trends['month'], y=monthly_trends['total_discounts'],
               marker_color='#e74c3c', name='Investment', opacity=0.7),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(x=monthly_trends['month'], y=monthly_trends['estimated_returns'],
               marker_color='#2ecc71', name='Returns', opacity=0.7),
        row=2, col=2
    )
    
    fig.update_layout(
        height=700,
        showlegend=False,
        template=theme['template'],
        paper_bgcolor=theme['paper_bgcolor'],
        plot_bgcolor=theme['plot_bgcolor'],
        font={'color': theme['font_color']}
    )
    fig.update_xaxes(gridcolor=theme['gridcolor'])
    fig.update_yaxes(gridcolor=theme['gridcolor'])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### 🎯 Key Patterns Identified")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='success-box'>
        <b>📈 Growth Pattern</b><br>
        Redemption peaked at<br>
        <b>25.4%</b> in July<br>
        then declined to 13.9%
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='warning-box'>
        <b>⚠️ Awareness Gap</b><br>
        <b>79%</b> of eligible<br>
        customer-months<br>
        don't use ZenoCoin
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='insight-box'>
        <b>💡 Opportunity</b><br>
        Increasing redemption<br>
        to 40% would add<br>
        <b>₹24M</b> in LTV
        </div>
        """, unsafe_allow_html=True)

def show_new_user_cohorts(df):
    """Show beautiful new user cohort analysis"""
    st.header("🆕 New User Cohort Analysis")
    st.markdown("*Comparing customer behavior based on acquisition method: ZenoCoin vs Non-ZenoCoin*")
    
    theme = get_plotly_theme()
    
    # Process cohort data
    with st.spinner("Analyzing new user cohorts..."):
        # Convert dates
        df['bill_date'] = pd.to_datetime(df['bill_date'])
        df['first_bill_date'] = pd.to_datetime(df['first-bill-date'])
        
        # Identify new users and ZC usage
        df['is_new_user'] = (df['bill_date'].dt.date == df['first_bill_date'].dt.date)
        df['used_zenocoin'] = ((df['eligibility_flag'] == 1) & 
                              ((df.get('zrd_promo_discount', 0) > 0) | 
                               (df.get('other_promo_discount', 0) > 0))).astype(int)
        
        # Get first transaction cohorts
        first_transactions = df[df['is_new_user']].copy()
        customer_acquisition = first_transactions.groupby('patient-id').agg({
            'used_zenocoin': 'max',
            'bill_date': 'first',
            'revenue-value': 'sum'
        }).reset_index()
        
        zc_acquired = customer_acquisition[customer_acquisition['used_zenocoin'] == 1]['patient-id'].unique()
        nonzc_acquired = customer_acquisition[customer_acquisition['used_zenocoin'] == 0]['patient-id'].unique()
        
        # Order progression
        df_sorted = df.sort_values(['patient-id', 'bill_date'])
        df_sorted['order_number'] = df_sorted.groupby('patient-id').cumcount() + 1
        df_sorted['cohort'] = 'Other'
        df_sorted.loc[df_sorted['patient-id'].isin(zc_acquired), 'cohort'] = 'ZC_Acquired'
        df_sorted.loc[df_sorted['patient-id'].isin(nonzc_acquired), 'cohort'] = 'NonZC_Acquired'
    
    # Key Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
        <h3 style='color: white; margin: 0;'>{len(zc_acquired)}</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 0;'>ZC-Acquired Users</p>
        <small style='color: rgba(255,255,255,0.7);'>0.5% of new users</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
        <h3 style='color: white; margin: 0;'>{len(nonzc_acquired):,}</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 0;'>NonZC-Acquired</p>
        <small style='color: rgba(255,255,255,0.7);'>99.5% of new users</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ltv_diff = 59.5  # From analysis
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
        <h3 style='color: white; margin: 0;'>+{ltv_diff:.1f}%</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 0;'>Higher LTV</p>
        <small style='color: rgba(255,255,255,0.7);'>ZC vs NonZC</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        retention_diff = 29.8  # From analysis
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);'>
        <h3 style='color: white; margin: 0;'>+{retention_diff:.1f}pp</h3>
        <p style='color: rgba(255,255,255,0.9); margin: 0;'>Better Retention</p>
        <small style='color: rgba(255,255,255,0.7);'>2nd order rate</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Tab layout for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Order Progression", "💰 Spend Analysis", "🔄 Retention Funnel", "💎 Lifetime Value"])
    
    with tab1:
        st.markdown("### Order Progression Analysis")
        
        # Calculate order metrics
        order_metrics = []
        for cohort in ['ZC_Acquired', 'NonZC_Acquired']:
            cohort_data = df_sorted[df_sorted['cohort'] == cohort]
            for order_num in range(1, 6):
                order_data = cohort_data[cohort_data['order_number'] == order_num]
                if len(order_data) > 0:
                    order_metrics.append({
                        'Cohort': cohort.replace('_', ' '),
                        'Order': f"Order {order_num}",
                        'Order_Num': order_num,
                        'Customers': order_data['patient-id'].nunique(),
                        'Avg_Spend': order_data['revenue-value'].mean(),
                        'ZC_Usage': order_data['used_zenocoin'].mean() * 100
                    })
        
        order_df = pd.DataFrame(order_metrics)
        
        # Dual axis chart - customers and spend
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Customer Retention by Order", "Average Spend by Order")
        )
        
        for cohort in ['ZC Acquired', 'NonZC Acquired']:
            cohort_data = order_df[order_df['Cohort'] == cohort]
            color = '#667eea' if 'ZC' in cohort else '#f5576c'
            
            fig.add_trace(
                go.Scatter(
                    x=cohort_data['Order_Num'],
                    y=cohort_data['Customers'],
                    mode='lines+markers',
                    name=cohort,
                    line=dict(color=color, width=3),
                    marker=dict(size=10)
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=cohort_data['Order_Num'],
                    y=cohort_data['Avg_Spend'],
                    mode='lines+markers',
                    name=cohort,
                    line=dict(color=color, width=3),
                    marker=dict(size=10),
                    showlegend=False
                ),
                row=1, col=2
            )
        
        fig.update_xaxes(title_text="Order Number", row=1, col=1)
        fig.update_xaxes(title_text="Order Number", row=1, col=2)
        fig.update_yaxes(title_text="Number of Customers", row=1, col=1)
        fig.update_yaxes(title_text="Average Spend (₹)", row=1, col=2)
        
        fig.update_layout(
            height=400,
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            font={'color': theme['font_color']}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        col1, col2 = st.columns(2)
        with col1:
            st.info("""
            **📈 Key Pattern:**
            - ZC-acquired users show **88.6%** 2nd order rate
            - NonZC-acquired show only **58.8%** 2nd order rate
            - **+29.8pp** retention advantage for ZC cohort
            """)
        
        with col2:
            st.success("""
            **💡 Insight:**
            - First ZC experience creates lasting behavior
            - Higher order frequency (2.2 vs 9.9 days)
            - Maintains 65% ZC usage in later orders
            """)
    
    with tab2:
        st.markdown("### Spend Behavior Comparison")
        
        # Create spend distribution comparison
        cohort_spend = []
        for cohort, name in [(zc_acquired, 'ZC-Acquired'), (nonzc_acquired, 'NonZC-Acquired')]:
            cohort_trans = df_sorted[df_sorted['patient-id'].isin(cohort)]
            for _, row in cohort_trans.iterrows():
                cohort_spend.append({
                    'Cohort': name,
                    'Order': min(row['order_number'], 5),
                    'Spend': row['revenue-value']
                })
        
        spend_df = pd.DataFrame(cohort_spend)
        
        # Box plot comparison
        fig = px.box(
            spend_df,
            x='Order',
            y='Spend',
            color='Cohort',
            title="Spend Distribution by Order Number",
            color_discrete_map={'ZC-Acquired': '#667eea', 'NonZC-Acquired': '#f5576c'}
        )
        
        fig.update_layout(
            height=400,
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            font={'color': theme['font_color']},
            yaxis_title="Transaction Value (₹)",
            xaxis_title="Order Number"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Spend metrics comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class='success-box'>
            <b>1st Order</b><br>
            ZC: ₹175<br>
            NonZC: ₹128<br>
            <span style='color: #4CAF50'>+36.9% higher</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='success-box'>
            <b>2nd Order</b><br>
            ZC: ₹184<br>
            NonZC: ₹129<br>
            <span style='color: #4CAF50'>+43.1% higher</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='success-box'>
            <b>Avg Order Value</b><br>
            ZC: ₹216<br>
            NonZC: ₹132<br>
            <span style='color: #4CAF50'>+64% higher</span>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Retention Funnel Analysis")
        
        # Create funnel data
        funnel_data = []
        
        for cohort in ['ZC_Acquired', 'NonZC_Acquired']:
            cohort_data = df_sorted[df_sorted['cohort'] == cohort]
            initial = cohort_data[cohort_data['order_number'] == 1]['patient-id'].nunique()
            
            for order_num in range(1, 6):
                customers = cohort_data[cohort_data['order_number'] == order_num]['patient-id'].nunique()
                retention = (customers / initial * 100) if initial > 0 else 0
                
                funnel_data.append({
                    'Cohort': cohort.replace('_', ' '),
                    'Stage': f"Order {order_num}",
                    'Customers': customers,
                    'Retention': retention
                })
        
        funnel_df = pd.DataFrame(funnel_data)
        
        # Create funnel chart
        fig = go.Figure()
        
        for cohort in ['ZC Acquired', 'NonZC Acquired']:
            cohort_data = funnel_df[funnel_df['Cohort'] == cohort]
            color = '#667eea' if 'ZC' in cohort else '#f5576c'
            
            fig.add_trace(go.Funnel(
                name=cohort,
                y=cohort_data['Stage'],
                x=cohort_data['Retention'],
                textinfo="value+percent initial",
                marker=dict(color=color),
                opacity=0.8
            ))
        
        fig.update_layout(
            title="Customer Retention Funnel",
            height=500,
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            font={'color': theme['font_color']}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Retention metrics
        st.markdown("### 📊 Retention Metrics Summary")
        
        retention_summary = funnel_df.pivot(index='Stage', columns='Cohort', values='Retention').round(1)
        retention_summary['Difference'] = retention_summary['ZC Acquired'] - retention_summary['NonZC Acquired']
        
        st.dataframe(
            retention_summary.style.format("{:.1f}%").background_gradient(cmap='RdYlGn', subset=['Difference']),
            use_container_width=True
        )
    
    with tab4:
        st.markdown("### Lifetime Value Analysis")
        
        # Calculate LTV metrics
        ltv_metrics = []
        for cohort, name in [(zc_acquired, 'ZC-Acquired'), (nonzc_acquired, 'NonZC-Acquired')]:
            cohort_trans = df_sorted[df_sorted['patient-id'].isin(cohort)]
            customer_ltv = cohort_trans.groupby('patient-id').agg({
                'revenue-value': 'sum',
                'order_number': 'max',
                'bill_date': ['min', 'max']
            }).reset_index()
            
            customer_ltv.columns = ['patient_id', 'total_spend', 'total_orders', 'first_date', 'last_date']
            customer_ltv['days_active'] = (customer_ltv['last_date'] - customer_ltv['first_date']).dt.days
            
            ltv_metrics.append({
                'Cohort': name,
                'Avg_LTV': customer_ltv['total_spend'].mean(),
                'Median_LTV': customer_ltv['total_spend'].median(),
                'Avg_Orders': customer_ltv['total_orders'].mean(),
                'Avg_Days': customer_ltv['days_active'].mean()
            })
        
        ltv_df = pd.DataFrame(ltv_metrics)
        
        # Create comparison chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Average Lifetime Value", "Median Lifetime Value", 
                          "Average Orders per Customer", "Average Days Active"),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        colors = ['#667eea', '#f5576c']
        
        fig.add_trace(
            go.Bar(x=ltv_df['Cohort'], y=ltv_df['Avg_LTV'], marker_color=colors, name='Avg LTV'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(x=ltv_df['Cohort'], y=ltv_df['Median_LTV'], marker_color=colors, name='Median LTV'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=ltv_df['Cohort'], y=ltv_df['Avg_Orders'], marker_color=colors, name='Avg Orders'),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(x=ltv_df['Cohort'], y=ltv_df['Avg_Days'], marker_color=colors, name='Avg Days'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            font={'color': theme['font_color']}
        )
        
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(title_text="", row=i, col=j)
        
        fig.update_yaxes(title_text="₹", row=1, col=1)
        fig.update_yaxes(title_text="₹", row=1, col=2)
        fig.update_yaxes(title_text="Orders", row=2, col=1)
        fig.update_yaxes(title_text="Days", row=2, col=2)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ROI Calculation
        st.markdown("### 💎 ROI of ZC Acquisition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='success-box'>
            <h4>Investment Analysis</h4>
            <b>Cost:</b> ₹30 discount on first order<br>
            <b>Return:</b> ₹333 additional LTV<br>
            <b>ROI:</b> <span style='font-size: 1.5em; color: #4CAF50'>1,010%</span><br><br>
            Every ₹1 spent on ZC acquisition<br>
            returns ₹11.10 in incremental value
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='insight-box'>
            <h4>Scaling Opportunity</h4>
            Current: 0.5% of new users via ZC<br>
            Target: 10% of new users via ZC<br>
            Impact: +1,300 premium customers/month<br>
            <b>Incremental LTV:</b> ₹433,000/month<br><br>
            <span style='color: #667eea'>20x growth potential</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Strategic Recommendations
    st.markdown("---")
    st.markdown("### 🎯 Strategic Recommendations")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='recommendation-card'>
        <b>1️⃣ Acquisition Focus</b><br>
        Prioritize ZenoCoin for<br>
        new user campaigns
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='recommendation-card'>
        <b>2️⃣ First Order Promo</b><br>
        Create "First Order<br>
        with ZenoCoin" offers
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='recommendation-card'>
        <b>3️⃣ Track Source</b><br>
        Monitor acquisition<br>
        channel as KPI
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='recommendation-card'>
        <b>4️⃣ Onboarding</b><br>
        Design flow to encourage<br>
        ZC on order #1
        </div>
        """, unsafe_allow_html=True)

def get_chart_theme():
    """Get chart theme based on dark mode setting"""
    if st.session_state.dark_mode:
        return {
            'template': 'plotly_dark',
            'paper_bgcolor': '#1e1e1e',
            'plot_bgcolor': '#1e1e1e',
            'font_color': '#ffffff',
            'gridcolor': '#444444'
        }
    else:
        return {
            'template': 'plotly_white',
            'paper_bgcolor': 'white',
            'plot_bgcolor': 'white',
            'font_color': '#333333',
            'gridcolor': '#e0e0e0'
        }

def show_zc_adoption_impact(df):
    """Show behavior change analysis after ZC adoption"""
    theme = get_chart_theme()
    
    st.markdown("## 🔄 ZC Adoption Impact Analysis")
    st.markdown("### How Customer Behavior Changes After First ZenoCoin Usage")
    
    # Convert dates
    df['bill_date'] = pd.to_datetime(df['bill_date'])
    
    # Identify ZenoCoin usage
    df['used_zenocoin'] = ((df['eligibility_flag'] == 1) & 
                          ((df.get('zrd_promo_discount', 0) > 0) | 
                           (df.get('other_promo_discount', 0) > 0))).astype(int)
    
    # Sort by customer and date
    df = df.sort_values(['patient-id', 'bill_date'])
    
    # Find first ZC usage for each customer
    zc_users = df[df['used_zenocoin'] == 1].groupby('patient-id')['bill_date'].min().reset_index()
    zc_users.columns = ['patient_id', 'first_zc_date']
    
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
    
    # Focus on customers who adopted ZC (have both before and after)
    adopters_with_history = df_with_adoption[
        (df_with_adoption['patient_id'].notna()) &
        (df_with_adoption['patient_id'].isin(
            df_with_adoption[df_with_adoption['adoption_phase'] == 'Before_ZC']['patient_id'].unique()
        ))
    ]
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_adopters = len(zc_users)
    with_history = adopters_with_history['patient_id'].nunique()
    
    with col1:
        st.metric("Total ZC Adopters", f"{total_adopters:,}")
    
    with col2:
        st.metric("With Before/After Data", f"{with_history:,}")
    
    with col3:
        adoption_rate = (total_adopters / df['patient-id'].nunique()) * 100
        st.metric("Adoption Rate", f"{adoption_rate:.1f}%")
    
    with col4:
        avg_days_to_adopt = df_with_adoption[
            df_with_adoption['adoption_phase'] == 'Before_ZC'
        ].groupby('patient_id')['days_from_adoption'].max().abs().mean()
        st.metric("Avg Days to Adopt", f"{avg_days_to_adopt:.0f}")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Before vs After", 
        "📈 Time Evolution", 
        "🎯 Customer Transformation",
        "📌 Retention Impact"
    ])
    
    with tab1:
        st.markdown("### Before vs After ZC Adoption Metrics")
        
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
        
        # Get summary statistics
        before_metrics = phase_metrics[phase_metrics['phase'] == 'Before_ZC']
        after_metrics = phase_metrics[phase_metrics['phase'] == 'After_ZC']
        
        # Create comparison visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction Value Comparison
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=before_metrics['avg_transaction'],
                name='Before ZC',
                marker_color='#f5576c'
            ))
            
            fig.add_trace(go.Box(
                y=after_metrics['avg_transaction'],
                name='After ZC',
                marker_color='#4CAF50'
            ))
            
            fig.update_layout(
                title="Transaction Value Distribution",
                yaxis_title="Average Transaction Value (₹)",
                showlegend=False,
                height=400,
                template=theme['template'],
                paper_bgcolor=theme['paper_bgcolor'],
                font={'color': theme['font_color']}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Frequency Comparison
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=before_metrics['transaction_frequency'],
                name='Before ZC',
                marker_color='#f5576c'
            ))
            
            fig.add_trace(go.Box(
                y=after_metrics['transaction_frequency'],
                name='After ZC',
                marker_color='#4CAF50'
            ))
            
            fig.update_layout(
                title="Transaction Frequency Distribution",
                yaxis_title="Transactions per Month",
                showlegend=False,
                height=400,
                template=theme['template'],
                paper_bgcolor=theme['paper_bgcolor'],
                font={'color': theme['font_color']}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Summary metrics
        st.markdown("### 📊 Aggregate Impact Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        avg_before_transaction = before_metrics['avg_transaction'].mean()
        avg_after_transaction = after_metrics['avg_transaction'].mean()
        transaction_value_lift = ((avg_after_transaction / avg_before_transaction - 1) * 100) if avg_before_transaction > 0 else 0
        
        avg_before_freq = before_metrics['transaction_frequency'].mean()
        avg_after_freq = after_metrics['transaction_frequency'].mean()
        frequency_lift = ((avg_after_freq / avg_before_freq - 1) * 100) if avg_before_freq > 0 else 0
        
        with col1:
            st.markdown(f"""
            <div class='kpi-card'>
            <div class='kpi-value'>₹{avg_before_transaction:.0f} → ₹{avg_after_transaction:.0f}</div>
            <div class='kpi-label'>Transaction Value</div>
            <div class='kpi-delta' style='color: {"#4CAF50" if transaction_value_lift > 0 else "#f5576c"}'>
            {transaction_value_lift:+.1f}% change</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='kpi-card'>
            <div class='kpi-value'>{avg_before_freq:.1f} → {avg_after_freq:.1f}</div>
            <div class='kpi-label'>Monthly Frequency</div>
            <div class='kpi-delta' style='color: {"#4CAF50" if frequency_lift > 0 else "#f5576c"}'>
            {frequency_lift:+.1f}% change</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_spend_before = before_metrics['total_spend'].mean()
            total_spend_after = after_metrics['total_spend'].mean()
            spend_lift = ((total_spend_after / total_spend_before - 1) * 100) if total_spend_before > 0 else 0
            
            st.markdown(f"""
            <div class='kpi-card'>
            <div class='kpi-value'>₹{total_spend_before:.0f} → ₹{total_spend_after:.0f}</div>
            <div class='kpi-label'>Avg Total Spend</div>
            <div class='kpi-delta' style='color: {"#4CAF50" if spend_lift > 0 else "#f5576c"}'>
            {spend_lift:+.1f}% change</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            active_days_before = before_metrics['days_active'].mean()
            active_days_after = after_metrics['days_active'].mean()
            
            st.markdown(f"""
            <div class='kpi-card'>
            <div class='kpi-value'>{active_days_before:.0f} → {active_days_after:.0f}</div>
            <div class='kpi-label'>Avg Days Active</div>
            <div class='kpi-delta' style='color: #667eea'>
            Days in period</div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Time-based Behavior Evolution")
        
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
        
        if window_metrics:
            window_df = pd.DataFrame(window_metrics)
            
            # Create time evolution chart
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Average Transaction Value", "ZC Usage Rate", 
                              "Active Customers", "Transaction Volume")
            )
            
            # Define colors for before/after
            colors = ['#f5576c' if 'before' in w else '#4CAF50' for w in window_df['window']]
            
            fig.add_trace(
                go.Bar(x=window_df['window'], y=window_df['avg_spend'], 
                      marker_color=colors, name='Avg Spend'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=window_df['window'], y=window_df['zc_usage_rate'],
                      marker_color=colors, name='ZC Usage %'),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(x=window_df['window'], y=window_df['unique_customers'],
                      marker_color=colors, name='Customers'),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Bar(x=window_df['window'], y=window_df['transactions'],
                      marker_color=colors, name='Transactions'),
                row=2, col=2
            )
            
            # Add vertical line at adoption point
            for i in range(1, 3):
                for j in range(1, 3):
                    fig.add_vline(x=1.5, line_dash="dash", line_color="gray", row=i, col=j)
            
            fig.update_layout(
                height=600,
                showlegend=False,
                template=theme['template'],
                paper_bgcolor=theme['paper_bgcolor'],
                font={'color': theme['font_color']}
            )
            
            fig.update_xaxes(tickangle=45)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.markdown("### 📋 Time Window Metrics")
            st.dataframe(
                window_df.style.format({
                    'avg_spend': '₹{:.2f}',
                    'transactions': '{:,.0f}',
                    'unique_customers': '{:,.0f}',
                    'zc_usage_rate': '{:.1f}%'
                }).background_gradient(cmap='RdYlGn', subset=['avg_spend', 'zc_usage_rate']),
                use_container_width=True
            )
    
    with tab3:
        st.markdown("### Individual Customer Transformations")
        
        # Track individual customer transformations (sample for performance)
        customer_transformations = []
        
        sample_customers = before_metrics['patient_id'].unique()[:min(1000, len(before_metrics))]
        
        for customer_id in sample_customers:
            before = before_metrics[before_metrics['patient_id'] == customer_id]
            after = after_metrics[after_metrics['patient_id'] == customer_id]
            
            if len(before) > 0 and len(after) > 0:
                before_row = before.iloc[0]
                after_row = after.iloc[0]
                
                transformation = {
                    'customer_id': customer_id,
                    'before_avg_transaction': before_row['avg_transaction'],
                    'after_avg_transaction': after_row['avg_transaction'],
                    'transaction_lift': ((after_row['avg_transaction'] / before_row['avg_transaction'] - 1) * 100) if before_row['avg_transaction'] > 0 else 0,
                    'before_frequency': before_row['transaction_frequency'],
                    'after_frequency': after_row['transaction_frequency'],
                    'frequency_lift': ((after_row['transaction_frequency'] / before_row['transaction_frequency'] - 1) * 100) if before_row['transaction_frequency'] > 0 else 0
                }
                customer_transformations.append(transformation)
        
        if customer_transformations:
            transformation_df = pd.DataFrame(customer_transformations)
            
            # Create distribution of impact
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Transaction Value Impact Distribution", "Frequency Impact Distribution")
            )
            
            fig.add_trace(
                go.Histogram(x=transformation_df['transaction_lift'], 
                           nbinsx=30, 
                           marker_color='#667eea',
                           name='Transaction Lift'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Histogram(x=transformation_df['frequency_lift'], 
                           nbinsx=30, 
                           marker_color='#764ba2',
                           name='Frequency Lift'),
                row=1, col=2
            )
            
            fig.update_xaxes(title_text="% Change", row=1, col=1)
            fig.update_xaxes(title_text="% Change", row=1, col=2)
            fig.update_yaxes(title_text="Number of Customers", row=1, col=1)
            fig.update_yaxes(title_text="Number of Customers", row=1, col=2)
            
            fig.update_layout(
                height=400,
                showlegend=False,
                template=theme['template'],
                paper_bgcolor=theme['paper_bgcolor'],
                font={'color': theme['font_color']}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Impact segments
            transformation_df['impact_segment'] = pd.cut(
                transformation_df['transaction_lift'],
                bins=[-np.inf, 0, 50, 100, np.inf],
                labels=['Negative', 'Low (0-50%)', 'Medium (50-100%)', 'High (>100%)']
            )
            
            st.markdown("### 🎯 Customer Impact Distribution")
            
            col1, col2, col3, col4 = st.columns(4)
            
            segment_counts = transformation_df['impact_segment'].value_counts()
            
            for idx, (col, segment) in enumerate(zip([col1, col2, col3, col4], 
                                                     ['Negative', 'Low (0-50%)', 'Medium (50-100%)', 'High (>100%)'])):
                with col:
                    count = segment_counts.get(segment, 0)
                    pct = (count / len(transformation_df) * 100) if len(transformation_df) > 0 else 0
                    
                    color = '#f5576c' if segment == 'Negative' else '#4CAF50'
                    if segment == 'Low (0-50%)':
                        color = '#ffd166'
                    elif segment == 'Medium (50-100%)':
                        color = '#06ffa5'
                    
                    st.markdown(f"""
                    <div class='kpi-card'>
                    <div class='kpi-value' style='color: {color}'>{count}</div>
                    <div class='kpi-label'>{segment}</div>
                    <div class='kpi-delta'>{pct:.1f}% of customers</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Top transformations
            st.markdown("### 🏆 Top Customer Transformations")
            
            top_transformations = transformation_df.nlargest(10, 'transaction_lift')[
                ['customer_id', 'before_avg_transaction', 'after_avg_transaction', 
                 'transaction_lift', 'frequency_lift']
            ]
            
            st.dataframe(
                top_transformations.style.format({
                    'before_avg_transaction': '₹{:.2f}',
                    'after_avg_transaction': '₹{:.2f}',
                    'transaction_lift': '{:+.1f}%',
                    'frequency_lift': '{:+.1f}%'
                }).background_gradient(cmap='RdYlGn', subset=['transaction_lift', 'frequency_lift']),
                use_container_width=True
            )
    
    with tab4:
        st.markdown("### Retention Impact After ZC Adoption")
        
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
        
        retention_df = pd.DataFrame(retention_analysis)
        
        # Create retention curve
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=retention_df['days_after'],
            y=retention_df['retention_rate'],
            mode='lines+markers',
            name='Post-Adoption Retention',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Customer Retention After First ZC Usage",
            xaxis_title="Days After First ZC Usage",
            yaxis_title="Retention Rate (%)",
            height=400,
            template=theme['template'],
            paper_bgcolor=theme['paper_bgcolor'],
            font={'color': theme['font_color']},
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Retention metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("7-Day Retention", f"{retention_df[retention_df['days_after']==7]['retention_rate'].iloc[0]:.1f}%")
        
        with col2:
            st.metric("14-Day Retention", f"{retention_df[retention_df['days_after']==14]['retention_rate'].iloc[0]:.1f}%")
        
        with col3:
            st.metric("30-Day Retention", f"{retention_df[retention_df['days_after']==30]['retention_rate'].iloc[0]:.1f}%")
        
        with col4:
            st.metric("90-Day Retention", f"{retention_df[retention_df['days_after']==90]['retention_rate'].iloc[0]:.1f}%")
        
        # Cohort retention heatmap
        st.markdown("### 📊 Adoption Cohort Retention")
        
        # Create monthly cohorts
        zc_users['adoption_month'] = pd.to_datetime(zc_users['first_zc_date']).dt.to_period('M')
        
        # Calculate retention for each cohort
        cohort_retention = []
        
        for cohort_month in zc_users['adoption_month'].unique()[:6]:  # Last 6 months
            cohort_users = zc_users[zc_users['adoption_month'] == cohort_month]['patient_id'].values
            
            for month_offset in range(0, 4):  # Track 4 months
                target_month = cohort_month + month_offset
                
                retained = adopters_with_history[
                    (adopters_with_history['patient_id'].isin(cohort_users)) &
                    (pd.to_datetime(adopters_with_history['bill_date']).dt.to_period('M') == target_month)
                ]['patient_id'].nunique()
                
                retention = (retained / len(cohort_users) * 100) if len(cohort_users) > 0 else 0
                
                cohort_retention.append({
                    'cohort': str(cohort_month),
                    'month': f'Month {month_offset}',
                    'retention': retention
                })
        
        if cohort_retention:
            cohort_retention_df = pd.DataFrame(cohort_retention)
            pivot_retention = cohort_retention_df.pivot(index='cohort', columns='month', values='retention')
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=pivot_retention.values,
                x=pivot_retention.columns,
                y=pivot_retention.index,
                colorscale='RdYlGn',
                text=np.round(pivot_retention.values, 1),
                texttemplate='%{text}%',
                textfont={"size": 10},
                colorbar=dict(title="Retention %")
            ))
            
            fig.update_layout(
                title="Monthly Cohort Retention After ZC Adoption",
                xaxis_title="Months Since Adoption",
                yaxis_title="Adoption Cohort",
                height=400,
                template=theme['template'],
                paper_bgcolor=theme['paper_bgcolor'],
                font={'color': theme['font_color']}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Strategic Insights
    st.markdown("---")
    st.markdown("### 💡 Key Insights - ZC Adoption Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class='success-box'>
        <h4>Behavioral Transformation</h4>
        <b>Transaction Value:</b> {transaction_value_lift:+.1f}% increase<br>
        <b>Purchase Frequency:</b> {frequency_lift:+.1f}% increase<br>
        <b>90-Day Retention:</b> {retention_df[retention_df['days_after']==90]['retention_rate'].iloc[0]:.1f}%<br><br>
        
        ZenoCoin adoption creates a behavioral inflection point,
        driving sustained increases in customer value.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        positive_impact = len(transformation_df[transformation_df['transaction_lift'] > 0]) if customer_transformations else 0
        total_analyzed = len(transformation_df) if customer_transformations else 1
        
        st.markdown(f"""
        <div class='insight-box'>
        <h4>Impact Distribution</h4>
        <b>Positive Impact:</b> {positive_impact}/{total_analyzed} customers<br>
        <b>Success Rate:</b> {(positive_impact/total_analyzed*100):.1f}%<br>
        <b>High Impact (>100%):</b> {len(transformation_df[transformation_df['transaction_lift'] > 100]) if customer_transformations else 0} customers<br><br>
        
        Majority of customers show improved behavior after
        adopting ZenoCoin, validating the program's effectiveness.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()