import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

df = pd.read_excel(
    '/mnt/user-data/uploads/API_SM_POP_TOTL_ZS_DS2_en_excel_v2_590.xls',
    header=3
)

DEVELOPED = [
    "Canada", "United States", "Australia", "Japan", "New Zealand", "Korea, Rep.",
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
    "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg",
    "Malta", "Netherlands", "Poland", "Portugal", "Romania", "Slovak Republic",
    "Slovenia", "Spain", "Sweden", "Iceland", "Norway", "Switzerland", "United Kingdom"
]
TRANSITION = [
    "Albania", "Bosnia and Herzegovina", "Montenegro", "North Macedonia", "Serbia",
    "Armenia", "Azerbaijan", "Belarus", "Georgia", "Kazakhstan", "Kyrgyz Republic",
    "Moldova", "Russian Federation", "Tajikistan", "Turkmenistan", "Ukraine", "Uzbekistan"
]
DEVELOPING = [
    "Burundi", "Comoros", "Congo, Dem. Rep.", "Djibouti", "Eritrea", "Ethiopia",
    "Kenya", "Madagascar", "Rwanda", "Somalia, Fed. Rep.", "South Sudan", "Uganda", "Tanzania",
    "Algeria", "Egypt, Arab Rep.", "Libya", "Mauritania", "Morocco", "Sudan", "Tunisia",
    "Cameroon", "Central African Republic", "Chad", "Congo, Rep.", "Equatorial Guinea",
    "Gabon", "Sao Tome and Principe",
    "Angola", "Botswana", "Eswatini", "Lesotho", "Malawi", "Mauritius",
    "Mozambique", "Namibia", "South Africa", "Zambia", "Zimbabwe",
    "Benin", "Burkina Faso", "Cabo Verde", "Cote d'Ivoire", "Gambia, The",
    "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Niger",
    "Nigeria", "Senegal", "Sierra Leone", "Togo",
    "Brunei Darussalam", "Cambodia", "China", "Korea, Dem. People's Rep.",
    "Fiji", "Hong Kong SAR, China", "Indonesia", "Kiribati",
    "Lao PDR", "Malaysia", "Mongolia", "Myanmar",
    "Papua New Guinea", "Philippines", "Samoa", "Singapore", "Solomon Islands",
    "Thailand", "Timor-Leste", "Vanuatu", "Viet Nam",
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Iran, Islamic Rep.",
    "Maldives", "Nepal", "Pakistan", "Sri Lanka",
    "Bahrain", "Iraq", "Israel", "Jordan", "Kuwait", "Lebanon",
    "Oman", "Qatar", "Saudi Arabia", "West Bank and Gaza",
    "Syrian Arab Republic", "Turkiye", "United Arab Emirates", "Yemen, Rep.",
    "Bahamas, The", "Barbados", "Belize", "Guyana", "Jamaica",
    "Suriname", "Trinidad and Tobago",
    "Costa Rica", "Cuba", "Dominican Republic", "El Salvador", "Guatemala",
    "Haiti", "Honduras", "Mexico", "Nicaragua", "Panama",
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
    "Paraguay", "Peru", "Uruguay", "Venezuela, RB"
]

YEAR = '2020'

def get_vals(countries):
    sub = df[df['Country Name'].isin(countries)][['Country Name', YEAR]].dropna()
    return sub['Country Name'].tolist(), sub[YEAR].tolist()

def iqr_fence(arr):
    q1, q3 = np.percentile(arr, [25, 75])
    return q3 + 1.5 * (q3 - q1)

dev_names,   dev_vals   = get_vals(DEVELOPED)
trans_names, trans_vals = get_vals(TRANSITION)
devel_names, devel_vals = get_vals(DEVELOPING)

groups = [
    ('Developed economies',     dev_vals,   dev_names,   '#2E7BB5', '#A8C8E8'),
    ('Economies in transition', trans_vals, trans_names, '#1A8C6A', '#8FD4BA'),
    ('Developing economies',    devel_vals, devel_names, '#C94F2A', '#F0A98A'),
]

# n에 비례한 violin max half-width 설정
# n: 37, 17, 124  →  비율 정규화 후 0.20~0.42 범위로 매핑
all_ns   = [len(dev_vals), len(trans_vals), len(devel_vals)]
n_min, n_max = min(all_ns), max(all_ns)
VW_MIN, VW_MAX = 0.18, 0.42
def n_to_vw(n):
    return VW_MIN + (n - n_min) / (n_max - n_min) * (VW_MAX - VW_MIN)

vw_list = [n_to_vw(n) for n in all_ns]

Y_MAX = 85
Y_MIN = -1
rng   = np.random.default_rng(42)

fig, axes = plt.subplots(1, 3, figsize=(17, 11), sharey=True)
fig.patch.set_facecolor('#FAFAF8')

for gi, (ax, (label, vals, names, color_dark, color_light)) in \
        enumerate(zip(axes, groups)):

    ax.set_facecolor('#FAFAF8')
    vals_arr = np.array(vals)
    n        = len(vals_arr)
    VW       = vw_list[gi]   # n에 비례한 violin 폭
    fence    = iqr_fence(vals_arr)
    out_mask = vals_arr > fence
    out_idx  = np.where(out_mask)[0]
    has_out  = len(out_idx) > 0

    violin_top = vals_arr.max() + 0.5

    # ── KDE ───────────────────────────────────────────────────────────────────
    kde    = gaussian_kde(vals_arr, bw_method=0.35)
    y_pts  = np.linspace(0, violin_top, 800)
    dens   = kde(y_pts)
    dens_n = dens / dens.max()   # 0~1 정규화, 최대폭 = VW

    ax.fill_betweenx(y_pts,  dens_n * VW, -dens_n * VW,
                     color=color_light, alpha=0.55, zorder=2)
    ax.plot( dens_n * VW, y_pts, color=color_dark, lw=1.5, zorder=3)
    ax.plot(-dens_n * VW, y_pts, color=color_dark, lw=1.5, zorder=3)

    # 상단 닫기
    top_hw = dens_n[-1] * VW
    ax.plot([-top_hw, top_hw], [violin_top, violin_top],
            color=color_dark, lw=1.5, zorder=3)

    # ── Scatter: 각 점의 jitter를 그 y에서의 violin 폭 안으로 클리핑 ─────────
    # 먼저 넉넉한 후보 jitter 생성 후 violin 폭 내로 클리핑
    raw_jitter = rng.uniform(-1, 1, size=n)  # 방향만 결정
    clipped_jitter = np.zeros(n)

    for k, (v, rj) in enumerate(zip(vals_arr, raw_jitter)):
        # 해당 y에서 violin half-width
        hw = float(np.interp(v, y_pts, dens_n)) * VW
        hw = max(hw, 0.003)          # 최솟값 보장
        scale = hw * 0.88            # 경계에서 살짝 안쪽
        clipped_jitter[k] = rj * scale

    # 비-아웃라이어 점
    ax.scatter(clipped_jitter[~out_mask], vals_arr[~out_mask],
               s=22, color=color_dark, alpha=0.65,
               linewidths=0.35, edgecolors='white', zorder=6)

    # 아웃라이어 점 (다이아몬드)
    if has_out:
        ax.scatter(clipped_jitter[out_mask], vals_arr[out_mask],
                   s=34, color=color_dark, alpha=0.92,
                   linewidths=0.5, edgecolors='white', zorder=6, marker='D')

    # ── 아웃라이어 레이블 (40% 초과만, 겹침 방지) ────────────────────────────
    LABEL_FS   = 9.5
    LABEL_THRESH = 40.0      # 이 값 초과만 이름 표시
    y_per_inch = (Y_MAX - Y_MIN) / (11 * 0.74)
    label_h    = LABEL_FS / 72 * y_per_inch * 1.8

    out_sorted   = sorted(out_idx, key=lambda i: vals_arr[i], reverse=True)
    # 레이블 표시 대상: 40% 초과
    label_targets = [i for i in out_sorted if vals_arr[i] > LABEL_THRESH]

    # side 교대 배정 (레이블 대상만)
    side_map = {i: ('right' if rank % 2 == 0 else 'left')
                for rank, i in enumerate(label_targets)}

    # 초기 label y = 실제 데이터 y
    label_y = {i: float(vals_arr[i]) for i in label_targets}

    # side별 겹침 방지
    for side in ['right', 'left']:
        grp = [i for i in label_targets if side_map[i] == side]
        for k in range(1, len(grp)):
            prev_i = grp[k - 1]
            curr_i = grp[k]
            if label_y[prev_i] - label_y[curr_i] < label_h:
                label_y[curr_i] = label_y[prev_i] - label_h

    for rank, i in enumerate(label_targets):
        v    = float(vals_arr[i])
        ly   = label_y[i]
        nm   = names[i]
        xj   = clipped_jitter[i]
        side = side_map[i]
        hw   = float(np.interp(v, y_pts, dens_n)) * VW

        if side == 'right':
            xtext = min(xj + 0.05, hw * 0.90)
            ha    = 'left'
        else:
            xtext = max(xj - 0.05, -hw * 0.90)
            ha    = 'right'

        ax.annotate(
            f'{nm}  {v:.1f}%',
            xy=(xj, v),
            xytext=(xtext, ly),
            fontsize=LABEL_FS,
            fontweight='semibold',
            color=color_dark,
            ha=ha, va='center',
            arrowprops=dict(arrowstyle='-', color=color_dark,
                            lw=0.65, alpha=0.45, shrinkA=0, shrinkB=0),
            bbox=dict(boxstyle='round,pad=0.2', fc='#FAFAF8',
                      ec='none', alpha=0.92),
            zorder=9,
            clip_on=False
        )

    # ── Stats box: 제목 바로 아래, ax 내부 상단 ──────────────────────────────
    med     = np.median(vals_arr)
    mean_v  = np.mean(vals_arr)
    q1, q3  = np.percentile(vals_arr, [25, 75])
    n_out   = len(out_idx)
    out_str = f'{n_out} outlier{"s" if n_out!=1 else ""}' if n_out else 'no outliers'
    stats_txt = (f'n={n}   median={med:.1f}%   mean={mean_v:.1f}%\n'
                 f'IQR: {q1:.1f}–{q3:.1f}%   fence: {fence:.1f}% ({out_str})')

    ax.text(0.5, 0.997, stats_txt,
            transform=ax.transAxes,
            fontsize=10.0, va='top', ha='center',
            color='#3A3A38', linespacing=1.6,
            bbox=dict(boxstyle='round,pad=0.5', fc='white',
                      ec='#DDDDDA', lw=0.7, alpha=0.95),
            zorder=10)

    # ── Axes styling ──────────────────────────────────────────────────────────
    ax.set_xlim(-0.52, 0.52)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_xticks([])
    for spine in ['bottom', 'top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#CCCCCA')
    ax.spines['left'].set_linewidth(0.6)
    ax.tick_params(axis='y', colors='#666662', labelsize=11, length=3)
    ax.yaxis.grid(True, color='#E8E8E5', linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title(label, fontsize=14, fontweight='bold', color='#2A2A28',
                 pad=10, loc='center')

axes[0].set_ylabel('International migrant stock (% of population)',
                    fontsize=12, color='#444440', labelpad=10)
for ax in axes[1:]:
    ax.tick_params(labelleft=False)

fig.suptitle('International Migrant Stock by Economy Group',
             fontsize=18, fontweight='bold', color='#1A1A18', y=0.99)
fig.text(0.5, 0.957,
         'Share of international migrants in total population · Year: 2020 · Source: World Bank',
         ha='center', fontsize=11, color='#888884')
fig.text(0.5, 0.012,
         '◆ = statistical outlier (IQR method)  ·  Violin width proportional to sample size',
         ha='center', fontsize=10, color='#AAAAAA', style='italic')

plt.tight_layout(rect=[0, 0.03, 1, 0.955])
plt.subplots_adjust(wspace=0.09)

out = '/mnt/user-data/outputs/migrant_stock_violin.png'
plt.savefig(out, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
print('Saved:', out)
plt.close()
