# ========================================
# GNI per capita & Fertility Rate Analysis
# SHOWING ALL COUNTRIES
# ========================================

# 1. Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

# 2. Load GNI per capita CSV (skip 4 metadata rows)
gni_raw = pd.read_csv("gni_file.csv", skiprows=4)

# 3. Load fertility rate CSV (skip 4 metadata rows)
fertility_raw = pd.read_csv("fertility_rate.csv", skiprows=4)

print("=== Data Loaded Successfully ===")
print(f"GNI data shape: {gni_raw.shape}")
print(f"Fertility data shape: {fertility_raw.shape}")

# 4. Clean GNI data (World Bank wide format)
# Get year columns (all columns that are numeric years)
year_columns = [col for col in gni_raw.columns if col.isdigit()]

print(f"\nYear range in data: {min(year_columns)} - {max(year_columns)}")

# Reshape from wide to long format
gni_clean = gni_raw.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_columns,
    var_name='year',
    value_name='gni_per_capita'
)

gni_clean = gni_clean.rename(columns={
    'Country Name': 'country',
    'Country Code': 'country_code'
})

gni_clean['year'] = pd.to_numeric(gni_clean['year'])
gni_clean['gni_per_capita'] = pd.to_numeric(gni_clean['gni_per_capita'], errors='coerce')

# Keep only recent years (2015 onwards) and remove missing values
gni_clean = gni_clean[gni_clean['year'] >= 2015].copy()
gni_clean = gni_clean.dropna(subset=['gni_per_capita'])

# 5. Clean fertility data (same process)
year_columns_fert = [col for col in fertility_raw.columns if col.isdigit()]

fertility_clean = fertility_raw.melt(
    id_vars=['Country Name', 'Country Code'],
    value_vars=year_columns_fert,
    var_name='year',
    value_name='total_fertility_rate'
)

fertility_clean = fertility_clean.rename(columns={
    'Country Name': 'country',
    'Country Code': 'country_code'
})

fertility_clean['year'] = pd.to_numeric(fertility_clean['year'])
fertility_clean['total_fertility_rate'] = pd.to_numeric(fertility_clean['total_fertility_rate'], errors='coerce')

fertility_clean = fertility_clean[fertility_clean['year'] >= 2015].copy()
fertility_clean = fertility_clean.dropna(subset=['total_fertility_rate'])

# 6. Find most recent year with data for both datasets
latest_year_gni = int(gni_clean['year'].max())
latest_year_fertility = int(fertility_clean['year'].max())
analysis_year = min(latest_year_gni, latest_year_fertility)

print(f"\n>>> Using data from year: {analysis_year}")

# 7. Merge datasets
combined_data = pd.merge(
    gni_clean[gni_clean['year'] == analysis_year],
    fertility_clean[fertility_clean['year'] == analysis_year],
    on=['country', 'country_code', 'year'],
    how='inner'
)

print(f">>> Total countries with data: {len(combined_data)}")

# 8. Filter out aggregates (regional/income groups)
# Remove rows that are not actual countries
aggregates_to_remove = [
    'World', 'Arab World', 'Africa', 'East Asia', 'Europe', 'European Union',
    'High income', 'Low income', 'Middle income', 'Lower middle income', 'Upper middle income',
    'OECD', 'Sub-Saharan', 'Latin America', 'Caribbean', 'South Asia', 'North America',
    'Central Europe', 'Pacific', 'IDA', 'IBRD', 'Fragile', 'Heavily indebted',
    'Least developed', 'Small states', 'Post-demographic', 'Pre-demographic',
    'Early-demographic', 'Late-demographic'
]

# Filter out aggregates
combined_data = combined_data[
    ~combined_data['country'].str.contains('|'.join(aggregates_to_remove), case=False, na=False)
].copy()

print(f">>> After removing aggregates: {len(combined_data)} countries")

# 9. Classify countries by World Bank income group
def classify_income_group(gni):
    """Classify countries by 2024 World Bank income thresholds"""
    if pd.isna(gni):
        return 'Unknown'
    elif gni <= 1135:
        return 'Low income'
    elif gni <= 4465:
        return 'Lower middle income'
    elif gni <= 13845:
        return 'Upper middle income'
    else:
        return 'High income'

combined_data['income_group'] = combined_data['gni_per_capita'].apply(classify_income_group)

# 10. Classify by UN development status (based on your list)
developed_countries_list = [
    "Canada", "United States",
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", 
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", 
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", 
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", 
    "Slovenia", "Spain", "Sweden", "Iceland", "Norway", "Switzerland", 
    "United Kingdom", "Australia", "Japan", "New Zealand", "Korea, Rep."
]

def classify_development_status(country):
    # Standardize country names
    if 'Korea, Rep' in country:
        country = 'Korea, Rep.'
    elif 'Czech Republic' in country:
        country = 'Czechia'
    
    if country in developed_countries_list:
        return 'Developed'
    else:
        return 'Developing'

combined_data['development_status'] = combined_data['country'].apply(classify_development_status)

# 11. Display summary by category
print("\n=== Countries by Development Status ===")
print(combined_data['development_status'].value_counts())

print("\n=== Countries by Income Group ===")
print(combined_data['income_group'].value_counts())

# 12. Calculate correlation
correlation = combined_data['gni_per_capita'].corr(combined_data['total_fertility_rate'])
print(f"\n=== Overall Correlation Coefficient: {correlation:.3f} ===")

# 13. Create comprehensive scatter plot
fig, ax = plt.subplots(figsize=(16, 10))

# Define colors for development status
colors = {
    'Developed': '#3498DB',
    'Developing': '#E74C3C'
}

# Plot points by development status
for status in sorted(combined_data['development_status'].unique()):
    data = combined_data[combined_data['development_status'] == status]
    ax.scatter(
        data['gni_per_capita'],
        data['total_fertility_rate'],
        label=f'{status} ({len(data)} countries)',
        color=colors[status],
        s=80,
        alpha=0.6,
        edgecolors='white',
        linewidth=1
    )

# Add regression line for all data
x = combined_data['gni_per_capita'].values
y = combined_data['total_fertility_rate'].values
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

# Create line points
x_line = np.linspace(x.min(), x.max(), 100)
y_line = slope * x_line + intercept

ax.plot(x_line, y_line, color='#2C3E50', linewidth=2.5, 
        linestyle='--', label=f'Overall Trend (r={correlation:.3f})', zorder=1)

# Styling
ax.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=14, fontweight='bold')
ax.set_ylabel('Total Fertility Rate (births per woman)', fontsize=14, fontweight='bold')
ax.set_title('Economic Development and Fertility Rates - All Countries',
             fontsize=18, fontweight='bold', pad=20)
plt.suptitle(f'Relationship between GNI per capita and Total Fertility Rate ({analysis_year}) | n={len(combined_data)} countries',
             fontsize=13, color='#555555', y=0.97)

# Format x-axis with dollar signs
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Grid and legend
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax.legend(loc='upper right', frameon=True, shadow=True, fontsize=11)

# Add caption
plt.figtext(0.99, 0.01, 'Source: World Bank World Development Indicators',
            ha='right', fontsize=10, style='italic', color='gray')

# Set background
ax.set_facecolor('#FAFAFA')
plt.tight_layout()

# Save plot
output_file = 'fertility_gni_all_countries.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n>>> Plot saved as '{output_file}'")

plt.show()

# 14. Create second plot: By Income Group
fig2, ax2 = plt.subplots(figsize=(16, 10))

# Define colors for income groups
income_colors = {
    'Low income': '#E74C3C',
    'Lower middle income': '#F39C12',
    'Upper middle income': '#F1C40F',
    'High income': '#2ECC71'
}

# Plot points by income group
for income in ['Low income', 'Lower middle income', 'Upper middle income', 'High income']:
    data = combined_data[combined_data['income_group'] == income]
    if len(data) > 0:
        ax2.scatter(
            data['gni_per_capita'],
            data['total_fertility_rate'],
            label=f'{income} ({len(data)})',
            color=income_colors[income],
            s=80,
            alpha=0.6,
            edgecolors='white',
            linewidth=1
        )

# Add regression line
ax2.plot(x_line, y_line, color='#2C3E50', linewidth=2.5, 
         linestyle='--', label=f'Overall Trend (r={correlation:.3f})', zorder=1)

# Styling
ax2.set_xlabel('GNI per Capita (USD, Atlas method)', fontsize=14, fontweight='bold')
ax2.set_ylabel('Total Fertility Rate (births per woman)', fontsize=14, fontweight='bold')
ax2.set_title('Economic Development and Fertility Rates by Income Group',
              fontsize=18, fontweight='bold', pad=20)
plt.suptitle(f'World Bank Income Classification ({analysis_year})',
             fontsize=13, color='#555555', y=0.97)

# Format x-axis
ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Grid and legend
ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
ax2.legend(loc='upper right', frameon=True, shadow=True, fontsize=11)

# Add caption
plt.figtext(0.99, 0.01, 'Source: World Bank World Development Indicators',
            ha='right', fontsize=10, style='italic', color='gray')

ax2.set_facecolor('#FAFAFA')
plt.tight_layout()

# Save second plot
output_file2 = 'fertility_gni_by_income_group.png'
plt.savefig(output_file2, dpi=300, bbox_inches='tight', facecolor='white')
print(f">>> Second plot saved as '{output_file2}'")

plt.show()

# 15. Summary statistics
print("\n=== Overall Summary Statistics ===")
print(combined_data[['gni_per_capita', 'total_fertility_rate']].describe())

print("\n=== Summary by Development Status ===")
print(combined_data.groupby('development_status')[['gni_per_capita', 'total_fertility_rate']].describe())

print("\n=== Summary by Income Group ===")
print(combined_data.groupby('income_group')[['gni_per_capita', 'total_fertility_rate']].mean().round(2))

# 16. Top 20 countries by GNI
print("\n=== Top 20 Countries by GNI per Capita ===")
top_countries = combined_data.nlargest(20, 'gni_per_capita')[
    ['country', 'development_status', 'income_group', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
top_countries.index = top_countries.index + 1
print(top_countries.to_string())

# 17. Bottom 20 countries by GNI
print("\n=== Bottom 20 Countries by GNI per Capita ===")
bottom_countries = combined_data.nsmallest(20, 'gni_per_capita')[
    ['country', 'development_status', 'income_group', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
bottom_countries.index = bottom_countries.index + 1
print(bottom_countries.to_string())

# 18. Countries with highest fertility
print("\n=== Top 20 Countries with Highest Fertility Rates ===")
high_fertility = combined_data.nlargest(20, 'total_fertility_rate')[
    ['country', 'development_status', 'income_group', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
high_fertility.index = high_fertility.index + 1
print(high_fertility.to_string())

# 19. Countries with lowest fertility
print("\n=== Top 20 Countries with Lowest Fertility Rates ===")
low_fertility = combined_data.nsmallest(20, 'total_fertility_rate')[
    ['country', 'development_status', 'income_group', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
low_fertility.index = low_fertility.index + 1
print(low_fertility.to_string())

# 20. Export full data to CSV
output_csv = 'all_countries_gni_fertility.csv'
combined_data_export = combined_data[[
    'country', 'country_code', 'year', 'gni_per_capita', 'total_fertility_rate',
    'development_status', 'income_group'
]].sort_values('country')

combined_data_export.to_csv(output_csv, index=False)
print(f"\n>>> Full dataset exported to '{output_csv}'")

# 21. Correlation by group
print("\n=== Correlation by Development Status ===")
for status in combined_data['development_status'].unique():
    data = combined_data[combined_data['development_status'] == status]
    corr = data['gni_per_capita'].corr(data['total_fertility_rate'])
    print(f"{status}: {corr:.3f} (n={len(data)})")

print("\n=== Correlation by Income Group ===")
for income in ['Low income', 'Lower middle income', 'Upper middle income', 'High income']:
    data = combined_data[combined_data['income_group'] == income]
    if len(data) > 1:
        corr = data['gni_per_capita'].corr(data['total_fertility_rate'])
        print(f"{income}: {corr:.3f} (n={len(data)})")

print("\n=== Analysis Complete! ===")
print(f"Total countries analyzed: {len(combined_data)}")
print(f"Developed countries: {len(combined_data[combined_data['development_status']=='Developed'])}")
print(f"Developing countries: {len(combined_data[combined_data['development_status']=='Developing'])}")