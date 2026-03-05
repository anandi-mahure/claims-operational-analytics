"""
Claims Operational Analytics — Python Insights
Author: Anandi M | MSc Data Science, University of Bath
Description: Loads claims data, runs operational analytics
             and produces 5 business-ready visualisations
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ── LOAD DATA ────────────────────────────────────────────────
df = pd.read_csv('claims_data.csv', parse_dates=['claim_date'])
print(f"Loaded {len(df)} claims records")
print(df.dtypes)
print(df.head())

# ── DERIVED COLUMNS ───────────────────────────────────────────
df['claim_month'] = df['claim_date'].dt.to_period('M')

# ── CHART STYLE ───────────────────────────────────────────────
BLUE      = '#1F4E79'
MID_BLUE  = '#2E75B6'
LIGHT     = '#D6E4F0'
RED       = '#C00000'
GREEN     = '#375623'
GREY      = '#F2F2F2'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.facecolor': GREY,
    'figure.facecolor': 'white',
})

os.makedirs('charts', exist_ok=True)

# ── CHART 1 — Average Settlement Days by Claim Type ──────────
settled = df[df['status'] == 'Settled']
avg_days = settled.groupby('claim_type')['settlement_days'].mean().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(avg_days.index, avg_days.values, color=MID_BLUE, edgecolor='white', height=0.5)
for bar, val in zip(bars, avg_days.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f} days', va='center', fontsize=10, color=BLUE, fontweight='bold')
ax.set_xlabel('Average Days to Settlement', fontsize=10, color=BLUE)
ax.set_title('Average Settlement Time by Claim Type', fontsize=13, fontweight='bold', color=BLUE, pad=15)
ax.axvline(avg_days.mean(), color=RED, linestyle='--', linewidth=1.5, label=f'Overall avg: {avg_days.mean():.1f} days')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('charts/01_settlement_by_type.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 1 saved")

# ── CHART 2 — Total Claim Value by Region ────────────────────
regional = df.groupby('region')['claim_amount'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8, 4))
colors = [BLUE if i == 0 else MID_BLUE if i == 1 else LIGHT for i in range(len(regional))]
bars = ax.bar(regional.index, regional.values / 1000, color=colors, edgecolor='white', width=0.5)
for bar, val in zip(bars, regional.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'£{val/1000:.0f}K', ha='center', fontsize=10, color=BLUE, fontweight='bold')
ax.set_ylabel('Total Claim Value (£000s)', fontsize=10, color=BLUE)
ax.set_title('Total Claims Exposure by Region', fontsize=13, fontweight='bold', color=BLUE, pad=15)
plt.tight_layout()
plt.savefig('charts/02_exposure_by_region.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 2 saved")

# ── CHART 3 — Monthly Claims Volume Trend ───────────────────
monthly = df.groupby('claim_month').agg(
    volume=('claim_id', 'count'),
    total_value=('claim_amount', 'sum'),
    flagged=('fraud_flag', 'sum')
).reset_index()
monthly['month_str'] = monthly['claim_month'].astype(str)

fig, ax1 = plt.subplots(figsize=(9, 4))
ax2 = ax1.twinx()
ax1.bar(monthly['month_str'], monthly['volume'], color=LIGHT, edgecolor=MID_BLUE, width=0.5, label='Claim Volume')
ax2.plot(monthly['month_str'], monthly['total_value'] / 1000, color=BLUE, linewidth=2.5,
         marker='o', markersize=6, label='Total Value (£K)')
ax1.set_ylabel('Number of Claims', fontsize=10, color=MID_BLUE)
ax2.set_ylabel('Total Value (£000s)', fontsize=10, color=BLUE)
ax1.set_title('Monthly Claims Volume & Value Trend', fontsize=13, fontweight='bold', color=BLUE, pad=15)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)
plt.tight_layout()
plt.savefig('charts/03_monthly_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 3 saved")

# ── CHART 4 — Handler Performance Scorecard ─────────────────
handler = df.groupby('handler_id').agg(
    total=('claim_id', 'count'),
    avg_days=('settlement_days', 'mean'),
    disputed=('status', lambda x: (x == 'Disputed').sum()),
    settled=('status', lambda x: (x == 'Settled').sum())
).reset_index()
handler['settlement_rate'] = handler['settled'] / handler['total'] * 100

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].barh(handler['handler_id'], handler['avg_days'], color=MID_BLUE, edgecolor='white', height=0.4)
axes[0].set_title('Avg Settlement Days per Handler', fontsize=11, fontweight='bold', color=BLUE)
axes[0].set_xlabel('Days', fontsize=9)
for i, (val, hid) in enumerate(zip(handler['avg_days'], handler['handler_id'])):
    axes[0].text(val + 0.3, i, f'{val:.1f}d', va='center', fontsize=10, fontweight='bold', color=BLUE)

axes[1].barh(handler['handler_id'], handler['settlement_rate'], color=GREEN, edgecolor='white', height=0.4)
axes[1].set_title('Settlement Rate % per Handler', fontsize=11, fontweight='bold', color=BLUE)
axes[1].set_xlabel('Settlement Rate (%)', fontsize=9)
axes[1].set_xlim(0, 110)
for i, (val, hid) in enumerate(zip(handler['settlement_rate'], handler['handler_id'])):
    axes[1].text(val + 0.5, i, f'{val:.0f}%', va='center', fontsize=10, fontweight='bold', color=GREEN)

plt.suptitle('Handler Performance Scorecard', fontsize=13, fontweight='bold', color=BLUE, y=1.02)
plt.tight_layout()
plt.savefig('charts/04_handler_scorecard.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 4 saved")

# ── CHART 5 — Claims Status Breakdown + Fraud Flags ─────────
status_counts = df['status'].value_counts()
fraud_total = df['fraud_flag'].sum()
non_fraud = len(df) - fraud_total

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
colors_pie = [BLUE, MID_BLUE, LIGHT, '#C00000']
wedges, texts, autotexts = axes[0].pie(
    status_counts.values, labels=status_counts.index,
    autopct='%1.1f%%', colors=colors_pie[:len(status_counts)],
    startangle=90, pctdistance=0.75
)
for text in autotexts:
    text.set_fontsize(10)
    text.set_fontweight('bold')
axes[0].set_title('Claims by Status', fontsize=11, fontweight='bold', color=BLUE)

axes[1].bar(['No Flag', 'Fraud Flagged'], [non_fraud, fraud_total],
             color=[MID_BLUE, RED], edgecolor='white', width=0.4)
axes[1].set_title('Fraud Flag Distribution', fontsize=11, fontweight='bold', color=BLUE)
axes[1].set_ylabel('Number of Claims', fontsize=9)
for i, val in enumerate([non_fraud, fraud_total]):
    axes[1].text(i, val + 0.2, str(val), ha='center', fontsize=12, fontweight='bold',
                 color=BLUE if i == 0 else RED)

plt.suptitle('Claims Portfolio Overview', fontsize=13, fontweight='bold', color=BLUE, y=1.02)
plt.tight_layout()
plt.savefig('charts/05_portfolio_overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("Chart 5 saved")

# ── SUMMARY STATS ────────────────────────────────────────────
print("\n" + "="*50)
print("CLAIMS ANALYTICS SUMMARY")
print("="*50)
print(f"Total Claims:          {len(df)}")
print(f"Total Exposure:        £{df['claim_amount'].sum():,.0f}")
print(f"Avg Claim Value:       £{df['claim_amount'].mean():,.0f}")
print(f"Avg Settlement Days:   {df[df['status']=='Settled']['settlement_days'].mean():.1f}")
print(f"Settlement Rate:       {(df['status']=='Settled').mean()*100:.1f}%")
print(f"Fraud Flagged:         {df['fraud_flag'].sum()} ({df['fraud_flag'].mean()*100:.1f}%)")
print(f"Disputed Claims:       {(df['status']=='Disputed').sum()}")
print("="*50)
print("All charts saved to /charts/")
