import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import contextily as cx

# 1. Page Configuration
st.set_page_config(
    page_title="Minard's 1812 Campaign Map",
    page_icon="🗺️",
    layout="wide"
)

st.title("Interactive Recreation of Minard's 1812 Napoleon Campaign Map")
st.markdown(
    "A Streamlit implementation reproducing Charles Joseph Minard's classic 1869 visualization "
    "of Napoleon's Russian Campaign (1812–1813)."
)

# 2. Interactive Sidebar Controls
st.sidebar.header("Map Settings")
show_basemap = st.sidebar.checkbox("Show CartoDB Voyager Basemap", value=True)
scale_factor = st.sidebar.slider(
    "Troop Line Width Scale Factor",
    min_value=5000,
    max_value=20000,
    value=12000,
    step=1000,
    help="Adjusts the line width scaling ratio relative to troop count."
)

# 3. Data Loading (Cached for performance)
@st.cache_data
def load_minard_data():
    cities = pd.DataFrame([
        ('Kowno', 24.0, 54.9), ('Wilna', 25.3, 54.7), ('Smorgoni', 26.4, 54.5),
        ('Molodezno', 26.9, 54.3), ('Minsk', 27.5, 53.9), ('Studienska', 28.3, 54.3),
        ('Botr', 29.1, 54.3), ('Orscha', 30.4, 54.5), ('Mohilow', 30.4, 53.9),
        ('Witebsk', 30.2, 55.1), ('Polotsk', 28.8, 55.5), ('Gloubokoe', 27.7, 55.1),
        ('Dorogobouge', 33.2, 54.9), ('Smolensk', 32.0, 54.8), ('Wixma', 34.3, 55.2),
        ('Chjat', 35.5, 55.5), ('Mojaisk', 36.8, 55.5), ('Moscou', 37.6, 55.8),
        ('Tarantino', 37.0, 55.1), ('Malo-jarosewli', 36.5, 55.0)
    ], columns=['city', 'lon', 'lat'])

    adv_main = pd.DataFrame([
        (24.0, 54.9, 422000), (25.3, 54.7, 400000), (26.4, 54.5, 300000),
        (30.2, 55.1, 175000), (32.0, 54.8, 145000), (33.2, 54.9, 127000),
        (35.5, 55.5, 127000), (36.8, 55.5, 100000), (37.6, 55.8, 100000)
    ], columns=['lon', 'lat', 'survivors'])

    adv_polotsk = pd.DataFrame([
        (25.3, 54.7, 60000), (27.7, 55.1, 60000), (28.8, 55.5, 33000)
    ], columns=['lon', 'lat', 'survivors'])

    adv_detachment = pd.DataFrame([
        (24.1, 55.0, 24.3, 55.7, 22000)
    ], columns=['lon1', 'lat1', 'lon2', 'lat2', 'survivors'])

    ret_main = pd.DataFrame([
        (37.6, 55.8, 100000), (37.0, 55.1, 96000), (36.5, 55.0, 96000),
        (36.8, 55.35, 87000), (35.5, 55.35, 87000), (34.3, 55.05, 55000),
        (33.2, 54.75, 37000), (32.0, 54.65, 24000), (30.4, 54.4, 20000),
        (29.1, 54.2, 50000), (28.3, 54.2, 28000), (26.9, 54.2, 12000),
        (26.4, 54.3, 14000), (25.3, 54.5, 8000), (24.0, 54.3, 4000)
    ], columns=['lon', 'lat', 'survivors'])

    ret_polotsk = pd.DataFrame([
        (28.8, 55.5, 30000), (29.1, 54.2, 30000)
    ], columns=['lon', 'lat', 'survivors'])

    ret_detachment = pd.DataFrame([
        (24.1, 55.6, 24.0, 54.3, 6000)
    ], columns=['lon1', 'lat1', 'lon2', 'lat2', 'survivors'])

    temps = pd.DataFrame([
        (37.6, 0, '18 Oct', 'Pluie 24 8bre', 55.8),
        (36.0, -9, '24 Oct', '', 55.1),
        (33.2, -21, '09 Nov', '', 54.75),
        (32.0, -11, '14 Nov', '', 54.65),
        (29.2, -20, '28 Nov', '', 54.2),
        (28.5, -24, '01 Dec', '', 54.2),
        (27.2, -30, '06 Dec', '', 54.25),
        (26.8, -26, '07 Dec', 'Les Cosaques passent au galop\nle Niemen gelé', 54.25)
    ], columns=['lon', 'temp', 'date', 'note', 'ret_lat'])

    return cities, adv_main, adv_polotsk, adv_detachment, ret_main, ret_polotsk, ret_detachment, temps

cities, adv_main, adv_polotsk, adv_detachment, ret_main, ret_polotsk, ret_detachment, temps = load_minard_data()

# 4. Figure & Map Construction
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9), sharex=True, gridspec_kw={'height_ratios': [3.2, 1]})

ax1.set_xlim(23.5, 38.5)
ax1.set_ylim(53.5, 56.5)
ax1.get_yaxis().set_visible(False)

if show_basemap:
    carto_url = "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_40ps_1_7b191fe849f5b1f855fa55f8"
    cx.add_basemap(ax1, crs="EPSG:4326", source=carto_url, zorder=0)

# Temperature Alignment Lines
for _, row in temps.iterrows():
    ax1.plot([row['lon'], row['lon']], [row['ret_lat'], 53.5], color='gray', linestyle='--', linewidth=0.7, zorder=1)
    ax2.plot([row['lon'], row['lon']], [0, row['temp']], color='gray', linestyle='--', linewidth=0.7, zorder=1)

# Retreat Path
for i in range(len(ret_main) - 1):
    lw_val = ret_main.iloc[i, 2] / scale_factor
    ax1.plot(ret_main.iloc[i:i+2, 0], ret_main.iloc[i:i+2, 1], color='black', lw=lw_val, zorder=2, solid_capstyle='round')
    ax1.text(ret_main.iloc[i, 0], ret_main.iloc[i, 1] - 0.18, f"{ret_main.iloc[i, 2]:,}", fontsize=6, zorder=4, color='black', ha='center')

for i in range(len(ret_polotsk) - 1):
    lw_val = ret_polotsk.iloc[i, 2] / scale_factor
    ax1.plot(ret_polotsk.iloc[i:i+2, 0], ret_polotsk.iloc[i:i+2, 1], color='black', lw=lw_val, zorder=2, solid_capstyle='round')

for _, row in ret_detachment.iterrows():
    ax1.plot([row['lon1'], row['lon2']], [row['lat1'], row['lat2']], color='black', lw=row['survivors']/scale_factor, zorder=2)
    ax1.text(row['lon1'], row['lat1'] + 0.05, f"{int(row['survivors']):,}", fontsize=5.5, color='black', ha='center')

# Advance Path
for i in range(len(adv_main) - 1):
    lw_val = adv_main.iloc[i, 2] / scale_factor
    ax1.plot(adv_main.iloc[i:i+2, 0], adv_main.iloc[i:i+2, 1], color='#e8c090', lw=lw_val, zorder=3, solid_capstyle='round')
    ax1.text(adv_main.iloc[i, 0], adv_main.iloc[i, 1] + 0.15, f"{adv_main.iloc[i, 2]:,}", fontsize=6, zorder=4, color='#8b5a2b', ha='center')

for i in range(len(adv_polotsk) - 1):
    lw_val = adv_polotsk.iloc[i, 2] / scale_factor
    ax1.plot(adv_polotsk.iloc[i:i+2, 0], adv_polotsk.iloc[i:i+2, 1], color='#e8c090', lw=lw_val, zorder=3, solid_capstyle='round')

for _, row in adv_detachment.iterrows():
    ax1.plot([row['lon1'], row['lon2']], [row['lat1'], row['lat2']], color='#e8c090', lw=row['survivors']/scale_factor, zorder=3)
    ax1.text(row['lon2'], row['lat2'] + 0.05, f"{int(row['survivors']):,}", fontsize=5.5, color='#8b5a2b', ha='center')

# City Annotations
for _, row in cities.iterrows():
    ax1.text(row['lon'], row['lat'] + 0.04, row['city'], fontfamily='serif', fontstyle='italic', fontsize=7.5, ha='center', va='bottom', zorder=5)

# Distance Scale Bar
scale_x, scale_y = 33.5, 53.8
ax1.plot([scale_x, scale_x + 2.5], [scale_y, scale_y], 'k-', lw=1.2, zorder=6)
for offset, label in zip([0, 0.83, 1.66, 2.5], ['0', '10', '20', '30 leagues']):
    ax1.plot([scale_x + offset, scale_x + offset], [scale_y - 0.03, scale_y + 0.03], 'k-', lw=1.0, zorder=6)
    ax1.text(scale_x + offset, scale_y - 0.08, label, fontsize=6, ha='center', va='top', fontfamily='serif')
ax1.text(scale_x + 1.25, scale_y + 0.06, "Common French Leagues (Map of M. de Fezensac)", fontsize=6.5, ha='center', fontfamily='serif', fontstyle='italic')

# Temperature Subplot
ax2.plot(temps['lon'], temps['temp'], 'k-', linewidth=1.2, zorder=2)
ax2.scatter(temps['lon'], temps['temp'], color='black', s=12, zorder=3)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")
ax2.set_ylim(-35, 2)
ax2.set_title("GRAPHIC TABLE of the temperature in degrees of the Réaumur thermometer below zero", fontsize=9, fontfamily='serif', fontstyle='italic', pad=6)

for _, row in temps.iterrows():
    lbl = f"{row['temp']}° Ré ({row['date']})" if row['temp'] != 0 else "0° (18 Oct)"
    ax2.annotate(lbl, (row['lon'], row['temp']), textcoords="offset points", xytext=(0, -12), ha='center', fontsize=6.5, fontfamily='serif')
    if row['note']:
        ax2.annotate(row['note'], (row['lon'], row['temp']), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=6, fontfamily='serif', fontstyle='italic')

ax2.set_ylabel("Temp (°Ré)", fontsize=8)
ax2.grid(True, linestyle=':', alpha=0.5)
ax2.get_xaxis().set_visible(False)

plt.tight_layout()

# 5. Display Figure in Streamlit
st.pyplot(fig)

