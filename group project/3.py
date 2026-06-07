# ========================================
# GNI per capita & Fertility Rate Analysis
# THREE CATEGORIES: Developed, Transitioning, Developing
# ========================================

# 1. Import libraries
import pandas as pd          # For data manipulation
import matplotlib.pyplot as plt  # For creating plots
import seaborn as sns        # For enhanced visualizations
from scipy import stats      # For statistical analysis (regression)
import numpy as np           # For numerical operations

# ========================================
# STEP 1: LOAD DATA
# ========================================

# Load GNI per capita CSV
# skiprows=4 removes the first 4 metadata rows from World Bank CSV
gni_raw = pd.read_csv("gni_file.csv", skiprows=4)

# Load fertility rate CSV
fertility_raw = pd.read_csv("fertility_rate.csv", skiprows=4)

print("=== Data Loaded Successfully ===")
print(f"GNI data shape: {gni_raw.shape}")  # Shows (rows, columns)
print(f"Fertility data shape: {fertility_raw.shape}")

# ========================================
# STEP 2: CLEAN GNI DATA
# ========================================

# World Bank data is in "wide format": one row per country, columns are years
# We need to convert to "long format": one row per country-year combination

# Get all columns that are years (e.g., "1960", "1961",..., "2023")
year_columns = [col for col in gni_raw.columns if col.isdigit()]

print(f"\nYear range in data: {min(year_columns)} - {max(year_columns)}")

# Reshape data from wide to long format using melt()
# Before: Country | 1960 | 1961 | 1962 |...
# After:  Country | Year | GNI
gni_clean = gni_raw.melt(
    id_vars=['Country Name', 'Country Code'],  # Keep these columns as-is
    value_vars=year_columns,                   # Convert year columns to rows
    var_name='year',                           # New column name for years
    value_name='gni_per_capita'                # New column name for values
)

# Rename columns to simpler names
gni_clean = gni_clean.rename(columns={
    'Country Name': 'country',
    'Country Code': 'country_code'
})

# Convert year to number (was text like "2023")
gni_clean['year'] = pd.to_numeric(gni_clean['year'])

# Convert GNI to number, replace invalid values with NaN
gni_clean['gni_per_capita'] = pd.to_numeric(gni_clean['gni_per_capita'], errors='coerce')

# Keep only recent years (2015 onwards) for better data quality
gni_clean = gni_clean[gni_clean['year'] >= 2015].copy()

# Remove rows where GNI is missing (NaN)
gni_clean = gni_clean.dropna(subset=['gni_per_capita'])

# ========================================
# STEP 3: CLEAN FERTILITY DATA (same process)
# ========================================

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

# ========================================
# STEP 4: FIND MOST RECENT YEAR
# ========================================

# Find the latest year that has data in both datasets
latest_year_gni = int(gni_clean['year'].max())
latest_year_fertility = int(fertility_clean['year'].max())
analysis_year = min(latest_year_gni, latest_year_fertility)  # Use the earlier one

print(f"\n>>> Using data from year: {analysis_year}")

# ========================================
# STEP 5: MERGE DATASETS
# ========================================

# Combine GNI and fertility data
# inner join = only keep countries that appear in BOTH datasets
combined_data = pd.merge(
    gni_clean[gni_clean['year'] == analysis_year],      # Filter to analysis year
    fertility_clean[fertility_clean['year'] == analysis_year],
    on=['country', 'country_code', 'year'],  # Match on these columns
    how='inner'  # Only keep matches
)

print(f">>> Total countries with data: {len(combined_data)}")

# ========================================
# STEP 6: REMOVE REGIONAL AGGREGATES
# ========================================

# World Bank data includes aggregates like "World", "Africa", "High income"
# We want only actual countries, so remove these

aggregates_to_remove = [
    'World', 'Arab World', 'Africa', 'East Asia', 'Europe', 'European Union',
    'High income', 'Low income', 'Middle income', 'Lower middle income', 'Upper middle income',
    'OECD', 'Sub-Saharan', 'Latin America', 'Caribbean', 'South Asia', 'North America',
    'Central Europe', 'Pacific', 'IDA', 'IBRD', 'Fragile', 'Heavily indebted',
    'Least developed', 'Small states', 'Post-demographic', 'Pre-demographic',
    'Early-demographic', 'Late-demographic', 'Eastern', 'Western', 'Southern', 'Northern'
]

# Filter out rows where country name contains any of these terms
combined_data = combined_data[
    ~combined_data['country'].str.contains('|'.join(aggregates_to_remove), case=False, na=False)
].copy()

print(f">>> After removing aggregates: {len(combined_data)} countries")

# ========================================
# STEP 7: CLASSIFY COUNTRIES INTO 3 CATEGORIES
# ========================================

# Define country lists based on UN classification

# DEVELOPED COUNTRIES (from Table A - your UN document)
developed_countries = [
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
    "Australia", "Japan", "New Zealand", "Korea, Rep."
]

# TRANSITIONING COUNTRIES (from Table B - Economies in Transition)
transitioning_countries = [
    # South-Eastern Europe
    "Albania", "Bosnia and Herzegovina", "Montenegro", "North Macedonia", "Serbia",
    # Commonwealth of Independent States
    "Armenia", "Azerbaijan", "Belarus", "Georgia", "Kazakhstan", "Kyrgyz Republic",
    "Moldova", "Russian Federation", "Tajikistan", "Turkmenistan", "Ukraine", "Uzbekistan"
]

# Function to classify each country
def classify_country(country_name):
    """
    Classify country into Developed, Transitioning, or Developing
    
    Args:
        country_name: Name of the country (string)
    
    Returns:
        Category: "Developed", "Transitioning", or "Developing"
    """
    # Standardize country name for matching
    name = str(country_name).strip()
    
    # Handle special cases (World Bank uses different names)
    if 'Korea, Rep' in name:
        name = 'Korea, Rep.'
    elif 'Czech Republic' in name:
        name = 'Czechia'
    elif 'Slovak Republic' in name:
        name = 'Slovakia'
    elif 'Kyrgyz' in name:
        name = 'Kyrgyz Republic'
    elif 'Russian' in name:
        name = 'Russian Federation'
    
    # Check which category the country belongs to
    if name in developed_countries or country_name in developed_countries:
        return 'Developed'
    elif name in transitioning_countries or country_name in transitioning_countries:
        return 'Transitioning'
    else:
        return 'Developing'  # Everything else is developing

# Apply classification to all countries
combined_data['category'] = combined_data['country'].apply(classify_country)

# ========================================
# STEP 8: DISPLAY SUMMARY
# ========================================

print("\n=== Countries by Category ===")
print(combined_data['category'].value_counts())

# Show which countries are in each category
print("\n=== Country Distribution ===")
for category in ['Developed', 'Transitioning', 'Developing']:
    countries = sorted(combined_data[combined_data['category'] == category]['country'].unique())
    print(f"\n{category} ({len(countries)} countries):")
    # Print first 10 countries as examples
    print(", ".join(countries[:10]))
    if len(countries) > 10:
        print(f"... and {len(countries) - 10} more")

# ========================================
# STEP 9: CALCULATE CORRELATIONS
# ========================================

# Overall correlation
correlation_overall = combined_data['gni_per_capita'].corr(combined_data['total_fertility_rate'])
print(f"\n=== Overall Correlation: {correlation_overall:.3f} ===")

# Correlation by category
print("\n=== Correlation by Category ===")
for category in ['Developed', 'Transitioning', 'Developing']:
    data = combined_data[combined_data['category'] == category]
    if len(data) > 1:  # Need at least 2 points for correlation
        corr = data['gni_per_capita'].corr(data['total_fertility_rate'])
        print(f"{category}: {corr:.3f} (n={len(data)} countries)")

# ========================================
# STEP 10: CREATE VISUALIZATION
# ========================================

# Create figure with specific size (width=16 inches, height=10 inches)
fig, ax = plt.subplots(figsize=(16, 10))

# Define colors for each category
colors = {
    'Developed': '#2ECC71',      # Green
    'Transitioning': '#F39C12',  # Orange
    'Developing': '#E74C3C'      # Red
}

# Plot each category separately
for category in ['Developed', 'Transitioning', 'Developing']:
    # Filter data for this category
    data = combined_data[combined_data['category'] == category]
    
    # Create scatter plot
    ax.scatter(
        data['gni_per_capita'],           # X-axis: GNI
        data['total_fertility_rate'],     # Y-axis: Fertility rate
        label=f'{category} ({len(data)})', # Legend label with count
        color=colors[category],           # Color from dictionary
        s=100,                            # Size of points
        alpha=0.6,                        # Transparency (0=invisible, 1=solid)
        edgecolors='white',               # White border around points
        linewidth=1.5                     # Border thickness
    )

# ========================================
# STEP 11: ADD REGRESSION LINE
# ========================================

# Get all data points as arrays
x = combined_data['gni_per_capita'].values
y = combined_data['total_fertility_rate'].values

# Calculate linear regression
# Returns: slope, intercept, r-value, p-value, standard error
slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

# Create smooth line for plotting
x_line = np.linspace(x.min(), x.max(), 100)  # 100 evenly spaced points
y_line = slope * x_line + intercept          # Calculate y = mx + b

# Plot regression line
ax.plot(
    x_line, y_line, 
    color='#2C3E50',           # Dark gray
    linewidth=2.5,             # Thick line
    linestyle='--',            # Dashed line
    label=f'Overall Trend (r={correlation_overall:.3f})',  # Show correlation
    zorder=1                   # Draw below scatter points
)

# ========================================
# STEP 12: STYLE THE PLOT
# ========================================

# Axis labels
ax.set_xlabel('GNI per Capita (USD, Atlas method)', 
              fontsize=14, fontweight='bold')
ax.set_ylabel('Total Fertility Rate (births per woman)', 
              fontsize=14, fontweight='bold')

# Main title
ax.set_title('Economic Development and Fertility Rates by Country Category',
             fontsize=18, fontweight='bold', pad=20)

# Subtitle
plt.suptitle(
    f'Developed, Transitioning, and Developing Countries ({analysis_year}) | n={len(combined_data)} countries',
    fontsize=13, color='#555555', y=0.97
)

# Format x-axis to show dollar signs and commas
# Example: 50000 → $50,000
ax.xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f'${x:,.0f}')
)

# Add grid for easier reading
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)

# Add legend (box showing what each color means)
ax.legend(
    loc='upper right',      # Position
    frameon=True,           # Show box around legend
    shadow=True,            # Add shadow
    fontsize=12,            # Text size
    title='Country Category',  # Legend title
    title_fontsize=13
)

# Add data source caption at bottom
plt.figtext(
    0.99, 0.01,  # Position (x, y) - bottom right
    'Source: World Bank World Development Indicators',
    ha='right',  # Horizontal alignment
    fontsize=10, 
    style='italic', 
    color='gray'
)

# Set background color
ax.set_facecolor('#FAFAFA')  # Very light gray

# Adjust layout to prevent overlapping
plt.tight_layout()

# ========================================
# STEP 13: SAVE AND DISPLAY
# ========================================

# Save as high-resolution PNG
output_file = 'fertility_gni_three_categories.png'
plt.savefig(
    output_file, 
    dpi=300,              # High resolution (300 dots per inch)
    bbox_inches='tight',  # Remove extra whitespace
    facecolor='white'     # White background
)
print(f"\n>>> Plot saved as '{output_file}'")

# Display plot on screen
plt.show()

# ========================================
# STEP 14: SUMMARY STATISTICS
# ========================================

print("\n=== Summary Statistics by Category ===")
summary = combined_data.groupby('category')[['gni_per_capita', 'total_fertility_rate']].agg([
    'count',  # Number of countries
    'mean',   # Average
    'median', # Middle value
    'min',    # Lowest
    'max'     # Highest
])
print(summary)

# ========================================
# STEP 15: TOP/BOTTOM COUNTRIES
# ========================================

# Highest GNI countries
print("\n=== Top 15 Countries by GNI per Capita ===")
top_gni = combined_data.nlargest(15, 'gni_per_capita')[
    ['country', 'category', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
top_gni.index = top_gni.index + 1  # Start numbering from 1
print(top_gni.to_string())

# Lowest fertility countries
print("\n=== Top 15 Countries with Lowest Fertility Rates ===")
low_fertility = combined_data.nsmallest(15, 'total_fertility_rate')[
    ['country', 'category', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
low_fertility.index = low_fertility.index + 1
print(low_fertility.to_string())

# Highest fertility countries
print("\n=== Top 15 Countries with Highest Fertility Rates ===")
high_fertility = combined_data.nlargest(15, 'total_fertility_rate')[
    ['country', 'category', 'gni_per_capita', 'total_fertility_rate']
].reset_index(drop=True)
high_fertility.index = high_fertility.index + 1
print(high_fertility.to_string())

# ========================================
# STEP 16: EXPORT DATA
# ========================================

# Save complete dataset to CSV for further analysis
output_csv = 'all_countries_three_categories.csv'
combined_data_export = combined_data[[
    'country', 'country_code', 'year', 
    'gni_per_capita', 'total_fertility_rate', 'category'
]].sort_values('country')  # Sort alphabetically

combined_data_export.to_csv(output_csv, index=False)
print(f"\n>>> Full dataset exported to '{output_csv}'")

# ========================================
# FINAL SUMMARY
# ========================================

print("\n" + "="*50)
print("=== ANALYSIS COMPLETE ===")
print("="*50)
print(f"Total countries analyzed: {len(combined_data)}")
print(f"  - Developed: {len(combined_data[combined_data['category']=='Developed'])}")
print(f"  - Transitioning: {len(combined_data[combined_data['category']=='Transitioning'])}")
print(f"  - Developing: {len(combined_data[combined_data['category']=='Developing'])}")
print(f"\nOverall correlation: {correlation_overall:.3f}")
print(f"Year analyzed: {analysis_year}")
print("="*50)