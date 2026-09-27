import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import contextily as cx

# 1. Page Configuration
st.set_page_config(page_title="Minard 1812 Interactive Campaign Map", layout="wide")
st.title("Interactive Recreation of Minard's 1812 Campaign Map")

# 2. Cache Data Initialization
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

    timeline = pd.DataFrame([
        (1, 'Advance', 'Kowno (Crossing Niemen)', '24 Jun 1812', 24.0, 54.9, 422000, None),
        (2, 'Advance', 'Wilna', '30 Jun 1812', 25.3, 54.7, 400000, None),
        (3, 'Advance', 'Smorgoni / Gloubokoe', '18 Jul 1812', 26.4, 54.5, 300000, None),
        (4, 'Advance', 'Witebsk', '28 Jul 1812', 30.2, 55.1, 175000, None),
        (5, 'Advance', 'Smolensk', '18 Aug 1812', 32.0, 54.8, 145000, None),
        (6, 'Advance', 'Dorogobouge', '24 Aug 1812', 33.2, 54.9, 127000, None),
        (7, 'Advance', 'Chjat', '04 Sep 1812', 35.5, 55.5, 127000, None),
        (8, 'Advance', 'Mojaisk (Borodino)', '07 Sep 1812', 36.8, 55.5, 100000, None),
        (9, 'Advance', 'Moscou (Arrival)', '14 Sep 1812', 37.6, 55.8, 100000, None),
        (10, 'Retreat', 'Moscou (Departure)', '18 Oct 1812', 37.6, 55.8, 100000, 0),
        (11, 'Retreat', 'Malo-jarosewli / Tarantino', '24 Oct 1812', 36.5, 55.0, 96000, -9),
        (12, 'Retreat', 'Mojaisk', '28 Oct 1812', 36.8, 55.35, 87000, None),
        (13, 'Retreat', 'Chjat', '31 Oct 1812', 35.5, 55.35, 87000, None),
        (14, 'Retreat', 'Wixma', '03 Nov 1812', 34.3, 55.05, 55000, None),
        (15, 'Retreat', 'Dorogobouge', '09 Nov 1812', 33.2, 54.75, 37000, -21),
        (16, 'Retreat', 'Smolensk', '14 Nov 1812', 32.0, 54.65, 24000, -11),
        (17, 'Retreat', 'Orscha', '20 Nov 1812', 30.4, 54.4, 20000, None),
        (18, 'Retreat', 'Studienska (Berezina)', '28 Nov 1812', 28.3, 54.2, 28000, -20),
        (19, 'Retreat', 'Molodezno', '01 Dec 1812', 26.9, 54.2, 12000, -24),
        (20, 'Retreat', 'Smorgoni', '06 Dec 1812', 26.4, 54.3, 14000, -30),
        (21, 'Retreat', 'Wilna', '07 Dec 1812', 25.3, 54.5, 8000, -26),
        (22, 'Retreat', 'Kowno (Recrossing Niemen)', '13 Dec 1812', 24.0, 54.3, 4000, None)
    ], columns=['step', 'phase', 'stage', 'date', 'lon', 'lat', 'survivors', 'temp'])

    adv_polotsk = pd.DataFrame([
        (25.3, 54.7, 60000), (27.7, 55.1, 60000), (28.8, 55.5, 33000)
    ], columns=['lon', 'lat', 'survivors'])

    adv_detachment = pd.DataFrame([
        (24.1, 55.0, 24.3, 55.7, 22000)
    ], columns=['lon1', 'lat1', 'lon2', 'lat2', 'survivors'])

    ret_polotsk = pd.DataFrame([
        (28.8, 55.5, 30000), (29.1, 54.2, 30000)
    ], columns=['lon', 'lat', 'survivors'])

    ret_detachment = pd.DataFrame([
        (24.1, 55.6, 24.0, 54.3, 6000)
    ], columns=['lon1', 'lat1', 'lon2', 'lat2', 'survivors'])

    return cities, timeline, adv_polotsk, adv_detachment, ret_polotsk, ret_detachment

cities, timeline, adv_polotsk, adv_detachment, ret_polotsk, ret_detachment = load_minard_data()

# 3. Sidebar Configuration
st.sidebar.header("Map Controls")
basemap_provider = st.sidebar.selectbox(
    "Basemap Style",
    ["CartoDB Voyager", "CartoDB Positron", "OpenStreetMap", "Esri WorldImagery", "None"]
)

adv_scale = st.sidebar.slider("Advance Width Scale", 5000, 20000, 12000, 1000)
ret_scale = st.sidebar.slider("Retreat Width Scale", 5000, 20000, 12000, 1000)

# 4. Scrubbing Slider & Metrics
st.markdown("### Campaign Progression Slider")
current_step = st.select_slider(
    "Drag to scrub along the army path:",
    options=timeline['step'].tolist(),
    format_func=lambda x: f"Step {x}: {timeline.loc[timeline['step']==x, 'stage'].values[0]} ({timeline.loc[timeline['step']==x, 'date'].values[0]})"
)

curr_row = timeline[timeline['step'] == current_step].iloc[0]
initial_troops = 422000
current_troops = curr_row['survivors']
loss_pct = ((current_troops - initial_troops) / initial_troops) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Troops Remaining", f"{current_troops:,}", f"{loss_pct:.1f}%")
col2.metric("Phase & Stage", f"{curr_row['phase']} — {curr_row['stage']}")
col3.metric("Date", curr_row['date'])
col4.metric("Temperature", f"{curr_row['temp']}° Ré" if pd.notnull(curr_row['temp']) else "N/A")

# 5. Figure & Filtered Rendering
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9), sharex=True, gridspec_kw={'height_ratios': [3.2, 1]})
ax1.set_xlim(23.5, 38.5)
ax1.set_ylim(53.5, 56.5)
ax1.get_yaxis().set_visible(False)

# Tile mapping
basemap_urls = {
    "CartoDB Voyager": "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_40ps_1_7b191fe849f5b1f855fa55f8",
    "CartoDB Positron": cx.providers.CartoDB.Positron,
    "OpenStreetMap": cx.providers.OpenStreetMap.Mapnik,
    "Esri WorldImagery": cx.providers.Esri.WorldImagery
}
if basemap_provider != "None":
    cx.add_basemap(ax1, crs="EPSG:4326", source=basemap_urls[basemap_provider], zorder=0)

# Filtered path segments
adv_active = timeline[(timeline['step'] <= current_step) & (timeline['phase'] == 'Advance')]
ret_active = timeline[(timeline['step'] <= current_step) & (timeline['phase'] == 'Retreat')]

# Temperature connecting lines
temps = timeline[timeline['temp'].notnull()]
for _, row in temps.iterrows():
    ax1.plot([row['lon'], row['lon']], [row['lat'], 53.5], color='gray', linestyle='--', linewidth=0.7, zorder=1)
    ax2.plot([row['lon'], row['lon']], [0, row['temp']], color='gray', linestyle='--', linewidth=0.7, zorder=1)

# Draw Advance up to current step
if len(adv_active) > 1:
    for i in range(len(adv_active) - 1):
        lw_val = adv_active.iloc[i]['survivors'] / adv_scale
        ax1.plot(adv_active.iloc[i:i+2]['lon'], adv_active.iloc[i:i+2]['lat'], color='#e8c090', lw=lw_val, zorder=3, solid_capstyle='round')
        ax1.text(adv_active.iloc[i]['lon'], adv_active.iloc[i]['lat'] + 0.15, f"{adv_active.iloc[i]['survivors']:,}", fontsize=6, color='#8b5a2b', ha='center', zorder=4)

if current_step >= 3:
    for i in range(len(adv_polotsk) - 1):
        ax1.plot(adv_polotsk.iloc[i:i+2]['lon'], adv_polotsk.iloc[i:i+2]['lat'], color='#e8c090', lw=adv_polotsk.iloc[i]['survivors']/adv_scale, zorder=3)
if current_step >= 1:
    for _, row in adv_detachment.iterrows():
        ax1.plot([row['lon1'], row['lon2']], [row['lat1'], row['lat2']], color='#e8c090', lw=row['survivors']/adv_scale, zorder=3)

# Draw Retreat up to current step
if len(ret_active) > 1:
    for i in range(len(ret_active) - 1):
        lw_val = ret_active.iloc[i]['survivors'] / ret_scale
        ax1.plot(ret_active.iloc[i:i+2]['lon'], ret_active.iloc[i:i+2]['lat'], color='black', lw=lw_val, zorder=2, solid_capstyle='round')
        ax1.text(ret_active.iloc[i]['lon'], ret_active.iloc[i]['lat'] - 0.18, f"{ret_active.iloc[i]['survivors']:,}", fontsize=6, color='black', ha='center', zorder=4)

if current_step >= 17:
    for i in range(len(ret_polotsk) - 1):
        ax1.plot(ret_polotsk.iloc[i:i+2]['lon'], ret_polotsk.iloc[i:i+2]['lat'], color='black', lw=ret_polotsk.iloc[i]['survivors']/ret_scale, zorder=2)
if current_step >= 22:
    for _, row in ret_detachment.iterrows():
        ax1.plot([row['lon1'], row['lon2']], [row['lat1'], row['lat2']], color='black', lw=row['survivors']/ret_scale, zorder=2)

# Marker for current position
ax1.scatter(curr_row['lon'], curr_row['lat'], color='red', s=50, zorder=6)

# City Labels
for _, row in cities.iterrows():
    ax1.text(row['lon'], row['lat'] + 0.04, row['city'], fontfamily='serif', fontstyle='italic', fontsize=7.5, ha='center', va='bottom', zorder=5)

# Temperature Plot
ax2.plot(temps['lon'], temps['temp'], 'k-', linewidth=1.2, zorder=2)
ax2.scatter(temps['lon'], temps['temp'], color='black', s=12, zorder=3)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position("right")
ax2.set_ylim(-35, 2)
ax2.set_title("GRAPHIC TABLE of the temperature in degrees of the Réaumur thermometer below zero", fontsize=9, fontfamily='serif', fontstyle='italic', pad=6)

for _, row in temps.iterrows():
    lbl = f"{row['temp']}° Ré ({row['date']})" if row['temp'] != 0 else "0° (18 Oct)"
    ax2.annotate(lbl, (row['lon'], row['temp']), textcoords="offset points", xytext=(0, -12), ha='center', fontsize=6.5, fontfamily='serif')

ax2.set_ylabel("Temp (°Ré)", fontsize=8)
ax2.grid(True, linestyle=':', alpha=0.5)
ax2.get_xaxis().set_visible(False)

plt.tight_layout()
st.pyplot(fig)