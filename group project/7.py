import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import AutoMinorLocator

# Load the analysis results
results_df = pd.read_csv('hdi_fertility_analysis.csv')

# Highlight countries
highlight_countries = ['Saudi Arabia', 'Kuwait', 'Korea (Republic of)', 'Qatar']
highlighted = results_df[results_df['country'].isin(highlight_countries)].copy()

# ========================================
# 두 그래프 동일한 축 기준을 위한 글로벌 최소/최대값 계산
# ========================================
# GNI 최소/최대
gni_min = min(results_df['gni_before'].min(), results_df['gni_now'].min()) * 0.9
gni_max = max(results_df['gni_before'].max(), results_df['gni_now'].max()) * 1.05

# 출산율 최소/최대
fert_min = min(results_df['mean_fertility_before'].min(), results_df['most_recent_fertility'].min()) * 0.9
fert_max = max(results_df['mean_fertility_before'].max(), results_df['most_recent_fertility'].max()) * 1.05


# ========================================
# FIGURE 1: BEFORE DEVELOPED STATUS
# ========================================

fig1, ax1 = plt.subplots(figsize=(18, 11))

# Plot ALL "BEFORE" points
ax1.scatter(
    results_df['gni_before'],
    results_df['mean_fertility_before'],
    color='#E74C3C',
    s=350,
    alpha=0.7,
    edgecolors='black',
    linewidth=2,
    zorder=3,
    label='Before Developed Status'
)

# Highlight the 4 special countries
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_before']):
        country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
        
        # 한국만 라벨을 x축에 밀착 (0.05cm 갭 느낌)
        if row['country'] == 'Korea (Republic of)':
            txt_x = row['gni_before']
            # y축 최하단(fert_min)에서 0.5%만 띄움
            txt_y = fert_min + (fert_max - fert_min) * 0.005 
            t_coords = 'data'
            ha_align = 'center'
            va_align = 'bottom' # 라벨 박스의 밑바닥이 txt_y에 닿도록 설정
        else:
            txt_x = 40
            txt_y = 40
            t_coords = 'offset points'
            ha_align = 'left'
            va_align = 'center'
            
        ax1.annotate(
            country_display,
            xy=(row['gni_before'], row['mean_fertility_before']),
            xytext=(txt_x, txt_y), 
            textcoords=t_coords,
            fontsize=18,
            fontweight='bold',
            color='#C0392B',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#FADBD8', 
                     edgecolor='#E74C3C', linewidth=2.5, alpha=0.95),
            arrowprops=dict(arrowstyle='-', color='#C0392B', lw=2, alpha=0.8),
            zorder=7,
            ha=ha_align,
            va=va_align
        )

# Add reference line
ax1.axhline(y=2.1, color='green', linestyle='--', linewidth=3, 
           alpha=0.7, label='Replacement Level (2.1)', zorder=0)

# Styling
ax1.set_xlim(gni_min, gni_max)
ax1.set_ylim(fert_min, fert_max)

ax1.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=22, fontweight='bold', labelpad=15)
ax1.set_ylabel('Total Fertility Rate (births per woman)', fontsize=22, fontweight='bold', labelpad=15)
ax1.set_title('Fertility BEFORE Developed Status (HDI < 0.800)',
             fontsize=26, fontweight='bold', pad=30)

# Format x-axis
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
ax1.tick_params(axis='both', which='major', labelsize=18)

# Add 2.1 to y-axis ticks
y_ticks = list(ax1.get_yticks())
if 2.1 not in y_ticks:
    y_ticks.append(2.1)
    y_ticks.sort()
    ax1.set_yticks(y_ticks)

y_tick_labels = ax1.get_yticklabels()
for label in y_tick_labels:
    if '2.1' in label.get_text():
        label.set_color('green')
        label.set_fontweight('bold')
        label.set_fontsize(18)

# Compact Grid
ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
ax1.grid(True, which='major', alpha=0.4, linestyle='-', linewidth=1.0, color='gray')
ax1.grid(True, which='minor', alpha=0.2, linestyle='--', linewidth=0.5, color='gray')
ax1.set_axisbelow(True)

ax1.legend(loc='upper right', fontsize=18, frameon=True, shadow=True, fancybox=True, framealpha=0.95)

# Background
ax1.set_facecolor('#F8F9FA')
fig1.patch.set_facecolor('white')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('fertility_before_developed.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Figure 1 saved as 'fertility_before_developed.png'")


# ========================================
# FIGURE 2: CURRENT STATUS
# ========================================

fig2, ax2 = plt.subplots(figsize=(18, 11))

# Plot ALL "CURRENT" points
ax2.scatter(
    results_df['gni_now'],
    results_df['most_recent_fertility'],
    color='#3498DB',
    s=350,
    alpha=0.8,
    edgecolors='black',
    linewidth=2,
    zorder=4,
    label='Current Status'
)

# Highlight the 4 special countries
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_now']):
        country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
        
        # 한국만 라벨을 x축에 밀착 (0.05cm 갭 느낌)
        if row['country'] == 'Korea (Republic of)':
            txt_x = row['gni_now']
            # y축 최하단(fert_min)에서 0.5%만 띄움
            txt_y = fert_min + (fert_max - fert_min) * 0.005
            t_coords = 'data'
            ha_align = 'center'
            va_align = 'bottom' # 라벨 박스의 밑바닥이 txt_y에 닿도록 설정
        else:
            txt_x = 40
            txt_y = 40
            t_coords = 'offset points'
            ha_align = 'left'
            va_align = 'center'
            
        ax2.annotate(
            country_display,
            xy=(row['gni_now'], row['most_recent_fertility']),
            xytext=(txt_x, txt_y), 
            textcoords=t_coords,
            fontsize=18,
            fontweight='bold',
            color='#1F618D',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#D6EAF8', 
                     edgecolor='#3498DB', linewidth=2.5, alpha=0.95),
            arrowprops=dict(arrowstyle='-', color='#1F618D', lw=2, alpha=0.8),
            zorder=7,
            ha=ha_align,
            va=va_align
        )

# Add reference line
ax2.axhline(y=2.1, color='green', linestyle='--', linewidth=3, 
           alpha=0.7, label='Replacement Level (2.1)', zorder=0)

# Styling
ax2.set_xlim(gni_min, gni_max)
ax2.set_ylim(fert_min, fert_max)

ax2.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=22, fontweight='bold', labelpad=15)
ax2.set_ylabel('Total Fertility Rate (births per woman)', fontsize=22, fontweight='bold', labelpad=15)
ax2.set_title('Fertility in CURRENT Developed Countries (HDI ≥ 0.800)',
             fontsize=26, fontweight='bold', pad=30)

# Format x-axis
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
ax2.tick_params(axis='both', which='major', labelsize=18)

# Add 2.1 to y-axis ticks
y_ticks2 = list(ax2.get_yticks())
if 2.1 not in y_ticks2:
    y_ticks2.append(2.1)
    y_ticks2.sort()
    ax2.set_yticks(y_ticks2)

y_tick_labels2 = ax2.get_yticklabels()
for label in y_tick_labels2:
    if '2.1' in label.get_text():
        label.set_color('green')
        label.set_fontweight('bold')
        label.set_fontsize(18)

# Compact Grid
ax2.xaxis.set_minor_locator(AutoMinorLocator(2))
ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
ax2.grid(True, which='major', alpha=0.4, linestyle='-', linewidth=1.0, color='gray')
ax2.grid(True, which='minor', alpha=0.2, linestyle='--', linewidth=0.5, color='gray')
ax2.set_axisbelow(True)

ax2.legend(loc='upper right', fontsize=18, frameon=True, shadow=True, fancybox=True, framealpha=0.95)

# Background
ax2.set_facecolor('#F8F9FA')
fig2.patch.set_facecolor('white')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('fertility_current_developed.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Figure 2 saved as 'fertility_current_developed.png'")

plt.show()