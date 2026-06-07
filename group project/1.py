# ========================================
# GNI per capita & Fertility Rate Analysis
# Using Local CSV Files
# ========================================

# 1. Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

# 2. Developed countries list (UN classification)
developed_countries_list = [
    # Northern America
    "Canada", "United States",
    
    # Europe
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", 
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", 
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", 
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", 
    "Slovenia", "Spain", "Sweden", "Iceland", "Norway", "Switzerland", 
    "United Kingdom",
    
    # Developed Asia and Pacific
    "Australia", "Japan", "New Zealand", "South Korea"
]

# 3. Load GNI per capita CSV (LOCAL FILE)
# REPLACE 'gni_file.csv' with your actual filename
gni_raw = pd.read_csv("gni_file.csv")

# 4. Load fertility rate CSV (LOCAL FILE)
# REPLACE 'fertility_file.csv' with your actual filename
fertility_raw = pd.read_csv("fertility_file.csv")

# ===== DIAGNOSTIC: Check your CSV structure =====
print("=== GNI CSV Structure ===")
print("Columns:", gni_raw.columns.tolist())
print("\nFirst 3 rows:")
print(gni_raw.head(3))

print("\n=== Fertility CSV Structure ===")
print("Columns:", fertility_raw.columns.tolist())
print("\nFirst 3 rows:")
print(fertility_raw.head(3))

# 5. Clean GNI data
# ADJUST column names based on your CSV structure

# Option A: If columns are like "Country Name", "Country Code", "2020", "2021", "2022", "2023"
# (Wide format - World Bank style)
if '2023' in gni_raw.columns or '2022' in gni_raw.columns:
    print("\n>>> Detected WIDE format (World Bank style)")
    
    # Get year columns
    year_columns = [col for col in gni_raw.columns if col.isdigit()]
    
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

# Option B: If columns are like "Entity", "Code", "Year", "GNI per capita"
# (Long format - Our World in Data style)
else:
    print("\n>>> Detected LONG format (Our World in Data style)")
    
    # Find the GNI column (it might have different names)
    gni_column = None
    for col in gni_raw.columns:
        if 'gni' in col.lower() or 'income' in col.lower():
            gni_column = col
            break
    
    if gni_column is None:
        gni_column = gni_raw.columns[-1]  # Use last column as fallback
    
    gni_clean = gni_raw.rename(columns={
        gni_raw.columns[0]: 'country',      # First column = country name
        gni_raw.columns[1]: 'country_code', # Second column = country code
        gni_raw.columns[2]: 'year',         # Third column = year
        gni_column: 'gni_per_capita'        # GNI column
    })

# Keep only necessary columns and remove missing values
gni_clean = gni_clean[['country', 'country_code', 'year', 'gni_per_capita']].copy()
gni_clean = gni_clean.dropna(subset=['gni_per_capita'])
gni_clean = gni_clean[gni_clean['year'] >= 2020]  # Keep recent years only

# 6. Clean fertility data
# ADJUST column names based on your CSV structure

# Option A: Wide format
if '2023' in fertility_raw.columns or '2022' in fertility_raw.columns:
    print("\n>>> Fertility data: WIDE format")
    
    year_columns = [col for col in fertility_raw.columns if col.isdigit()]
    
    fertility_clean = fertility_raw.melt(
        id_vars=['Country Name', 'Country Code'],
        value_vars=year_columns,
        var_name='year',
        value_name='total_fertility_rate'
    )
    
    fertility_clean = fertility_clean.rename(columns={
        'Country Name': 'country',
        'Country Code': 'country_code'
    })
    
    fertility_clean['year'] = pd.to_numeric(fertility_clean['year'])
    fertility_clean['total_fertility_rate'] = pd.to_numeric(fertility_clean['total_fertility_rate'], errors='coerce')

# Option B: Long format
else:
    print("\n>>> Fertility data: LONG format")
    
    # Find the fertility column
    fertility_column = None
    for col in fertility_raw.columns:
        if 'fertility' in col.lower() or 'tfr' in col.lower() or 'birth' in col.lower():
            fertility_column = col
            break
    
    if fertility_column is None:
        fertility_column = fertility_raw.columns[-1]
    
    fertility_clean = fertility_raw.rename(columns={
        fertility_raw.columns[0]: 'country',
        fertility_raw.columns[1]: 'country_code',
        fertility_raw.columns[2]: 'year',
        fertility_column: 'total_fertility_rate'
    })

fertility_clean = fertility_clean[['country', 'country_code', 'year', 'total_fertility_rate']].copy()
fertility_clean = fertility_clean.dropna(subset=['total_fertility_rate'])
fertility_clean = fertility_clean[fertility_clean['year'] >= 2020]

# 7. Find most recent year with data for both datasets
latest_year_gni = int(gni_clean['year'].max())
latest_year_fertility = int(fertility_clean['year'].max())
analysis_year = min(latest_year_gni, latest_year_fertility)

print(f"\n>>> Using data from year: {analysis_year}")

# 8. Merge datasets
combined_data = pd.merge(
    gni_clean[gni_clean['year'] == analysis_year],
    fertility_clean[fertility_clean['year'] == analysis_year],
    on=['country', 'country_code', 'year'],
    how='inner'
)

print(f"\n>>> Merged data: {len(combined_data)} countries before filtering")

# 9. Standardize country names for matching
def standardize_country(name):
    name = str(name).strip()
    
    # Common variations
    replacements = {
        'Korea, Rep.': 'South Korea',
        'Korea, Republic of': 'South Korea',
        'Czech Republic': 'Czechia',
        'United States of America': 'United States',
        'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom',
        'Russian Federation': 'Russia',
        'Slovak Republic': 'Slovakia'
    }
    
    for old, new in replacements.items():
        if old in name:
            return new
    
    return name

combined_data['country_standard'] = combined_data['country'].apply(standardize_country)

# 10. Filter developed countries only
combined_data = combined_data[
    combined_data['country_standard'].isin(developed_countries_list)
].copy()

print(f"\n>>> After filtering: {len(combined_data)} developed countries")

# 11. Add region classification
def classify_region(country):
    if country in ["Canada", "United States"]:
        return "North America"
    elif country in ["Australia", "Japan", "New Zealand", "South Korea"]:
        return "Asia-Pacific"
    else:
        return "Europe"

combined_data['region'] = combined_data['country_standard'].apply(classify_region)

# 12. Display countries included
print("\n=== Countries Included ===")
for region in sorted(combined_data['region'].unique()):
    countries = sorted(combined_data[combined_data['region'] == region]['country_standard'].unique())
    print(f"\n{region} ({len(countries)}):")
    print(", ".join(countries))

# 13. Calculate correlation
correlation = combined_data['gni_per_capita'].corr(combined_data['total_fertility_rate'])
print(f"\n=== Correlation Coefficient: {correlation:.3f} ===")

# 14. Create scatter plot
plt.figure(figsize=(14, 9))

# Define colors for regions
colors = {
    'North America': '#E74C3C',
    'Europe': '#3498DB',
    'Asia-Pacific': '#2ECC71'
}

# Plot points by region
for region in sorted(combined_data['region'].unique()):
    data = combined_data[combined_data['region'] == region]
    plt.scatter(
        data['gni_per_capita'],
        data['total_fertility_rate'],
        label=region,
        color=colors[region],
        s=120,
        alpha=0.7,
        edgecolors='white',
        linewidth=2
    )

# Add regression line
x = combined_data['gni_per_capita'].values
y = combined_data['total_fertility_rate'].values
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

# Create line points
x_line = np.linspace(x.min(), x.max(), 100)
y_line = slope * x_line + intercept

plt.plot(x_line, y_line, color='#2C3E50', linewidth=2.5, 
         linestyle='--', label=f'Linear Trend (r={correlation:.3f})', zorder=1)

# Add confidence interval (optional)
predict_y = slope * x + intercept
predict_error = y - predict_y
degrees_of_freedom = len(x) - 2
residual_std_error = np.sqrt(np.sum(predict_error**2) / degrees_of_freedom)

# Styling
plt.xlabel('GNI per Capita (USD)', fontsize=13, fontweight='bold')
plt.ylabel('Total Fertility Rate (births per woman)', fontsize=13, fontweight='bold')
plt.title('Economic Development and Fertility Rates in Developed Countries',
          fontsize=17, fontweight='bold', pad=20)
plt.suptitle(f'Relationship between GNI per capita and Total Fertility Rate ({analysis_year}) | Correlation: {correlation:.3f}',
             fontsize=12, color='#555555', y=0.965)

# Format x-axis with dollar signs
ax = plt.gca()
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Grid and legend
plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
plt.legend(loc='best', frameon=True, shadow=True, fontsize=11)

# Add caption
plt.figtext(0.99, 0.01, 'Source: World Bank & UN Population Division',
            ha='right', fontsize=9, style='italic', color='gray')

# Set background
ax.set_facecolor('#FAFAFA')
plt.tight_layout()

# Save plot
output_file = 'fertility_gni_developed_countries.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n>>> Plot saved as '{output_file}'")

plt.show()

# 15. Summary statistics
print("\n=== Summary Statistics ===")
print(combined_data[['gni_per_capita', 'total_fertility_rate']].describe())

# 16. Top 10 countries by GNI
print("\n=== Top 10 Countries by GNI per Capita ===")
top_countries = combined_data.nlargest(10, 'gni_per_capita')[
    ['country_standard', 'region', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
top_countries.index = top_countries.index + 1
print(top_countries)

# 17. Countries with lowest fertility
print("\n=== Top 10 Countries with Lowest Fertility Rates ===")
low_fertility = combined_data.nsmallest(10, 'total_fertility_rate')[
    ['country_standard', 'region', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
low_fertility.index = low_fertility.index + 1
print(low_fertility)

# 18. Export combined data to CSV (optional)
output_csv = 'combined_data_developed_countries.csv'
combined_data.to_csv(output_csv, index=False)
print(f"\n>>> Combined data exported to '{output_csv}'")

print("\n=== Analysis Complete! ===")