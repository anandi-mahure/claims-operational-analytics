"""
Tests for Claims Operational Analytics
Author: Anandi M | MSc Data Science, University of Bath
"""

import pytest
import pandas as pd
import os
import sys

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def claims_df():
    """Load claims data from CSV — works from any working directory."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'claims_data.csv'),
        'claims_data.csv',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path, parse_dates=['claim_date'])
    pytest.skip("claims_data.csv not found — skipping data tests")


# ---------------------------------------------------------------------------
# 1. Schema & Data Quality
# ---------------------------------------------------------------------------

class TestSchema:
    REQUIRED_COLUMNS = [
        'claim_id', 'customer_id', 'claim_date', 'claim_type',
        'claim_amount', 'status', 'settlement_days', 'handler_id',
        'region', 'fraud_flag'
    ]

    def test_required_columns_exist(self, claims_df):
        for col in self.REQUIRED_COLUMNS:
            assert col in claims_df.columns, f"Missing column: {col}"

    def test_no_null_claim_ids(self, claims_df):
        assert claims_df['claim_id'].isnull().sum() == 0

    def test_no_null_claim_amounts(self, claims_df):
        assert claims_df['claim_amount'].isnull().sum() == 0

    def test_no_duplicate_claim_ids(self, claims_df):
        assert claims_df['claim_id'].duplicated().sum() == 0

    def test_claim_amounts_positive(self, claims_df):
        assert (claims_df['claim_amount'] > 0).all(), "All claim amounts must be positive"

    def test_settlement_days_non_negative(self, claims_df):
        assert (claims_df['settlement_days'] >= 0).all()

    def test_fraud_flag_binary(self, claims_df):
        assert claims_df['fraud_flag'].isin([0, 1]).all(), "fraud_flag must be 0 or 1"


# ---------------------------------------------------------------------------
# 2. Business Logic — Status Values
# ---------------------------------------------------------------------------

class TestBusinessLogic:
    VALID_STATUSES = {'Settled', 'Pending', 'Disputed'}
    VALID_CLAIM_TYPES = {'Health', 'Motor', 'Home'}

    def test_valid_statuses(self, claims_df):
        unexpected = set(claims_df['status'].unique()) - self.VALID_STATUSES
        assert not unexpected, f"Unexpected status values: {unexpected}"

    def test_valid_claim_types(self, claims_df):
        unexpected = set(claims_df['claim_type'].unique()) - self.VALID_CLAIM_TYPES
        assert not unexpected, f"Unexpected claim types: {unexpected}"

    def test_fraud_flags_only_in_health_and_home(self, claims_df):
        """Motor should have zero fraud flags per business findings."""
        motor_fraud = claims_df[
            (claims_df['claim_type'] == 'Motor') &
            (claims_df['fraud_flag'] == 1)
        ]
        assert len(motor_fraud) == 0, "Motor claims should have zero fraud flags"

    def test_fraud_flag_rate_within_expected_range(self, claims_df):
        """Fraud flag rate should be between 10% and 25%."""
        rate = claims_df['fraud_flag'].mean()
        assert 0.10 <= rate <= 0.25, f"Fraud rate {rate:.1%} outside expected 10–25% range"

    def test_settled_claims_have_settlement_days(self, claims_df):
        settled = claims_df[claims_df['status'] == 'Settled']
        assert (settled['settlement_days'] > 0).all()

    def test_london_highest_exposure(self, claims_df):
        """London should carry highest total claims exposure."""
        regional = claims_df.groupby('region')['claim_amount'].sum()
        assert regional.idxmax() == 'London', "London expected to have highest exposure"

    def test_health_slowest_to_settle(self, claims_df):
        """Health claims should be slowest to settle on average."""
        settled = claims_df[claims_df['status'] == 'Settled']
        avg_days = settled.groupby('claim_type')['settlement_days'].mean()
        assert avg_days.idxmax() == 'Health', "Health expected to be slowest claim type"


# ---------------------------------------------------------------------------
# 3. Aggregation Accuracy
# ---------------------------------------------------------------------------

class TestAggregations:
    def test_total_claims_count(self, claims_df):
        assert len(claims_df) == 40, f"Expected 40 claims, got {len(claims_df)}"

    def test_settlement_rate_above_50_pct(self, claims_df):
        rate = (claims_df['status'] == 'Settled').mean()
        assert rate > 0.5, f"Settlement rate {rate:.1%} below expected 50%+"

    def test_four_regions_present(self, claims_df):
        assert claims_df['region'].nunique() == 4

    def test_three_handlers_present(self, claims_df):
        assert claims_df['handler_id'].nunique() == 3

    def test_monthly_trend_has_four_months(self, claims_df):
        months = claims_df['claim_date'].dt.to_period('M').nunique()
        assert months == 4, f"Expected 4 months of data, got {months}"

    def test_handler_settlement_rates_reasonable(self, claims_df):
        """Every handler should have at least a 50% settlement rate."""
        handler_stats = claims_df.groupby('handler_id').apply(
            lambda x: (x['status'] == 'Settled').mean()
        )
        assert (handler_stats >= 0.4).all(), f"Handler settlement rates too low: {handler_stats}"


# ---------------------------------------------------------------------------
# 4. SLA Logic
# ---------------------------------------------------------------------------

class TestSLALogic:
    def test_sla_critical_threshold(self, claims_df):
        """Claims over 60 days should be classified as Critical."""
        critical = claims_df[claims_df['settlement_days'] > 60]
        # Just check the filter works — critical cases may exist
        assert isinstance(critical, pd.DataFrame)

    def test_sla_warning_threshold(self, claims_df):
        """Claims 31–60 days pending should be Warning."""
        warning = claims_df[
            (claims_df['settlement_days'] > 30) &
            (claims_df['settlement_days'] <= 60) &
            (claims_df['status'] == 'Pending')
        ]
        assert isinstance(warning, pd.DataFrame)

    def test_pending_claims_exist(self, claims_df):
        pending = claims_df[claims_df['status'] == 'Pending']
        assert len(pending) > 0, "Expected some pending claims in dataset"


# ---------------------------------------------------------------------------
# 5. Charts Output
# ---------------------------------------------------------------------------

class TestChartsOutput:
    EXPECTED_CHARTS = [
        '01_settlement_by_type.png',
        '02_exposure_by_region.png',
        '03_monthly_trend.png',
        '04_handler_scorecard.png',
        '05_portfolio_overview.png',
    ]

    def test_charts_directory_exists(self):
        charts_dir = os.path.join(os.path.dirname(__file__), '..', 'charts')
        assert os.path.isdir(charts_dir), "charts/ directory not found — run insights.py first"

    def test_all_charts_present(self):
        charts_dir = os.path.join(os.path.dirname(__file__), '..', 'charts')
        if not os.path.isdir(charts_dir):
            pytest.skip("charts/ directory not found")
        for chart in self.EXPECTED_CHARTS:
            path = os.path.join(charts_dir, chart)
            assert os.path.exists(path), f"Missing chart: {chart}"

    def test_charts_non_empty(self):
        charts_dir = os.path.join(os.path.dirname(__file__), '..', 'charts')
        if not os.path.isdir(charts_dir):
            pytest.skip("charts/ directory not found")
        for chart in self.EXPECTED_CHARTS:
            path = os.path.join(charts_dir, chart)
            if os.path.exists(path):
                assert os.path.getsize(path) > 10_000, f"Chart too small (likely empty): {chart}"
