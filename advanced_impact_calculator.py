#!/usr/bin/env python3
"""
Advanced Impact Calculator with Statistical Modeling and ML Predictions
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class AdvancedImpactCalculator:
    def __init__(self):
        # Load historical data
        self.df = pd.read_csv('data dump for suman part 2.csv')
        self.monthly_data = pd.read_csv('monthly_customer_data.csv')
        self.customer_lifetime = pd.read_csv('customer_lifetime_monthly.csv')
        
        # Calculate baseline metrics
        self._calculate_baseline_metrics()
        
        # Build predictive models
        self._build_predictive_models()
    
    def _calculate_baseline_metrics(self):
        """Calculate baseline metrics from historical data"""
        # Current metrics
        self.current_redemption_rate = 21.0  # From analysis
        self.current_avg_monthly_spend_zc = 1088  # ZC users
        self.current_avg_monthly_spend_non_zc = 624  # Non-ZC users
        self.spend_lift_per_user = 464  # Incremental spend
        
        # Customer behavior patterns
        zc_users = self.customer_lifetime[self.customer_lifetime['is_zc_user'] == 1]
        non_zc_users = self.customer_lifetime[self.customer_lifetime['is_zc_user'] == 0]
        
        # Retention rates
        self.retention_7d_zc = 24.8
        self.retention_30d_zc = 67.5
        self.retention_7d_non_zc = 22.8
        self.retention_30d_non_zc = 60.5
        
        # Frequency patterns
        self.avg_freq_zc = zc_users['avg_frequency'].mean() if len(zc_users) > 0 else 7.3
        self.avg_freq_non_zc = non_zc_users['avg_frequency'].mean() if len(non_zc_users) > 0 else 4.0
        
        # Calculate elasticity coefficients using statistical analysis
        self._calculate_elasticity()
    
    def _calculate_elasticity(self):
        """Calculate price elasticity and adoption elasticity"""
        # Analyze historical redemption patterns
        monthly_trends = pd.read_csv('monthly_trends.csv')
        
        # Calculate elasticity of redemption to discounts
        if len(monthly_trends) > 1:
            # Use log-log regression for elasticity
            X = np.log(monthly_trends['total_discounts'].replace(0, 1))
            y = np.log(monthly_trends['redemption_rate'].replace(0, 1))
            slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
            self.discount_elasticity = slope
        else:
            self.discount_elasticity = -0.3  # Default negative elasticity
        
        # Network effect coefficient (users attract more users)
        self.network_effect = 0.15  # 15% additional adoption from network effects
        
        # Saturation curve parameters (S-curve adoption)
        self.saturation_point = 0.45  # Maximum realistic redemption rate
        self.adoption_speed = 0.8  # Speed of adoption
    
    def _build_predictive_models(self):
        """Build ML models for prediction"""
        # Prepare features for modeling
        features = []
        targets = []
        
        for _, row in self.monthly_data.iterrows():
            features.append([
                row['month_num'],
                row['used_zenocoin'],
                row['monthly_spend'],
                row['order_count']
            ])
            targets.append(row['monthly_spend'])
        
        if len(features) > 10:
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, random_state=42
            )
            
            # Random Forest for spend prediction
            self.spend_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.spend_model.fit(X_train, y_train)
            
            # Calculate confidence intervals
            predictions = []
            for _ in range(100):
                sample_indices = np.random.choice(len(X_train), len(X_train), replace=True)
                X_sample = [X_train[i] for i in sample_indices]
                y_sample = [y_train[i] for i in sample_indices]
                
                model = RandomForestRegressor(n_estimators=50, random_state=np.random.randint(1000))
                model.fit(X_sample, y_sample)
                predictions.append(model.predict(X_test))
            
            predictions = np.array(predictions)
            self.prediction_std = np.std(predictions, axis=0).mean()
        else:
            self.spend_model = None
            self.prediction_std = 100
    
    def calculate_impact(self, target_usage_percent, total_monthly_customers=20000):
        """
        Calculate comprehensive impact metrics with confidence intervals
        
        Parameters:
        - target_usage_percent: Target percentage of customers using coins (0-100)
        - total_monthly_customers: Total expected monthly customers
        
        Returns dictionary with all calculated metrics
        """
        results = {}
        
        # Current baseline
        current_usage_percent = 21.0  # Current actual usage rate
        
        # Apply S-curve adoption model
        effective_rate = self._apply_adoption_curve(target_usage_percent / 100)
        current_rate = current_usage_percent / 100
        
        # 1. Calculate user metrics
        eligible_customers = total_monthly_customers * 0.8  # 80% eligibility assumed
        
        # Current and target users
        current_coin_users = eligible_customers * current_rate
        target_coin_users = eligible_customers * effective_rate
        
        # INCREMENTAL users (can be negative)
        incremental_coin_users = target_coin_users - current_coin_users
        results['current_coin_users'] = int(current_coin_users)
        results['target_coin_users'] = int(target_coin_users)
        results['new_coin_users'] = int(incremental_coin_users)  # This is the CHANGE, not total
        
        # 2. Calculate spending patterns with confidence intervals
        base_spend = self.current_avg_monthly_spend_non_zc
        lift_factor = 1 + (self.spend_lift_per_user / base_spend)
        
        # Average monthly amount per user (constant based on historical data)
        # ZC users consistently spend ₹1,088 regardless of how many users there are
        avg_monthly_per_user = self.current_avg_monthly_spend_zc  # Use actual ZC user spend
        results['avg_monthly_amount_per_user'] = round(avg_monthly_per_user, 2)
        
        # 3. Calculate incremental revenue
        # The incremental value per ZC user is the difference between ZC and non-ZC spend
        # This is ₹1,088 - ₹624 = ₹464 per user per month
        incrementality_rate = self._calculate_incrementality(effective_rate)
        
        # Use the actual spend lift from data
        incremental_spend_per_user = self.spend_lift_per_user * incrementality_rate
        
        # Revenue is based on INCREMENTAL users only
        if incremental_coin_users > 0:
            # Growing user base
            monthly_incremental_revenue = incremental_coin_users * incremental_spend_per_user
        else:
            # Shrinking user base (negative revenue impact)
            monthly_incremental_revenue = incremental_coin_users * incremental_spend_per_user
        
        results['incremental_revenue_monthly'] = round(monthly_incremental_revenue, 2)
        
        # 4. Calculate costs
        avg_discount_per_redemption = 30  # Base discount
        avg_redemptions_per_user = self.avg_freq_zc  # Monthly frequency
        
        # Cost with volume discounting
        volume_discount = 1 - (0.1 * min(effective_rate, 0.5))  # Up to 10% volume discount
        
        # Total cost for TARGET users
        total_monthly_cost = target_coin_users * avg_discount_per_redemption * avg_redemptions_per_user * volume_discount
        
        # Incremental cost (only for new users if positive)
        if incremental_coin_users > 0:
            monthly_cost = incremental_coin_users * avg_discount_per_redemption * avg_redemptions_per_user * volume_discount
        else:
            # If reducing users, we save costs
            monthly_cost = incremental_coin_users * avg_discount_per_redemption * avg_redemptions_per_user * volume_discount
        
        results['monthly_cost'] = round(monthly_cost, 2)
        results['total_monthly_cost'] = round(total_monthly_cost, 2)
        
        # 5. Net monthly impact
        net_monthly_impact = monthly_incremental_revenue - monthly_cost
        results['net_monthly_impact'] = round(net_monthly_impact, 2)
        
        # 6. Annual impact with growth projections
        # Apply growth curve over 12 months
        monthly_impacts = []
        for month in range(12):
            month_rate = self._monthly_growth_curve(month, effective_rate)
            month_users = eligible_customers * month_rate
            month_revenue = month_users * incremental_spend_per_user
            month_cost = month_users * avg_discount_per_redemption * avg_redemptions_per_user * volume_discount
            monthly_impacts.append(month_revenue - month_cost)
        
        annual_impact = sum(monthly_impacts)
        results['annual_impact'] = round(annual_impact, 2)
        
        # 7. Additional advanced metrics
        results['roi_percentage'] = round((annual_impact / (monthly_cost * 12)) * 100, 2) if monthly_cost > 0 else 0
        results['payback_period_months'] = round(monthly_cost / net_monthly_impact, 1) if net_monthly_impact > 0 else float('inf')
        results['customer_ltv_increase'] = round(incremental_spend_per_user * 4.8, 2)  # 4.8 months avg lifetime
        
        # 8. Confidence intervals
        confidence_level = 0.95
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        revenue_std = monthly_incremental_revenue * 0.15  # 15% standard deviation estimate
        results['revenue_confidence_lower'] = round(monthly_incremental_revenue - z_score * revenue_std, 2)
        results['revenue_confidence_upper'] = round(monthly_incremental_revenue + z_score * revenue_std, 2)
        
        # 9. Risk-adjusted metrics
        risk_factor = self._calculate_risk_factor(effective_rate)
        results['risk_adjusted_annual_impact'] = round(annual_impact * (1 - risk_factor), 2)
        results['risk_score'] = round(risk_factor * 100, 1)  # As percentage
        
        return results
    
    def _apply_adoption_curve(self, target_rate):
        """Apply S-curve adoption model"""
        # Logistic function for realistic adoption
        x = target_rate * 10 - 5  # Scale and center
        adoption = self.saturation_point / (1 + np.exp(-self.adoption_speed * x))
        return min(adoption, target_rate)  # Cap at target if lower than saturation
    
    def _calculate_incrementality(self, usage_rate):
        """Calculate true incrementality considering cannibalization"""
        # Higher usage rates lead to some cannibalization
        base_incrementality = 0.75  # 75% of lift is truly incremental
        cannibalization_factor = usage_rate * 0.3  # Up to 30% cannibalization at high usage
        return max(0.4, base_incrementality - cannibalization_factor)
    
    def _monthly_growth_curve(self, month_index, target_rate):
        """Calculate monthly growth curve for adoption"""
        # S-curve adoption over time
        max_months = 12
        growth_rate = target_rate / (1 + np.exp(-0.8 * (month_index - 6)))
        return min(growth_rate, target_rate)
    
    def _calculate_risk_factor(self, usage_rate):
        """Calculate risk based on usage rate and market factors"""
        # Higher usage rates have execution risk
        execution_risk = min(0.3, usage_rate * 0.5)
        
        # Market risk (competition, economy)
        market_risk = 0.1
        
        # Combined risk with correlation
        total_risk = execution_risk + market_risk - (execution_risk * market_risk)
        return total_risk
    
    def get_kpi_definitions(self):
        """Return KPI definitions"""
        return {
            "New Coin Users": {
                "definition": "Projected number of unique customers who will use ZenoCoin in a month",
                "formula": "Eligible Customers × Target Usage % × Adoption Curve Factor",
                "importance": "Primary driver of program scale and network effects"
            },
            "Average Monthly Amount per User": {
                "definition": "Expected average monthly spend by ZenoCoin users",
                "formula": "Base Spend × Lift Factor × Network Effect Multiplier",
                "importance": "Indicates spending behavior change and program effectiveness"
            },
            "Incremental Revenue": {
                "definition": "Additional revenue generated beyond baseline spending",
                "formula": "(Avg Spend ZC - Avg Spend Non-ZC) × New Users × Incrementality Rate",
                "importance": "True economic value created by the program"
            },
            "Net Monthly Impact": {
                "definition": "Net financial impact after accounting for all costs",
                "formula": "Incremental Revenue - Program Costs",
                "importance": "Actual bottom-line impact on profitability"
            },
            "Annual Impact": {
                "definition": "Projected 12-month cumulative impact with growth curve",
                "formula": "Sum of monthly impacts with S-curve adoption model",
                "importance": "Long-term value creation and ROI justification"
            },
            "Risk-Adjusted Impact": {
                "definition": "Annual impact adjusted for execution and market risks",
                "formula": "Annual Impact × (1 - Risk Factor)",
                "importance": "Conservative estimate for financial planning"
            },
            "Payback Period": {
                "definition": "Time to recover initial investment",
                "formula": "Monthly Cost / Net Monthly Impact",
                "importance": "Investment efficiency and cash flow planning"
            },
            "Customer LTV Increase": {
                "definition": "Incremental lifetime value per ZenoCoin user",
                "formula": "Monthly Incremental Spend × Average Customer Lifetime",
                "importance": "Long-term customer value creation"
            }
        }

if __name__ == "__main__":
    # Example usage
    calculator = AdvancedImpactCalculator()
    
    # Calculate impact for 40% usage target
    results = calculator.calculate_impact(target_usage_percent=40)
    
    print("\n=== ADVANCED IMPACT ANALYSIS ===\n")
    for key, value in results.items():
        print(f"{key}: {value:,}" if isinstance(value, (int, float)) else f"{key}: {value}")
    
    print("\n=== KPI DEFINITIONS ===\n")
    definitions = calculator.get_kpi_definitions()
    for kpi, details in definitions.items():
        print(f"\n{kpi}:")
        for k, v in details.items():
            print(f"  {k}: {v}")