# ========================================
# FIND TRANSITION TO DEVELOPED STATUS USING HDI
# For Excel file with header rows
# ========================================

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# ========================================
# STEP 1: LOAD HDI DATA WITH MULTI-ROW HEADER
# ========================================

# Read first few rows to understand structure
preview = pd.read_excel("hdi_data.xlsx", nrows=5)
print("=== Preview of Excel file ===")
print(preview)

# The actual structure has years in row 2, so we need to read with header=[0,1,2]
# But let's try a simpler approach: read raw and manually assign column names

# Read without header first
hdi_raw_no_header = pd.read_excel("hdi_data.xlsx", header=None)

print("\n=== First 5 rows (no header) ===")
print(hdi_raw_no_header.head(5))

# Find the row with years (1990, 2000, 2010, etc.)
year_row_idx = None
for idx in range(min(10, len(hdi_raw_no_header))):
    row = hdi_raw_no_header.iloc[idx]
    # Check if this row contains years
    year_count = sum(1 for val in row if str(val).strip() in ['1990', '2000', '2010', '2015', '2020', '2021', '2022', '2023'])
    if year_count >= 3:  # If we find at least 3 years
        year_row_idx = idx
        print(f"\n✓ Found year row at index {idx}")
        print(f"Year row: {row.tolist()}")
        break

if year_row_idx is None:
    print("\n❌ Could not find year row. Trying alternative method...")
    # Use header=3 and manually map columns
    hdi_raw = pd.read_excel("hdi_data.xlsx", header=3)
    
    # Manually assign year columns based on position
    # Typically: Col 0=Rank, Col 1=Country, Col 2=1990, Col 4=2000, Col 6=2010, etc.
    year_columns = {
        2: 1990,   # Column index 2 = 1990
        4: 2000,   # Column index 4 = 2000
        6: 2010,   # Column index 6 = 2010
        8: 2015,   # Column index 8 = 2015
        10: 2020,  # Column index 10 = 2020
        12: 2021,  # Column index 12 = 2021
        14: 2022,  # Column index 14 = 2022
        16: 2023   # Column index 16 = 2023
    }
    
    # Rename columns
    new_columns = {}
    for col_idx, year in year_columns.items():
        if col_idx < len(hdi_raw.columns):
            new_columns[hdi_raw.columns[col_idx]] = year
    
    # Also rename country column
    new_columns[hdi_raw.columns[1]] = 'Country'
    
    hdi_raw = hdi_raw.rename(columns=new_columns)
    
    print("\n=== Renamed columns ===")
    print(hdi_raw.columns.tolist())
    
else:
    # Read data starting from the row after years
    hdi_raw = pd.read_excel("hdi_data.xlsx", header=year_row_idx)
    
    # Clean column names (remove extra spaces)
    hdi_raw.columns = [str(col).strip() for col in hdi_raw.columns]

print("\n=== HDI Data Loaded ===")
print(f"Shape: {hdi_raw.shape}")
print("\nColumn names:")
print(hdi_raw.columns.tolist())
print("\nFirst few rows:")
print(hdi_raw.head(10))

# ========================================
# STEP 2: IDENTIFY COLUMNS
# ========================================

# Find country column
country_col = None
for col in hdi_raw.columns:
    if 'country' in str(col).lower():
        country_col = col
        break

if country_col is None:
    country_col = hdi_raw.columns[1]

print(f"\nCountry column: {country_col}")

# Find year columns
year_columns = []
for col in hdi_raw.columns:
    # Check if column name is a year
    try:
        year_val = int(float(str(col)))
        if 1990 <= year_val <= 2023:
            year_columns.append(col)
    except:
        pass

# If no year columns found, use the mapping
if len(year_columns) == 0:
    print("\nUsing manual year column mapping...")
    year_columns = [col for col in hdi_raw.columns if isinstance(col, int) and 1990 <= col <= 2023]

print(f"\nYear columns found: {year_columns}")

if len(year_columns) == 0:
    print("\n⚠️ Still no year columns. Showing all columns with sample data:")
    for i, col in enumerate(hdi_raw.columns):
        sample = hdi_raw[col].iloc[5] if len(hdi_raw) > 5 else None
        print(f"  Col {i}: '{col}' → sample: {sample}")

# ========================================
# STEP 3: CLEAN DATA
# ========================================

hdi_clean = hdi_raw.copy()

# Rename country column for consistency
hdi_clean = hdi_clean.rename(columns={country_col: 'Country'})

# Remove rows that are category headers
hdi_clean = hdi_clean[
    ~hdi_clean['Country'].astype(str).str.contains(
        'Very high|High human|Medium human|Low human|development', 
        case=False, na=False
    )
]

# Remove rows where Country is NaN or empty
hdi_clean = hdi_clean[hdi_clean['Country'].notna()]
hdi_clean['Country'] = hdi_clean['Country'].astype(str).str.strip()
hdi_clean = hdi_clean[hdi_clean['Country'] != 'nan']
hdi_clean = hdi_clean[hdi_clean['Country'] != '']

print(f"\nCleaned data shape: {hdi_clean.shape}")
print(f"Countries found: {len(hdi_clean)}")

# Show sample of cleaned data
print("\nSample countries:")
print(hdi_clean[['Country'] + year_columns[:4]].head(10))

# ========================================
# STEP 4: FIND TRANSITION YEAR FOR EACH COUNTRY
# ========================================

HDI_THRESHOLD = 0.800

transition_results = []

# Debug: Check if we have valid year columns
if len(year_columns) == 0:
    print("\n❌ ERROR: No year columns found!")
    print("Available columns:", hdi_clean.columns.tolist())
    print("\nPlease check your Excel file structure.")
    exit()

print(f"\nProcessing {len(hdi_clean)} countries...")

for idx, row in hdi_clean.iterrows():
    country = row['Country']
    
    # Skip if country is empty
    if not country or country == 'nan':
        continue
    
    # Find first year where HDI >= 0.800
    transition_year = None
    hdi_at_transition = None
    
    for year_col in year_columns:
        try:
            hdi_value = pd.to_numeric(row[year_col], errors='coerce')
        except:
            continue
        
        if pd.isna(hdi_value) or hdi_value == 0:
            continue
        
        if hdi_value >= HDI_THRESHOLD:
            # Get year from column
            if isinstance(year_col, (int, float)):
                transition_year = int(year_col)
            else:
                transition_year = int(str(year_col))
            
            hdi_at_transition = float(hdi_value)
            break
    
    if transition_year is None:
        # Not yet developed - get latest HDI
        latest_hdi = None
        latest_year = None
        
        for year_col in reversed(year_columns):
            try:
                hdi_value = pd.to_numeric(row[year_col], errors='coerce')
                if not pd.isna(hdi_value) and hdi_value > 0:
                    latest_hdi = float(hdi_value)
                    if isinstance(year_col, (int, float)):
                        latest_year = int(year_col)
                    else:
                        latest_year = int(str(year_col))
                    break
            except:
                continue
        
        if latest_hdi:
            transition_results.append({
                'country': country,
                'transition_year': 'Not yet developed',
                'hdi_at_transition': None,
                'latest_year': latest_year,
                'latest_hdi': latest_hdi
            })
    else:
        transition_results.append({
            'country': country,
            'transition_year': transition_year,
            'hdi_at_transition': hdi_at_transition,
            'latest_year': None,
            'latest_hdi': None
        })

# Create DataFrame
if len(transition_results) == 0:
    print("\n❌ ERROR: No transition data found!")
    print("Check if year columns contain valid HDI values.")
    exit()

transition_df = pd.DataFrame(transition_results)

# Filter to developed countries
developed_countries = transition_df[transition_df['transition_year'] != 'Not yet developed'].copy()

if len(developed_countries) == 0:
    print("\n❌ ERROR: No developed countries found!")
    print("This might mean:")
    print("1. Year columns are not being read correctly")
    print("2. HDI values are not numeric")
    print("\nShowing sample data:")
    print(transition_df.head())
    exit()

print("\n" + "="*70)
print("=== COUNTRIES THAT REACHED DEVELOPED STATUS (HDI ≥ 0.800) ===")
print("="*70)
print(f"Total: {len(developed_countries)} countries\n")
print(developed_countries[['country', 'transition_year', 'hdi_at_transition']].sort_values('transition_year').to_string(index=False))

# Export
transition_df.to_csv('hdi_transition_years.csv', index=False)
developed_countries.to_csv('developed_countries_hdi.csv', index=False)
print("\n>>> Saved to 'hdi_transition_years.csv' and 'developed_countries_hdi.csv'")

# ========================================
# STEP 5: LOAD FERTILITY DATA
# ========================================

print("\n" + "="*70)
print("Loading fertility data...")
print("="*70)

fertility_raw = pd.read_csv("fertility_rate.csv", skiprows=4)

year_columns_fert = [col for col in fertility_raw.columns if col.isdigit()]

fertility_long = fertility_raw.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_columns_fert,
    var_name='year',
    value_name='total_fertility_rate'
)

fertility_long = fertility_long.rename(columns={
    'Country Name': 'country',
    'Country Code': 'country_code'
})

fertility_long['year'] = pd.to_numeric(fertility_long['year'])
fertility_long['total_fertility_rate'] = pd.to_numeric(fertility_long['total_fertility_rate'], errors='coerce')
fertility_long = fertility_long.dropna(subset=['total_fertility_rate'])

print("✓ Fertility data loaded")

# ========================================
# STEP 6: LOAD GNI DATA
# ========================================

print("Loading GNI data...")

gni_raw = pd.read_csv("gni_file.csv", skiprows=4)

year_columns_gni = [col for col in gni_raw.columns if col.isdigit()]

gni_long = gni_raw.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_columns_gni,
    var_name='year',
    value_name='gni_per_capita'
)

gni_long = gni_long.rename(columns={
    'Country Name': 'country',
    'Country Code': 'country_code'
})

gni_long['year'] = pd.to_numeric(gni_long['year'])
gni_long['gni_per_capita'] = pd.to_numeric(gni_long['gni_per_capita'], errors='coerce')
gni_long = gni_long.dropna(subset=['gni_per_capita'])

print("✓ GNI data loaded")

# ========================================
# STEP 7: STANDARDIZE COUNTRY NAMES
# ========================================

def standardize_country_name(name):
    """Standardize country names for matching"""
    name = str(name).strip()
    
    replacements = {
        'Korea, Rep.': 'Korea (Republic of)',
        'South Korea': 'Korea (Republic of)',
        'Republic of Korea': 'Korea (Republic of)',
        'Czech Republic': 'Czechia',
        'Slovak Republic': 'Slovakia',
        'United States': 'United States of America',
        'Russia': 'Russian Federation',
        'Iran, Islamic Rep.': 'Iran (Islamic Republic of)',
        'Egypt, Arab Rep.': 'Egypt',
        'Venezuela, RB': 'Venezuela (Bolivarian Republic of)',
        'Türkiye': 'Turkey',
        'Turkiye': 'Turkey',
        'Viet Nam': 'Vietnam',
        'Hong Kong SAR, China': 'Hong Kong, China (SAR)',
        'Macao SAR, China': 'Macao, China (SAR)',
    }
    
    for old, new in replacements.items():
        if old.lower() in name.lower():
            return new
    
    return name

developed_countries['country_standard'] = developed_countries['country'].apply(standardize_country_name)
fertility_long['country_standard'] = fertility_long['country'].apply(standardize_country_name)
gni_long['country_standard'] = gni_long['country'].apply(standardize_country_name)

# ========================================
# STEP 8: CALCULATE FERTILITY BEFORE & AFTER
# ========================================

print("\n" + "="*70)
print("Calculating fertility changes...")
print("="*70)

analysis_results = []
no_match_countries = []

for _, row in developed_countries.iterrows():
    country = row['country']
    country_std = row['country_standard']
    transition_year = row['transition_year']
    
    # Try multiple matching strategies
    country_fertility = fertility_long[
        (fertility_long['country_standard'].str.lower() == country_std.lower()) |
        (fertility_long['country'].str.lower() == country.lower()) |
        (fertility_long['country'].str.contains(country, case=False, na=False, regex=False))
    ].copy()
    
    if len(country_fertility) == 0:
        no_match_countries.append(country)
        continue
    
    # Mean fertility BEFORE transition (10 years before)
    ten_years_before = transition_year - 10
    
    before_data = country_fertility[
        (country_fertility['year'] >= ten_years_before) & 
        (country_fertility['year'] < transition_year)
    ]
    
    if len(before_data) > 0:
        mean_fertility_before = before_data['total_fertility_rate'].mean()
        years_before = f"{int(before_data['year'].min())}-{transition_year-1}"
    else:
        before_data = country_fertility[country_fertility['year'] < transition_year]
        if len(before_data) > 0:
            mean_fertility_before = before_data['total_fertility_rate'].mean()
            years_before = f"{int(before_data['year'].min())}-{transition_year-1}"
        else:
            mean_fertility_before = None
            years_before = "No data"
    
    # Most recent fertility
    recent_data = country_fertility[country_fertility['year'] >= 2020]
    
    if len(recent_data) > 0:
        most_recent_fertility = recent_data.iloc[-1]['total_fertility_rate']
        most_recent_year = int(recent_data.iloc[-1]['year'])
    else:
        most_recent_fertility = country_fertility.iloc[-1]['total_fertility_rate']
        most_recent_year = int(country_fertility.iloc[-1]['year'])
    
    # Get GNI data
    country_gni = gni_long[
        (gni_long['country_standard'].str.lower() == country_std.lower()) |
        (gni_long['country'].str.lower() == country.lower()) |
        (gni_long['country'].str.contains(country, case=False, na=False, regex=False))
    ].copy()
    
    # GNI at transition
    gni_at_transition = country_gni[country_gni['year'] == transition_year]
    gni_before = gni_at_transition.iloc[0]['gni_per_capita'] if len(gni_at_transition) > 0 else None
    
    # GNI now
    gni_recent = country_gni[country_gni['year'] == most_recent_year]
    gni_now = gni_recent.iloc[0]['gni_per_capita'] if len(gni_recent) > 0 else None
    
    analysis_results.append({
        'country': country,
        'transition_year': transition_year,
        'hdi_at_transition': row['hdi_at_transition'],
        'mean_fertility_before': mean_fertility_before,
        'years_used_before': years_before,
        'gni_before': gni_before,
        'most_recent_fertility': most_recent_fertility,
        'most_recent_year': most_recent_year,
        'gni_now': gni_now,
        'fertility_change': most_recent_fertility - mean_fertility_before if mean_fertility_before else None
    })

if no_match_countries:
    print(f"\n⚠️  Could not find fertility data for {len(no_match_countries)} countries:")
    for c in no_match_countries[:10]:
        print(f"   - {c}")

# Create results DataFrame
results_df = pd.DataFrame(analysis_results)
results_df = results_df.dropna(subset=['mean_fertility_before', 'most_recent_fertility'])
results_df = results_df.sort_values('transition_year')

print(f"\n✓ Successfully matched {len(results_df)} countries")

print("\n" + "="*70)
print("=== FERTILITY ANALYSIS: BEFORE HDI ≥ 0.800 vs NOW ===")
print("="*70)
print(results_df[['country', 'transition_year', 'mean_fertility_before', 'most_recent_fertility', 'fertility_change']].to_string(index=False))

# Export
results_df.to_csv('hdi_fertility_analysis.csv', index=False)
print("\n>>> Saved to 'hdi_fertility_analysis.csv'")

# ========================================
# STEP 9: CREATE SIMPLIFIED SCATTER PLOT
# ========================================

print("\nCreating simplified visualization...")

fig, ax = plt.subplots(figsize=(18, 11))

# Categorize by decline magnitude
results_df['decline_category'] = pd.cut(
    results_df['fertility_change'],
    bins=[-np.inf, -1.5, -1.0, -0.5, np.inf],
    labels=['Large decline (>1.5)', 'Moderate decline (1.0-1.5)', 'Small decline (0.5-1.0)', 'Minimal decline (<0.5)']
)

# Plot ALL "BEFORE" points
ax.scatter(
    results_df['gni_before'],
    results_df['mean_fertility_before'],
    color='#E74C3C',
    s=250,
    alpha=0.7,
    edgecolors='black',
    linewidth=2,
    marker='o',
    zorder=3,
    label='Before Developed Status (HDI < 0.800)'
)

# Plot ALL "NOW" points
ax.scatter(
    results_df['gni_now'],
    results_df['most_recent_fertility'],
    color='#3498DB',
    s=250,
    alpha=0.8,
    edgecolors='black',
    linewidth=2,
    marker='s',
    zorder=4,
    label='Current Status (HDI ≥ 0.800)'
)

# ========================================
# SPECIAL HIGHLIGHTING: Saudi Arabia, Kuwait, Korea, Qatar
# ========================================

highlight_countries = ['Saudi Arabia', 'Kuwait', 'Korea (Republic of)', 'Qatar']
highlighted = results_df[results_df['country'].isin(highlight_countries)].copy()

# Draw arrows for highlighted countries (RED)
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_before']) and pd.notna(row['gni_now']):
        ax.annotate(
            '',
            xy=(row['gni_now'], row['most_recent_fertility']),
            xytext=(row['gni_before'], row['mean_fertility_before']),
            arrowprops=dict(
                arrowstyle='-|>',
                color='#E74C3C',
                alpha=0.8,
                linewidth=3.5,
                connectionstyle="arc3,rad=0.2",
                shrinkA=8,
                shrinkB=8
            ),
            zorder=6
        )

# Add labels with country name AND decline amount (RED)
for _, row in highlighted.iterrows():
    country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
    decline_amount = abs(row['fertility_change'])
    
    label_text = f"{country_display}\n(↓ {decline_amount:.2f})"
    
    ax.annotate(
        label_text,
        xy=(row['gni_now'], row['most_recent_fertility']),
        xytext=(12, 8),
        textcoords='offset points',
        fontsize=11,
        fontweight='bold',
        color='#C0392B',
        alpha=1.0,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#FADBD8', 
                 edgecolor='#E74C3C', linewidth=2, alpha=0.95),
        zorder=7,
        ha='left'
    )

# Add reference line
ax.axhline(y=2.1, color='green', linestyle='--', linewidth=2, 
           alpha=0.6, label='Replacement Level (2.1)', zorder=0)

# Styling
ax.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=16, fontweight='bold', labelpad=10)
ax.set_ylabel('Total Fertility Rate (births per woman)', fontsize=16, fontweight='bold', labelpad=10)
ax.set_title('Fertility Change in Developed Countries:\nBefore HDI ≥ 0.800 vs. Present',
             fontsize=20, fontweight='bold', pad=25)

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Grid
ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, color='gray')
ax.set_axisbelow(True)

# Legend
legend = ax.legend(
    loc='upper right', 
    fontsize=12, 
    frameon=True, 
    shadow=True,
    fancybox=True,
    framealpha=0.95
)

# Statistics box BELOW legend
stats_text = f"""Key Statistics:
• Countries analyzed: {len(results_df)}
• Highlighted countries: {len(highlighted)}
• Avg. fertility before: {results_df['mean_fertility_before'].mean():.2f}
• Avg. fertility now: {results_df['most_recent_fertility'].mean():.2f}"""

ax.text(
    0.98, 0.55, stats_text,
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment='top',
    horizontalalignment='right',
    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
    family='monospace'
)

# Caption
plt.figtext(
    0.99, 0.01, 
    'Source: UNDP Human Development Report & World Bank | HDI threshold: 0.800',
    ha='right', 
    fontsize=9, 
    style='italic', 
    color='#34495E',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
)

# Background
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('white')

plt.tight_layout(rect=[0, 0.03, 1, 1])

# Save
plt.savefig('hdi_fertility_transition_highlighted.png', dpi=300, bbox_inches='tight', 
            facecolor='white')
print("✓ Plot saved as 'hdi_fertility_transition_highlighted.png'")

plt.show()

print("\n=== HIGHLIGHTED COUNTRIES DETAILS ===")
print(highlighted[['country', 'transition_year', 'mean_fertility_before', 
                   'most_recent_fertility', 'fertility_change']].to_string(index=False))

# ========================================
# SPECIAL HIGHLIGHTING: Saudi Arabia, Kuwait, Korea, Qatar
# ========================================

# Countries to highlight
highlight_countries = ['Saudi Arabia', 'Kuwait', 'Korea (Republic of)', 'Qatar']

# Find these countries in the data
highlighted = results_df[results_df['country'].isin(highlight_countries)].copy()

# Draw arrows for highlighted countries (in different color)
for _, row in highlighted.iterrows():
    if pd.notna(row['gni_before']) and pd.notna(row['gni_now']):
        ax.annotate(
            '',
            xy=(row['gni_now'], row['most_recent_fertility']),
            xytext=(row['gni_before'], row['mean_fertility_before']),
            arrowprops=dict(
                arrowstyle='-|>',
                color='#8E44AD',  # Purple for special countries
                alpha=0.8,
                linewidth=3.5,
                connectionstyle="arc3,rad=0.2",
                shrinkA=8,
                shrinkB=8
            ),
            zorder=6
        )

# Add labels with country name AND decline amount
for _, row in highlighted.iterrows():
    country_display = row['country'].replace('Korea (Republic of)', 'South Korea')
    decline_amount = abs(row['fertility_change'])
    
    label_text = f"{country_display}\n(↓ {decline_amount:.2f})"
    
    ax.annotate(
        label_text,
        xy=(row['gni_now'], row['most_recent_fertility']),
        xytext=(12, 8),
        textcoords='offset points',
        fontsize=11,
        fontweight='bold',
        color='#8E44AD',
        alpha=1.0,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#F4ECF7', 
                 edgecolor='#8E44AD', linewidth=2, alpha=0.95),
        zorder=7,
        ha='left'
    )

# Add reference lines
ax.axhline(y=2.1, color='green', linestyle='--', linewidth=2, 
           alpha=0.6, label='Replacement Level (2.1)', zorder=0)

ax.axhline(y=1.3, color='red', linestyle=':', linewidth=2, 
           alpha=0.4, label='Very Low Fertility (1.3)', zorder=0)

# Styling
ax.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=16, fontweight='bold', labelpad=10)
ax.set_ylabel('Total Fertility Rate (births per woman)', fontsize=16, fontweight='bold', labelpad=10)
ax.set_title('Fertility Decline in Developed Countries:\nBefore HDI ≥ 0.800 vs. Present',
             fontsize=20, fontweight='bold', pad=25)

# Format x-axis
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))

# Grid
ax.grid(True, alpha=0.25, linestyle='-', linewidth=0.5, color='gray')
ax.set_axisbelow(True)

# Legend
ax.legend(
    loc='upper right', 
    fontsize=12, 
    frameon=True, 
    shadow=True,
    fancybox=True,
    framealpha=0.95
)

# Statistics box
stats_text = f"""Key Statistics:
• Countries analyzed: {len(results_df)}
• Moderate decline cases: {len(moderate_decline)}
• Highlighted countries: {len(highlighted)}
• Avg. fertility before: {results_df['mean_fertility_before'].mean():.2f}
• Avg. fertility now: {results_df['most_recent_fertility'].mean():.2f}"""

ax.text(
    0.02, 0.98, stats_text,
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment='top',
    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85),
    family='monospace'
)

# Caption
plt.figtext(
    0.99, 0.01, 
    'Source: UNDP Human Development Report & World Bank | HDI threshold: 0.800\n'
    'Purple arrows: Saudi Arabia, Kuwait, South Korea, Qatar | Red arrows: Moderate decline countries',
    ha='right', 
    fontsize=9, 
    style='italic', 
    color='#34495E',
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
)

# Background
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('white')

plt.tight_layout(rect=[0, 0.03, 1, 1])

# Save
plt.savefig('hdi_fertility_transition_highlighted.png', dpi=300, bbox_inches='tight', 
            facecolor='white')
print("✓ Plot saved as 'hdi_fertility_transition_highlighted.png'")

plt.show()

print("\n=== HIGHLIGHTED COUNTRIES DETAILS ===")
print(highlighted[['country', 'transition_year', 'mean_fertility_before', 
                   'most_recent_fertility', 'fertility_change']].to_string(index=False))


# ========================================
# DETAILED FERTILITY CHANGE ANALYSIS
# ========================================

print("\n" + "="*90)
print("=== COMPLETE FERTILITY CHANGE RANKING (LARGEST TO SMALLEST DECLINE) ===")
print("="*90)

# Sort by fertility change (most negative = largest decline)
results_sorted = results_df.sort_values('fertility_change', ascending=True).copy()

# Add rank
results_sorted['rank'] = range(1, len(results_sorted) + 1)

# Display all countries with detailed information
print("\n{:<5} {:<35} {:<8} {:<10} {:<10} {:<12}".format(
    "Rank", "Country", "Trans Yr", "Before", "Current", "Change"
))
print("-" * 90)

for _, row in results_sorted.iterrows():
    print("{:<5} {:<35} {:<8} {:<10.2f} {:<10.2f} {:<12.2f}".format(
        row['rank'],
        row['country'][:34],  # Truncate long names
        row['transition_year'],
        row['mean_fertility_before'],
        row['most_recent_fertility'],
        row['fertility_change']
    ))

# Export detailed ranking
results_sorted[['rank', 'country', 'transition_year', 'mean_fertility_before', 
                'most_recent_fertility', 'fertility_change', 'gni_before', 'gni_now']].to_csv(
    'fertility_change_ranking.csv', index=False
)
print("\n>>> Detailed ranking saved to 'fertility_change_ranking.csv'")

# ========================================
# CHECK FOR INCREASES OR NO CHANGE
# ========================================

print("\n" + "="*90)
print("=== COUNTRIES WITH FERTILITY INCREASE OR NO CHANGE ===")
print("="*90)

# Countries where fertility increased or stayed same
increased_or_same = results_df[results_df['fertility_change'] >= 0].copy()

if len(increased_or_same) > 0:
    print(f"\n⚠️  Found {len(increased_or_same)} countries with fertility increase or no change:\n")
    
    print("{:<35} {:<8} {:<10} {:<10} {:<12}".format(
        "Country", "Trans Yr", "Before", "Current", "Change"
    ))
    print("-" * 90)
    
    for _, row in increased_or_same.iterrows():
        change_type = "INCREASE ↑" if row['fertility_change'] > 0 else "NO CHANGE ≈"
        print("{:<35} {:<8} {:<10.2f} {:<10.2f} {:<12.2f}  {}".format(
            row['country'][:34],
            row['transition_year'],
            row['mean_fertility_before'],
            row['most_recent_fertility'],
            row['fertility_change'],
            change_type
        ))
    
    # Export these special cases
    increased_or_same.to_csv('fertility_increased_or_same.csv', index=False)
    print("\n>>> Saved to 'fertility_increased_or_same.csv'")
    
else:
    print("\n✓ No countries found with fertility increase or no change.")
    print("  All developed countries experienced fertility decline.")

# ========================================
# SUMMARY BY DECLINE MAGNITUDE
# ========================================

print("\n" + "="*90)
print("=== SUMMARY BY DECLINE MAGNITUDE ===")
print("="*90)

# Count by category
decline_summary = results_df['decline_category'].value_counts().sort_index()

print("\nDistribution of countries by fertility decline:")
print("-" * 50)
for category, count in decline_summary.items():
    percentage = (count / len(results_df)) * 100
    print(f"{category:<30} {count:>3} countries ({percentage:>5.1f}%)")

print("\n" + "="*90)

# ========================================
# TOP AND BOTTOM 10
# ========================================

print("\n" + "="*90)
print("=== TOP 10 LARGEST FERTILITY DECLINES ===")
print("="*90)

top_10 = results_sorted.head(10)
print("\n{:<5} {:<35} {:<12} {:<12}".format("Rank", "Country", "Before", "Change"))
print("-" * 70)
for _, row in top_10.iterrows():
    print("{:<5} {:<35} {:<12.2f} {:<12.2f}".format(
        int(row['rank']),
        row['country'][:34],
        row['mean_fertility_before'],
        row['fertility_change']
    ))

print("\n" + "="*90)
print("=== TOP 10 SMALLEST FERTILITY DECLINES ===")
print("="*90)

bottom_10 = results_sorted.tail(10)
print("\n{:<5} {:<35} {:<12} {:<12}".format("Rank", "Country", "Before", "Change"))
print("-" * 70)
for _, row in bottom_10.iterrows():
    print("{:<5} {:<35} {:<12.2f} {:<12.2f}".format(
        int(row['rank']),
        row['country'][:34],
        row['mean_fertility_before'],
        row['fertility_change']
    ))

print("\n" + "="*90)

# ========================================
# RANKING BY CURRENT FERTILITY RATE
# ========================================

print("\n" + "="*90)
print("=== RANKING BY CURRENT FERTILITY RATE (LOWEST TO HIGHEST) ===")
print("="*90)

# Sort by current fertility rate (lowest to highest)
current_fertility_ranking = results_df.sort_values('most_recent_fertility', ascending=True).copy()
current_fertility_ranking['current_rank'] = range(1, len(current_fertility_ranking) + 1)

print("\n{:<5} {:<35} {:<8} {:<12} {:<12} {:<12}".format(
    "Rank", "Country", "Trans Yr", "Before", "Current", "Change"
))
print("-" * 90)

for _, row in current_fertility_ranking.iterrows():
    # Highlight the 4 special countries
    if row['country'] in ['Saudi Arabia', 'Kuwait', 'Korea (Republic of)', 'Qatar']:
        marker = " ★"
    else:
        marker = ""
    
    print("{:<5} {:<35} {:<8} {:<12.2f} {:<12.2f} {:<12.2f}{}".format(
        int(row['current_rank']),
        row['country'][:34],
        row['transition_year'],
        row['mean_fertility_before'],
        row['most_recent_fertility'],
        row['fertility_change'],
        marker
    ))

# Export
current_fertility_ranking[['current_rank', 'country', 'transition_year', 
                           'mean_fertility_before', 'most_recent_fertility', 
                           'fertility_change']].to_csv(
    'current_fertility_ranking.csv', index=False
)
print("\n>>> Saved to 'current_fertility_ranking.csv'")

# ========================================
# SPECIAL FOCUS: Saudi Arabia, Kuwait, Korea, Qatar
# ========================================

print("\n" + "="*90)
print("=== SPECIAL FOCUS: SAUDI ARABIA, KUWAIT, KOREA, QATAR ===")
print("="*90)

highlight_countries = ['Saudi Arabia', 'Kuwait', 'Korea (Republic of)', 'Qatar']
special_focus = current_fertility_ranking[current_fertility_ranking['country'].isin(highlight_countries)].copy()

if len(special_focus) > 0:
    print("\n{:<25} {:<8} {:<12} {:<12} {:<12} {:<12}".format(
        "Country", "Rank", "Trans Year", "Before", "Current", "Decline"
    ))
    print("-" * 90)
    
    for _, row in special_focus.iterrows():
        print("{:<25} {:<8} {:<12} {:<12.2f} {:<12.2f} {:<12.2f}".format(
            row['country'].replace('Korea (Republic of)', 'South Korea'),
            int(row['current_rank']),
            row['transition_year'],
            row['mean_fertility_before'],
            row['most_recent_fertility'],
            row['fertility_change']
        ))
else:
    print("\n⚠️  None of the highlighted countries found in dataset.")
    print("Available countries similar to your search:")
    for country in results_df['country'].unique():
        if any(term in country.lower() for term in ['korea', 'saudi', 'kuwait', 'qatar']):
            print(f"  - {country}")

print("\n" + "="*90)

# ========================================
# TOP 10 LOWEST CURRENT FERTILITY
# ========================================

print("\n" + "="*90)
print("=== TOP 10 COUNTRIES WITH LOWEST CURRENT FERTILITY ===")
print("="*90)

top_10_lowest = current_fertility_ranking.head(10)

print("\n{:<5} {:<35} {:<12}".format("Rank", "Country", "Current TFR"))
print("-" * 60)
for _, row in top_10_lowest.iterrows():
    print("{:<5} {:<35} {:<12.2f}".format(
        int(row['current_rank']),
        row['country'][:34],
        row['most_recent_fertility']
    ))

print("\n" + "="*90)