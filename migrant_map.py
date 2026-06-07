import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase
from matplotlib.patches import Patch, FancyBboxPatch, ConnectionPatch
from matplotlib.gridspec import GridSpec

# ── 데이터 ────────────────────────────────────────────────────────────────────
world = gpd.read_file('/home/claude/world.geojson')
world['iso_use'] = world['ISO_A3'].where(world['ISO_A3'] != '-99', world['ADM0_A3'])

df = pd.read_excel(
    '/mnt/user-data/uploads/API_SM_POP_TOTL_ZS_DS2_en_excel_v2_590.xls', header=3
)

DEVELOPING = [
    'Burundi','Comoros','Congo, Dem. Rep.','Djibouti','Eritrea','Ethiopia',
    'Kenya','Madagascar','Rwanda','Somalia, Fed. Rep.','South Sudan','Uganda','Tanzania',
    'Algeria','Egypt, Arab Rep.','Libya','Mauritania','Morocco','Sudan','Tunisia',
    'Cameroon','Central African Republic','Chad','Congo, Rep.','Equatorial Guinea',
    'Gabon','Sao Tome and Principe','Angola','Botswana','Eswatini','Lesotho','Malawi',
    'Mauritius','Mozambique','Namibia','South Africa','Zambia','Zimbabwe',
    'Benin','Burkina Faso','Cabo Verde',"Cote d'Ivoire",'Gambia, The','Ghana','Guinea',
    'Guinea-Bissau','Liberia','Mali','Niger','Nigeria','Senegal','Sierra Leone','Togo',
    'Brunei Darussalam','Cambodia','China',"Korea, Dem. People's Rep.",'Fiji',
    'Hong Kong SAR, China','Indonesia','Kiribati','Lao PDR','Malaysia','Mongolia',
    'Myanmar','Papua New Guinea','Philippines','Samoa','Singapore','Solomon Islands',
    'Thailand','Timor-Leste','Vanuatu','Viet Nam','Afghanistan','Bangladesh','Bhutan',
    'India','Iran, Islamic Rep.','Maldives','Nepal','Pakistan','Sri Lanka',
    'Bahrain','Iraq','Israel','Jordan','Kuwait','Lebanon','Oman','Qatar','Saudi Arabia',
    'West Bank and Gaza','Syrian Arab Republic','Turkiye','United Arab Emirates',
    'Yemen, Rep.','Bahamas, The','Barbados','Belize','Guyana','Jamaica','Suriname',
    'Trinidad and Tobago','Costa Rica','Cuba','Dominican Republic','El Salvador',
    'Guatemala','Haiti','Honduras','Mexico','Nicaragua','Panama','Argentina','Bolivia',
    'Brazil','Chile','Colombia','Ecuador','Paraguay','Peru','Uruguay','Venezuela, RB'
]

dev_data = df[df['Country Name'].isin(DEVELOPING)][
    ['Country Name','Country Code','2020']
].dropna(subset=['2020']).rename(columns={'2020': 'migrant_pct'})

merged = world.merge(dev_data, left_on='iso_use', right_on='Country Code', how='left')

cmap = mcolors.LinearSegmentedColormap.from_list('white_red', [
    (0.00, '#f7f0f0'),
    (0.10, '#f5c0b0'),
    (0.25, '#e8836a'),
    (0.45, '#c93a2a'),
    (0.70, '#8b1a10'),
    (1.00, '#4a0808'),
])
vmin, vmax = 0, 80

BG = '#1C2331'
NOGRAY = '#2E3447'

# manual 좌표 (110m shapefile에 없는 소국)
manual_coords = {
    'Bahrain':               (50.55, 26.00),
    'Singapore':             (103.82,  1.35),
    'Hong Kong SAR, China':  (114.10, 22.35),
}
short_names = {
    'Hong Kong SAR, China': 'Hong Kong SAR',
    'United Arab Emirates': 'UAE',
}
LABEL_THRESH = 30.0

extreme = dev_data[dev_data['migrant_pct'] > LABEL_THRESH].sort_values(
    'migrant_pct', ascending=False
)

# 각 국가 좌표 수집
coords = {}
for _, row in extreme.iterrows():
    nm, cc, val = row['Country Name'], row['Country Code'], row['migrant_pct']
    if nm in manual_coords:
        coords[nm] = (*manual_coords[nm], val)
    else:
        match = merged[merged['Country Code'] == cc]
        if len(match) and match.iloc[0].geometry:
            cx = match.iloc[0].geometry.centroid.x
            cy = match.iloc[0].geometry.centroid.y
            coords[nm] = (cx, cy, val)

# ── Figure: 상단 전체지도 + 하단 인셋 2개(걸프, 동아시아) ───────────────────
fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor(BG)

gs = GridSpec(2, 3, figure=fig,
              height_ratios=[1.15, 0.85],
              hspace=0.06, wspace=0.06,
              left=0.02, right=0.98,
              top=0.91, bottom=0.09)

ax_world = fig.add_subplot(gs[0, :])    # 상단: 전체 지도
ax_gulf  = fig.add_subplot(gs[1, :2])  # 하단 왼쪽: 걸프 확대
ax_sea   = fig.add_subplot(gs[1, 2])   # 하단 오른쪽: 동아시아 확대

for ax in [ax_world, ax_gulf, ax_sea]:
    ax.set_facecolor(BG)

# ── 공통 지도 그리기 함수 ─────────────────────────────────────────────────────
def draw_map(ax):
    merged[merged['migrant_pct'].isna()].plot(
        ax=ax, color=NOGRAY, edgecolor=BG, linewidth=0.3, zorder=2)
    merged[merged['migrant_pct'].notna()].plot(
        ax=ax, column='migrant_pct', cmap=cmap,
        vmin=vmin, vmax=vmax,
        edgecolor=BG, linewidth=0.3, zorder=3)

draw_map(ax_world)
draw_map(ax_gulf)
draw_map(ax_sea)

# ── 전체 지도: 인셋 박스 표시 + 간단 점만 ────────────────────────────────────
GULF_EXTENT = (29, 62, 14, 36)   # xmin,xmax,ymin,ymax
SEA_EXTENT  = (99, 122, -3, 27)

for extent, color in [(GULF_EXTENT,'#FFD700'),(SEA_EXTENT,'#7FDBFF')]:
    x0,x1,y0,y1 = extent
    rect = plt.Polygon(
        [(x0,y0),(x1,y0),(x1,y1),(x0,y1)],
        fill=False, edgecolor=color, linewidth=1.4, linestyle='--',
        zorder=10, transform=ax_world.transData
    )
    ax_world.add_patch(rect)

# 전체지도에 점만 (레이블 없음)
for nm, (cx,cy,val) in coords.items():
    ax_world.plot(cx, cy, 'o', ms=5, color='white', zorder=8,
                  mec='#ff4444', mew=1.2)

ax_world.set_xlim(-175, 180)
ax_world.set_ylim(-60, 85)
ax_world.set_axis_off()

# ── 걸프 인셋 ─────────────────────────────────────────────────────────────────
ax_gulf.set_xlim(29, 62)
ax_gulf.set_ylim(14, 36)
ax_gulf.set_axis_off()

# 걸프 인셋 테두리
for spine in ax_gulf.spines.values():
    spine.set_edgecolor('#FFD700')
    spine.set_linewidth(1.2)
ax_gulf.set_axis_off()
rect_g = FancyBboxPatch((0,0),1,1,transform=ax_gulf.transAxes,
                         fill=False,edgecolor='#FFD700',linewidth=1.4,
                         boxstyle='square,pad=0',zorder=20,clip_on=False)
ax_gulf.add_patch(rect_g)

# 걸프 레이블 — 좌표 기반 수동 오프셋 (degree)
gulf_labels = {
    'Qatar':                (51.18, 25.32,  5.5,  1.5),
    'United Arab Emirates': (54.21, 23.87,  4.0, -2.5),
    'Kuwait':               (47.60, 29.31, -6.5,  1.2),
    'Bahrain':              (50.55, 26.00, -7.0,  1.5),
    'Jordan':               (36.78, 31.25, -5.5,  1.5),
    'Saudi Arabia':         (44.52, 24.12,  0.0, -4.0),
    'Oman':                 (56.10, 20.61,  4.5, -2.0),
}

for nm, (cx, cy, dx, dy) in gulf_labels.items():
    row = dev_data[dev_data['Country Name'] == nm]
    if row.empty: continue
    val = row.iloc[0]['migrant_pct']
    disp = short_names.get(nm, nm)
    tx, ty = cx+dx, cy+dy

    ax_gulf.plot(cx, cy, 'D', ms=6, color='white', zorder=8,
                 mec='#ff4444', mew=1.2)
    ax_gulf.annotate(
        f'{disp}\n{val:.1f}%',
        xy=(cx, cy), xytext=(tx, ty),
        fontsize=10, fontweight='bold', color='white',
        ha='center', va='center',
        arrowprops=dict(arrowstyle='-', color='white', lw=0.9, alpha=0.7,
                        shrinkA=3, shrinkB=3),
        bbox=dict(boxstyle='round,pad=0.35', fc='#b01a10', ec='none', alpha=0.90),
        zorder=10
    )

ax_gulf.set_title('Gulf Region', color='#FFD700', fontsize=12,
                   fontweight='bold', pad=6, loc='left')

# ── 동아시아 인셋 ─────────────────────────────────────────────────────────────
ax_sea.set_xlim(99, 122)
ax_sea.set_ylim(-3, 27)
ax_sea.set_axis_off()
rect_s = FancyBboxPatch((0,0),1,1,transform=ax_sea.transAxes,
                          fill=False,edgecolor='#7FDBFF',linewidth=1.4,
                          boxstyle='square,pad=0',zorder=20,clip_on=False)
ax_sea.add_patch(rect_s)

sea_labels = {
    'Singapore':             (103.82,  1.35,  5.5,  2.0),
    'Hong Kong SAR, China':  (114.10, 22.35, -6.0,  2.5),
}

for nm, (cx, cy, dx, dy) in sea_labels.items():
    row = dev_data[dev_data['Country Name'] == nm]
    if row.empty: continue
    val = row.iloc[0]['migrant_pct']
    disp = short_names.get(nm, nm)
    tx, ty = cx+dx, cy+dy

    ax_sea.plot(cx, cy, 'D', ms=6, color='white', zorder=8,
                mec='#ff4444', mew=1.2)
    ax_sea.annotate(
        f'{disp}\n{val:.1f}%',
        xy=(cx, cy), xytext=(tx, ty),
        fontsize=10, fontweight='bold', color='white',
        ha='center', va='center',
        arrowprops=dict(arrowstyle='-', color='white', lw=0.9, alpha=0.7,
                        shrinkA=3, shrinkB=3),
        bbox=dict(boxstyle='round,pad=0.35', fc='#b01a10', ec='none', alpha=0.90),
        zorder=10
    )

ax_sea.set_title('East / Southeast Asia', color='#7FDBFF', fontsize=12,
                  fontweight='bold', pad=6, loc='left')

# ── Colorbar ──────────────────────────────────────────────────────────────────
cbar_ax = fig.add_axes([0.18, 0.045, 0.64, 0.018])
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
cb   = ColorbarBase(cbar_ax, cmap=cmap, norm=norm, orientation='horizontal')
cb.set_label('International migrant stock (% of population)  —  Developing economies only',
             color='#CCCCCC', fontsize=10.5, labelpad=5)
plt.setp(cb.ax.xaxis.get_ticklabels(), color='#CCCCCC', fontsize=9)
cb.outline.set_edgecolor('#555566')
cb.ax.axvline(x=(30-vmin)/(vmax-vmin), color='white', lw=1.3, ls='--', alpha=0.8)
cb.ax.text((30-vmin)/(vmax-vmin), 1.8, '30% threshold',
           transform=cb.ax.transAxes, ha='center', va='bottom',
           color='white', fontsize=8.5)

# ── 범례 ──────────────────────────────────────────────────────────────────────
legend_elements = [Patch(facecolor=NOGRAY, edgecolor='#444455',
                          label='Non-developing / No data')]
ax_world.legend(handles=legend_elements, loc='lower left',
                fontsize=9.5, framealpha=0.3, facecolor=BG,
                edgecolor='#555566', labelcolor='#CCCCCC',
                bbox_to_anchor=(0.01, 0.05))

# ── 제목 ──────────────────────────────────────────────────────────────────────
fig.suptitle('International Migrant Stock — Developing Economies  (2020)',
             fontsize=17, fontweight='bold', color='white', y=0.955)
fig.text(0.5, 0.928,
         'Labeled countries (>30%) are extreme outliers  ·  Dashed boxes = zoomed insets below  ·  Source: World Bank',
         ha='center', fontsize=9.5, color='#AAAAAA')

out = '/mnt/user-data/outputs/migrant_map.png'
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
print('Saved:', out)
plt.close()
