import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.patches import FancyArrowPatch
import numpy as np
import os

df = pd.read_csv('/home/claude/claims-operational-analytics/claims_data.csv', parse_dates=['claim_date'])
df['claim_month'] = df['claim_date'].dt.to_period('M')
os.makedirs('/home/claude/claims-operational-analytics/charts', exist_ok=True)

# ── PALETTE ───────────────────────────────────────────────────
C1  = '#1F4E79'   # dark navy
C2  = '#2E75B6'   # mid blue
C3  = '#5BA3D9'   # light blue
C4  = '#D6E4F0'   # pale blue
RED = '#C00000'
GRN = '#2D6A2D'
WHT = '#FFFFFF'
GRY = '#F7F9FC'
LGR = '#E8EDF2'

def base_style(fig, ax):
    fig.patch.set_facecolor(WHT)
    ax.set_facecolor(GRY)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.tick_params(colors='#555555', labelsize=9)
    ax.yaxis.label.set_color('#555555')
    ax.xaxis.label.set_color('#555555')

def add_titles(ax, title, subtitle, color=C1):
    ax.set_title(title, fontsize=14, fontweight='bold', color=color, pad=18, loc='left')
    ax.annotate(subtitle, xy=(0, 1.04), xycoords='axes fraction',
                fontsize=9, color='#666666', style='italic')

def watermark(ax):
    ax.annotate('Anandi M | MSc Data Science, University of Bath',
                xy=(1, 0), xycoords='axes fraction',
                fontsize=7, color='#AAAAAA', ha='right', va='bottom')

# ═══════════════════════════════════════════════════════════════
# CHART 1 — Settlement Time by Claim Type
# ═══════════════════════════════════════════════════════════════
settled = df[df['status'] == 'Settled']
avg_days = settled.groupby('claim_type')['settlement_days'].mean().sort_values()
overall  = avg_days.mean()

fig, ax = plt.subplots(figsize=(10, 4.5))
fig.patch.set_facecolor(WHT)
ax.set_facecolor(GRY)

colors = [C4, C2, C1]
bars = ax.barh(avg_days.index, avg_days.values, color=colors,
               edgecolor=WHT, height=0.45, zorder=3)

# value labels
for bar, val in zip(bars, avg_days.values):
    ax.text(val + 0.6, bar.get_y() + bar.get_height()/2,
            f'{val:.1f} days', va='center', ha='left',
            fontsize=10, fontweight='bold', color=C1)

# average line
ax.axvline(overall, color=RED, linestyle='--', linewidth=1.8, zorder=4,
           label=f'Overall avg: {overall:.1f} days')

# annotate Health
ax.annotate('4.6× slower\nthan Motor',
            xy=(avg_days['Health'], 2),
            xytext=(38, 1.55),
            fontsize=8, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

ax.set_xlabel('Average Days to Settlement', fontsize=10)
ax.set_xlim(0, 56)
ax.xaxis.set_major_locator(mticker.MultipleLocator(10))
ax.grid(axis='x', color='#DDDDDD', linewidth=0.7, zorder=0)
ax.legend(fontsize=9, framealpha=0)

for spine in ['top','right']:
    ax.spines[spine].set_visible(False)
for spine in ['left','bottom']:
    ax.spines[spine].set_color('#CCCCCC')
ax.tick_params(colors='#555555', labelsize=10)

add_titles(ax, 'Average Settlement Time by Claim Type',
           'Health claims take 45.5 days on average — 4.6× longer than Motor. Both Home and Health breach the 30-day SLA threshold.')
watermark(ax)
plt.tight_layout()
plt.savefig('/home/claude/claims-operational-analytics/charts/01_settlement_by_type.png',
            dpi=180, bbox_inches='tight', facecolor=WHT)
plt.close()
print("Chart 1 done")

# ═══════════════════════════════════════════════════════════════
# CHART 2 — Total Claims Exposure by Region
# ═══════════════════════════════════════════════════════════════
regional = df.groupby('region').agg(
    total=('claim_amount','sum'),
    count=('claim_id','count'),
    disputed=('status', lambda x: (x=='Disputed').sum())
).sort_values('total', ascending=False).reset_index()
regional['dispute_rate'] = regional['disputed']/regional['count']*100

fig, ax = plt.subplots(figsize=(10, 4.5))
fig.patch.set_facecolor(WHT)
ax.set_facecolor(GRY)

bar_colors = [C1, C2, C3, C4]
bars = ax.bar(regional['region'], regional['total']/1000,
              color=bar_colors, edgecolor=WHT, width=0.45, zorder=3)

for bar, row in zip(bars, regional.itertuples()):
    # value label
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5,
            f'£{row.total/1000:.0f}K', ha='center', fontsize=10,
            fontweight='bold', color=C1)
    # dispute rate label
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()/2,
            f'{row.dispute_rate:.0f}%\ndisputed',
            ha='center', va='center', fontsize=8,
            color=WHT if row.total > 150000 else C1, fontweight='bold')

# highlight Leeds
ax.annotate('Highest\ndispute rate',
            xy=(2, regional[regional['region']=='Leeds']['total'].values[0]/1000),
            xytext=(2.6, 70),
            fontsize=8, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))

ax.set_ylabel('Total Claim Value (£000s)', fontsize=10)
ax.set_ylim(0, 265)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'£{x:.0f}K'))
ax.grid(axis='y', color='#DDDDDD', linewidth=0.7, zorder=0)
for spine in ['top','right']:
    ax.spines[spine].set_visible(False)
for spine in ['left','bottom']:
    ax.spines[spine].set_color('#CCCCCC')
ax.tick_params(colors='#555555', labelsize=10)

add_titles(ax, 'Total Claims Exposure by Region',
           'London carries 44% of total exposure (£215K). Leeds has the highest dispute rate despite lower volume — a quality signal worth investigating.')
watermark(ax)
plt.tight_layout()
plt.savefig('/home/claude/claims-operational-analytics/charts/02_exposure_by_region.png',
            dpi=180, bbox_inches='tight', facecolor=WHT)
plt.close()
print("Chart 2 done")

# ═══════════════════════════════════════════════════════════════
# CHART 3 — Monthly Claims Volume & Value Trend
# ═══════════════════════════════════════════════════════════════
monthly = df.groupby('claim_month').agg(
    volume=('claim_id','count'),
    total_value=('claim_amount','sum'),
    flagged=('fraud_flag','sum')
).reset_index()
monthly['month_str'] = monthly['claim_month'].astype(str)
x = np.arange(len(monthly))

fig, ax1 = plt.subplots(figsize=(10, 4.5))
fig.patch.set_facecolor(WHT)
ax1.set_facecolor(GRY)
ax2 = ax1.twinx()

ax1.bar(x, monthly['volume'], color=C4, edgecolor=C2,
        width=0.45, zorder=3, label='Claim Volume', linewidth=1.2)
ax2.plot(x, monthly['total_value']/1000, color=C1, linewidth=2.5,
         marker='o', markersize=8, markerfacecolor=WHT,
         markeredgecolor=C1, markeredgewidth=2, zorder=4, label='Total Value (£K)')

# value labels on line
for i, (xi, val) in enumerate(zip(x, monthly['total_value'])):
    ax2.text(xi, val/1000+1.5, f'£{val/1000:.0f}K',
             ha='center', fontsize=8.5, fontweight='bold', color=C1)

# volume labels on bars
for i, (xi, vol) in enumerate(zip(x, monthly['volume'])):
    ax1.text(xi, vol+0.1, str(vol), ha='center', fontsize=9,
             fontweight='bold', color=C2)

ax1.set_xticks(x)
ax1.set_xticklabels(['Jan 2024','Feb 2024','Mar 2024','Apr 2024'], fontsize=10)
ax1.set_ylabel('Number of Claims', fontsize=10, color=C2)
ax2.set_ylabel('Total Value (£000s)', fontsize=10, color=C1)
ax1.set_ylim(0, 14)
ax2.set_ylim(100, 155)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(2))
ax1.grid(axis='y', color='#DDDDDD', linewidth=0.7, zorder=0)

for spine in ['top']:
    ax1.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)
ax1.spines['left'].set_color('#CCCCCC')
ax1.spines['bottom'].set_color('#CCCCCC')
ax2.spines['right'].set_color('#CCCCCC')
ax1.tick_params(colors='#555555')
ax2.tick_params(colors='#555555')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc='upper left',
           fontsize=9, framealpha=0.9, edgecolor='#CCCCCC')

add_titles(ax1, 'Monthly Claims Volume & Value Trend',
           'Volume stabilised at 10 claims/month from Feb–Apr. March peak (£144K) driven by high-value Health and Home claims.')
watermark(ax1)
plt.tight_layout()
plt.savefig('/home/claude/claims-operational-analytics/charts/03_monthly_trend.png',
            dpi=180, bbox_inches='tight', facecolor=WHT)
plt.close()
print("Chart 3 done")

# ═══════════════════════════════════════════════════════════════
# CHART 4 — Handler Performance Scorecard
# ═══════════════════════════════════════════════════════════════
handler = df.groupby('handler_id').agg(
    total=('claim_id','count'),
    avg_days=('settlement_days','mean'),
    disputed=('status', lambda x: (x=='Disputed').sum()),
    settled=('status',  lambda x: (x=='Settled').sum())
).reset_index()
handler['settlement_rate'] = handler['settled']/handler['total']*100
handler = handler.sort_values('avg_days')

fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
fig.patch.set_facecolor(WHT)

# subplot 1 — avg days
ax = axes[0]
ax.set_facecolor(GRY)
colors_h = [GRN if r == handler['avg_days'].min() else C2 for r in handler['avg_days']]
bars = ax.barh(handler['handler_id'], handler['avg_days'],
               color=colors_h, edgecolor=WHT, height=0.4, zorder=3)
for bar, val in zip(bars, handler['avg_days']):
    ax.text(val+0.4, bar.get_y()+bar.get_height()/2,
            f'{val:.1f}d', va='center', fontsize=10,
            fontweight='bold', color=C1)
ax.set_xlabel('Avg Days to Settle', fontsize=9)
ax.set_title('Settlement Speed', fontsize=11, fontweight='bold', color=C1, pad=10)
ax.set_xlim(0, 42)
ax.grid(axis='x', color='#DDDDDD', linewidth=0.7, zorder=0)
best_patch = mpatches.Patch(color=GRN, label='Fastest handler')
ax.legend(handles=[best_patch], fontsize=8, framealpha=0)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
for sp in ['left','bottom']: ax.spines[sp].set_color('#CCCCCC')
ax.tick_params(colors='#555555', labelsize=10)

# subplot 2 — settlement rate
ax = axes[1]
ax.set_facecolor(GRY)
colors_s = [GRN if r == handler['settlement_rate'].max() else C2 for r in handler['settlement_rate']]
bars = ax.barh(handler['handler_id'], handler['settlement_rate'],
               color=colors_s, edgecolor=WHT, height=0.4, zorder=3)
for bar, val in zip(bars, handler['settlement_rate']):
    ax.text(val+0.5, bar.get_y()+bar.get_height()/2,
            f'{val:.0f}%', va='center', fontsize=10,
            fontweight='bold', color=C1)
ax.set_xlabel('Settlement Rate (%)', fontsize=9)
ax.set_title('Settlement Rate', fontsize=11, fontweight='bold', color=C1, pad=10)
ax.set_xlim(0, 110)
ax.grid(axis='x', color='#DDDDDD', linewidth=0.7, zorder=0)
best_patch2 = mpatches.Patch(color=GRN, label='Best performer')
ax.legend(handles=[best_patch2], fontsize=8, framealpha=0)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
for sp in ['left','bottom']: ax.spines[sp].set_color('#CCCCCC')
ax.tick_params(colors='#555555', labelsize=10)

# subplot 3 — disputed claims
ax = axes[2]
ax.set_facecolor(GRY)
colors_d = [RED if r > 0 else C4 for r in handler['disputed']]
bars = ax.barh(handler['handler_id'], handler['disputed'],
               color=colors_d, edgecolor=WHT, height=0.4, zorder=3)
for bar, val in zip(bars, handler['disputed']):
    ax.text(val+0.04, bar.get_y()+bar.get_height()/2,
            str(int(val)), va='center', fontsize=10,
            fontweight='bold', color=C1)
ax.set_xlabel('Number of Disputed Claims', fontsize=9)
ax.set_title('Disputed Claims', fontsize=11, fontweight='bold', color=C1, pad=10)
ax.set_xlim(0, 4)
ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
ax.grid(axis='x', color='#DDDDDD', linewidth=0.7, zorder=0)
for sp in ['top','right']: ax.spines[sp].set_visible(False)
for sp in ['left','bottom']: ax.spines[sp].set_color('#CCCCCC')
ax.tick_params(colors='#555555', labelsize=10)

fig.suptitle('Handler Performance Scorecard', fontsize=14, fontweight='bold',
             color=C1, x=0.02, ha='left', y=1.02)
fig.text(0.02, 0.97, 'H01 fastest to settle (28.7d). H02 highest settlement rate (85%). H03 most disputed — review caseload mix.',
         fontsize=9, color='#666666', style='italic')
fig.text(0.99, -0.02, 'Anandi M | MSc Data Science, University of Bath',
         fontsize=7, color='#AAAAAA', ha='right')

plt.tight_layout()
plt.savefig('/home/claude/claims-operational-analytics/charts/04_handler_scorecard.png',
            dpi=180, bbox_inches='tight', facecolor=WHT)
plt.close()
print("Chart 4 done")

# ═══════════════════════════════════════════════════════════════
# CHART 5 — Portfolio Overview
# ═══════════════════════════════════════════════════════════════
status_counts = df['status'].value_counts()
fraud_by_type = df.groupby('claim_type')['fraud_flag'].sum().sort_values(ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
fig.patch.set_facecolor(WHT)

# LEFT — donut chart (much more professional than pie)
ax = axes[0]
ax.set_facecolor(WHT)
pie_colors = [C1, C2, C3]
wedges, texts, autotexts = ax.pie(
    status_counts.values,
    labels=None,
    autopct='%1.0f%%',
    colors=pie_colors,
    startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor=WHT, linewidth=2)
)
for at in autotexts:
    at.set_fontsize(11)
    at.set_fontweight('bold')
    at.set_color(WHT)

# centre label
ax.text(0, 0, f'{len(df)}\nClaims', ha='center', va='center',
        fontsize=12, fontweight='bold', color=C1)

legend_labels = [f'{k}: {v} ({v/len(df)*100:.0f}%)' for k,v in status_counts.items()]
ax.legend(wedges, legend_labels, loc='lower center', fontsize=9,
          framealpha=0, bbox_to_anchor=(0.5, -0.12), ncol=1)
ax.set_title('Claims by Status', fontsize=11, fontweight='bold', color=C1, pad=10)

# RIGHT — fraud flags by claim type
ax = axes[1]
ax.set_facecolor(GRY)
bar_colors = [RED if v > 0 else C4 for v in fraud_by_type.values]
bars = ax.bar(fraud_by_type.index, fraud_by_type.values,
              color=bar_colors, edgecolor=WHT, width=0.4, zorder=3)
for bar, val in zip(bars, fraud_by_type.values):
    if val > 0:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05,
                f'{int(val)} flagged', ha='center', fontsize=9.5,
                fontweight='bold', color=RED)
    else:
        ax.text(bar.get_x()+bar.get_width()/2, 0.05,
                'None', ha='center', fontsize=9, color='#888888', va='bottom')

ax.set_ylabel('Fraud-Flagged Claims', fontsize=10)
ax.set_ylim(0, 5.5)
ax.yaxis.set_major_locator(mticker.MultipleLocator(1))
ax.set_title('Fraud Flags by Claim Type', fontsize=11, fontweight='bold', color=C1, pad=10)
ax.grid(axis='y', color='#DDDDDD', linewidth=0.7, zorder=0)
ax.annotate('100% of fraud flags\nin Health & Home\n— Motor = zero flags',
            xy=(0.5, 3), xytext=(1.5, 3.8),
            fontsize=8, color=RED, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
for sp in ['top','right']: ax.spines[sp].set_visible(False)
for sp in ['left','bottom']: ax.spines[sp].set_color('#CCCCCC')
ax.tick_params(colors='#555555', labelsize=10)

fig.suptitle('Claims Portfolio Overview', fontsize=14, fontweight='bold',
             color=C1, x=0.02, ha='left', y=1.02)
fig.text(0.02, 0.97, '75% of claims settled. 6 fraud-flagged claims (15%) — all in Health and Home. Motor has zero fraud flags across all 40 claims.',
         fontsize=9, color='#666666', style='italic')
fig.text(0.99, -0.02, 'Anandi M | MSc Data Science, University of Bath',
         fontsize=7, color='#AAAAAA', ha='right')

plt.tight_layout()
plt.savefig('/home/claude/claims-operational-analytics/charts/05_portfolio_overview.png',
            dpi=180, bbox_inches='tight', facecolor=WHT)
plt.close()
print("Chart 5 done")
print("\nAll 5 charts rebuilt ✅")
