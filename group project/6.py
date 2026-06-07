import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the analysis results
results_df = pd.read_csv('hdi_fertility_analysis.csv')

# Highlight countries
highlight_countries = ['Saudi Arabia', 'Kuwait', 'Korea (Republic of)', 'Qatar']
highlighted = results_df[results_df['country'].isin(highlight_countries)].copy()

# ========================================
# FIGURE 1: BEFORE DEVELOPED STATUS
# ========================================

fig1, ax1 = plt.subplots(figsize=(18, 11))

# Plot ALL "BEFORE" points (red only)
ax1.scatter(
    results_df['gni_before'],
    results_df['mean_fertility_before'],
    color='#E74C3C',
    s=300,
    alpha=0.7,
    edgecolors='black',
    linewidth=2,
    zorder=3
)

# Highlight the 4 special countries with labels
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_before']):
        country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
        
        ax1.annotate(
            country_display,
            xy=(row['gni_before'], row['mean_fertility_before']),
            xytext=(15, 10),
            textcoords='offset points',
            fontsize=14,
            fontweight='bold',
            color='#C0392B',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#FADBD8', 
                     edgecolor='#E74C3C', linewidth=2.5, alpha=0.95),
            arrowprops=dict(arrowstyle='->', color='#C0392B', lw=2),
            zorder=7
        )

# Add reference line
ax1.axhline(y=2.1, color='green', linestyle='--', linewidth=3, 
           alpha=0.7, label='Replacement Level (2.1)', zorder=0)

# Styling
ax1.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=20, fontweight='bold', labelpad=15)
ax1.set_ylabel('Total Fertility Rate (births per woman)', fontsize=20, fontweight='bold', labelpad=15)
ax1.set_title('Fertility BEFORE Developed Status (HDI < 0.800)',
             fontsize=24, fontweight='bold', pad=30)

# Format x-axis
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Increase tick label size
ax1.tick_params(axis='both', which='major', labelsize=16)

# Add 2.1 to y-axis ticks and color it green
y_ticks = list(ax1.get_yticks())
if 2.1 not in y_ticks:
    y_ticks.append(2.1)
    y_ticks.sort()
    ax1.set_yticks(y_ticks)

# Color the 2.1 tick label green
y_tick_labels = ax1.get_yticklabels()
for label in y_tick_labels:
    if '2.1' in label.get_text():
        label.set_color('green')
        label.set_fontweight('bold')
        label.set_fontsize(16)

# Grid
ax1.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, color='gray')
ax1.set_axisbelow(True)

# Legend
legend1 = ax1.legend(
    loc='upper right', 
    fontsize=16, 
    frameon=True, 
    shadow=True,
    fancybox=True,
    framealpha=0.95
)

# Caption
plt.figtext(
    0.99, 0.01, 
    'Source: UNDP Human Development Report & World Bank | HDI threshold: 0.800',
    ha='right', 
    fontsize=12, 
    style='italic', 
    color='#34495E',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
)

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

# Plot ALL "CURRENT" points (blue only)
ax2.scatter(
    results_df['gni_now'],
    results_df['most_recent_fertility'],
    color='#3498DB',
    s=300,
    alpha=0.8,
    edgecolors='black',
    linewidth=2,
    zorder=4
)

# Highlight the 4 special countries with labels
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_now']):
        country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
        
        ax2.annotate(
            country_display,
            xy=(row['gni_now'], row['most_recent_fertility']),
            xytext=(15, 10),
            textcoords='offset points',
            fontsize=14,
            fontweight='bold',
            color='#1F618D',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='#D6EAF8', 
                     edgecolor='#3498DB', linewidth=2.5, alpha=0.95),
            arrowprops=dict(arrowstyle='->', color='#1F618D', lw=2),
            zorder=7
        )

# Add reference line
ax2.axhline(y=2.1, color='green', linestyle='--', linewidth=3, 
           alpha=0.7, label='Replacement Level (2.1)', zorder=0)

# Styling
ax2.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=20, fontweight='bold', labelpad=15)
ax2.set_ylabel('Total Fertility Rate (births per woman)', fontsize=20, fontweight='bold', labelpad=15)
ax2.set_title('Fertility in CURRENT Developed Countries (HDI ≥ 0.800)',
             fontsize=24, fontweight='bold', pad=30)

# Format x-axis
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Increase tick label size
ax2.tick_params(axis='both', which='major', labelsize=16)

# Add 2.1 to y-axis ticks and color it green
y_ticks = list(ax2.get_yticks())
if 2.1 not in y_ticks:
    y_ticks.append(2.1)
    y_ticks.sort()
    ax2.set_yticks(y_ticks)

# Color the 2.1 tick label green
y_tick_labels = ax2.get_yticklabels()
for label in y_tick_labels:
    if '2.1' in label.get_text():
        label.set_color('green')
        label.set_fontweight('bold')
        label.set_fontsize(16)

# Grid
ax2.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, color='gray')
ax2.set_axisbelow(True)

# Legend
legend2 = ax2.legend(
    loc='upper right', 
    fontsize=16, 
    frameon=True, 
    shadow=True,
    fancybox=True,
    framealpha=0.95
)

# Caption
plt.figtext(
    0.99, 0.01, 
    'Source: UNDP Human Development Report & World Bank | HDI threshold: 0.800',
    ha='right', 
    fontsize=12, 
    style='italic', 
    color='#34495E',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
)

# Background
ax2.set_facecolor('#F8F9FA')
fig2.patch.set_facecolor('white')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('fertility_current_developed.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Figure 2 saved as 'fertility_current_developed.png'")

# ========================================
# FIGURE 3: TRANSITION (4 HIGHLIGHTED COUNTRIES)
# ========================================

fig3, ax3 = plt.subplots(figsize=(18, 11))

# Plot BEFORE points for highlighted countries only
ax3.scatter(
    highlighted['gni_before'],
    highlighted['mean_fertility_before'],
    color='#E74C3C',
    s=350,
    alpha=0.7,
    edgecolors='black',
    linewidth=2.5,
    zorder=3,
    label='Before Developed Status'
)

# Plot CURRENT points for highlighted countries only
ax3.scatter(
    highlighted['gni_now'],
    highlighted['most_recent_fertility'],
    color='#3498DB',
    s=350,
    alpha=0.8,
    edgecolors='black',
    linewidth=2.5,
    zorder=4,
    label='Current Status'
)

# Draw STRAIGHT arrows for highlighted countries
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_before']) and pd.notna(row['gni_now']):
        ax3.annotate(
            '',
            xy=(row['gni_now'], row['most_recent_fertility']),
            xytext=(row['gni_before'], row['mean_fertility_before']),
            arrowprops=dict(
                arrowstyle='-|>',
                color='#E74C3C',
                alpha=0.8,
                linewidth=4,
                shrinkA=10,
                shrinkB=10
            ),
            zorder=6
        )

# Add labels with country name AND decline amount
for _, row in highlighted.iterrows():
    country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
    decline_amount = abs(row['fertility_change'])
    
    label_text = f"{country_display}\n(↓ {decline_amount:.2f})"
    
    # Calculate midpoint of the line
    mid_x = (row['gni_before'] + row['gni_now']) / 2
    mid_y = (row['mean_fertility_before'] + row['most_recent_fertility']) / 2
    
    # Custom positioning for each country
    if row['country'] == 'Saudi Arabia':
        label_x = mid_x
        label_y = mid_y
        xytext = (0, 0)
        ha = 'center'
    elif row['country'] == 'Kuwait':
        label_x = mid_x
        label_y = 1.95
        xytext = (0, 0)
        ha = 'center'
    elif row['country'] == 'Korea (Republic of)':
        label_x = mid_x
        label_y = 0.85
        xytext = (0, 0)
        ha = 'center'
    elif row['country'] == 'Qatar':
        label_x = mid_x
        label_y = 2.25
        xytext = (0, 0)
        ha = 'center'
    else:
        label_x = row['gni_now']
        label_y = row['most_recent_fertility']
        xytext = (15, 10)
        ha = 'left'
    
    ax3.annotate(
        label_text,
        xy=(label_x, label_y),
        xytext=xytext,
        textcoords='offset points',
        fontsize=14,
        fontweight='bold',
        color='#C0392B',
        alpha=1.0,
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#FADBD8', 
                 edgecolor='#E74C3C', linewidth=2.5, alpha=0.95),
        zorder=7,
        ha=ha
    )

# Add reference line
ax3.axhline(y=2.1, color='green', linestyle='--', linewidth=3, 
           alpha=0.7, label='Replacement Level (2.1)', zorder=0)

# Styling
ax3.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=20, fontweight='bold', labelpad=15)
ax3.set_ylabel('Total Fertility Rate (births per woman)', fontsize=20, fontweight='bold', labelpad=15)
ax3.set_title('Fertility Transition: Saudi Arabia, Kuwait, South Korea, Qatar',
             fontsize=24, fontweight='bold', pad=30)

# Format x-axis
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Increase tick label size
ax3.tick_params(axis='both', which='major', labelsize=16)

# Add 2.1 to y-axis ticks and color it green
y_ticks = list(ax3.get_yticks())
if 2.1 not in y_ticks:
    y_ticks.append(2.1)
    y_ticks.sort()
    ax3.set_yticks(y_ticks)

# Color the 2.1 tick label green
y_tick_labels = ax3.get_yticklabels()
for label in y_tick_labels:
    if '2.1' in label.get_text():
        label.set_color('green')
        label.set_fontweight('bold')
        label.set_fontsize(16)

# Grid
ax3.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, color='gray')
ax3.set_axisbelow(True)

# Legend
legend3 = ax3.legend(
    loc='upper right', 
    fontsize=16, 
    frameon=True, 
    shadow=True,
    fancybox=True,
    framealpha=0.95
)

# Caption
plt.figtext(
    0.99, 0.01, 
    'Source: UNDP Human Development Report & World Bank | HDI threshold: 0.800',
    ha='right', 
    fontsize=12, 
    style='italic', 
    color='#34495E',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
)

# Background
ax3.set_facecolor('#F8F9FA')
fig3.patch.set_facecolor('white')

plt.tight_layout(rect=[0, 0.03, 1, 1])
plt.savefig('fertility_transition_highlighted.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Figure 3 saved as 'fertility_transition_highlighted.png'")

plt.show()

print("\n" + "="*70)
print("=== ALL 3 FIGURES CREATED ===")
print("="*70)
print("\n1. fertility_before_developed.png - All countries BEFORE developed status")
print("2. fertility_current_developed.png - All countries CURRENT status")
print("3. fertility_transition_highlighted.png - 4 highlighted countries with transitions")
print("\nChanges made:")
print("  ✓ Increased all label sizes (axis labels, tick labels, legend)")
print("  ✓ Removed key statistics box")
print("  ✓ Changed arrows to straight (removed curves)")
print("  ✓ Created 3 separate figures instead of 1 combined plot")
print("  ✓ Removed shape differentiation (color only)")
print("="*70)
