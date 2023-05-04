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

#%%
deta = Deta(st.secrets["data_key"])
drive = deta.Drive("earth")

#%%
# Get the list of files in the drive
files = drive.list()
file_list = files['names']
# %%
# get file_name from streamlit selectbox
file_name = st.selectbox("Select a file", file_list)
file_stream = drive.get(file_name)

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
        st.success(f"Finished downloading {file_name}")

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
# plot df using streamlit
st.map(df)

# %%
# preview df
st.dataframe(df)

#%%
st.download_button(
    label="Download data as CSV",
    data=df.to_csv().encode("utf-8"),
    file_name="DE_tower.csv",
)
