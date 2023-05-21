#%%
import streamlit as st
from deta import Deta
import pandas as pd
import pydeck as pdk
import os

#%%
# set streamlit meta
st.set_page_config(
    page_title="Earth-OSM", 
    page_icon="🌎", 
    # initial_sidebar_state="collapsed"
)

# st.title("EnergiX")
# st.subheader("Für nicht-erneuerbare Energiequellen das X")
st.title("Earth-OSM")
st.subheader("Extract and Visualize Power Infrastructure data from OpenStreetMap")

# add under development in red
st.markdown(
    f'<p style="color:red;">Under development</p>',
    unsafe_allow_html=True,
)

#%%
deta = Deta(st.secrets["data_key"])
drive = deta.Drive("earth")

#%%
# Get the list of files in the drive
files = drive.list()
file_list = files['names']
# %%
# get file_name from streamlit selectbox
file_name = st.selectbox("Select a region", file_list)

#%%
def save_file(file_name):
    file_stream = drive.get(file_name)
    with open(file_name, "wb+") as f:
        for chunk in file_stream.iter_chunks(4096):
            f.write(chunk)
    file_stream.close()

#%%
# save_file with streamlit spinner
if not os.path.exists(file_name):
    with st.spinner(f"Extracting {file_name}"):
        save_file(file_name)
        st.success(f"Finished extracting {file_name}")

#%%
df = pd.read_csv(file_name)
# drop unnamed:0 column
df.drop(df.columns[df.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

# df contain a column lonlat which is list of tuples (lon,lat)
# split lonlat into two columns lon and lat

# convert lonlat to list object
df['lonlat'] = df['lonlat'].apply(lambda x: eval(x))

df['lon'] = df['lonlat'].apply(lambda x: x[0][0])
df['lat'] = df['lonlat'].apply(lambda x: x[0][1])

#%%
df.drop(['lonlat'], axis=1, inplace=True)
df.drop(['other_tags'], axis=1, inplace=True)

#%%
chart_data = df[['lon', 'lat']]

_ZOOM_LEVELS = [360 / (2**i) for i in range(21)]

min_lat = chart_data['lat'].min()
max_lat = chart_data['lat'].max()
min_lon = chart_data['lon'].min()
max_lon = chart_data['lon'].max()
center_lat = (max_lat + min_lat) / 2.0
center_lon = (max_lon + min_lon) / 2.0
range_lon = abs(max_lon - min_lon)
range_lat = abs(max_lat - min_lat)

if range_lon > range_lat:
    longitude_distance = range_lon
else:
    longitude_distance = range_lat

# For small number of points the default zoom level will be used.
zoom_l = 12
for i in range(len(_ZOOM_LEVELS) - 1):
    if _ZOOM_LEVELS[i + 1] < longitude_distance <= _ZOOM_LEVELS[i]:
        zoom_l = i

 

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=df['lat'].mean(),
        longitude=df['lon'].mean(),
        # set zoom level automatically
        zoom=zoom_l,
        pitch=30,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))

# %%
# preview df if check box
if st.checkbox('Show dataframe'):
    st.dataframe(df)

#%%
st.download_button(
    label="Download data as CSV",
    data=df.to_csv().encode("utf-8"),
    file_name="DE_tower.csv",
)


# add powered by earth-osm hyperlink with github icon
earth_osm_url = "https://github.com/pypsa-meets-earth/earth-osm"
st.markdown(
    f'<a href="{earth_osm_url}"><img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="30"></a>'
    f'<a href="{earth_osm_url}">Powered by earth-osm</a>',
    unsafe_allow_html=True,
)
