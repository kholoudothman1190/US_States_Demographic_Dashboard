import streamlit as st
import geopandas as gpd
import pandas as pd
import json
import plotly.express as px

# Load the states JSON file
file_path = "states.json"
gdf = gpd.read_file(file_path)
# Set the CRS to EPSG:3857
if gdf.crs is None:
    gdf.set_crs(epsg=3857, inplace=True)
gdf = gdf.to_crs(epsg=3857)

# Selecting relevant columns
relevant_columns = ['STATE_NAME', 'STATE_FIPS', 'POP2000', 'POP2003', 'POP00_SQMI', 'WHITE', 'BLACK', 'MALES', 'FEMALES','geometry']
gdf = gdf[relevant_columns]

gdf.rename(columns={
    "STATE_NAME": "State",
    "STATE_FIPS": "State FIPS Code",
    "POP2000": "Population in 2000",
    "POP2003": "Population in 2003",
    "POP00_SQMI": "Population Density (2000)",
    "WHITE": "White Population",
    "BLACK": "Black Population",
    "MALES": "Male Population",
    "FEMALES": "Female Population"
}, inplace=True)

# Streamlit setup
st.set_page_config(layout="wide", page_title="US States Dashboard")
st.title("US States Demographic Dashboard")

st.sidebar.header("Filters")
states = ["All"] + sorted(gdf["State"].unique().tolist())
selected_states = st.sidebar.multiselect("Select States", states, default=["All"])


# Apply filter
gdf_filtered = gdf if "All" in selected_states else gdf[gdf["State"].isin(selected_states)]

#side bar charts

top_states_2003 = gdf_filtered.nlargest(10, "Population in 2003")
fig_pie_pop_2003 = px.pie(top_states_2003, names="State", values="Population in 2003",
                      title="Top 10 States by Population in 2003",
                      color_discrete_sequence=px.colors.sequential.Plasma)
st.sidebar.plotly_chart(fig_pie_pop_2003, use_container_width=True)

top_states_black = gdf_filtered.nlargest(10, "Black Population")
fig_pie_pop_Black = px.pie(top_states_black, names="State", values="Black Population",
                      title="Top 10 States by Black Population",
                      color_discrete_sequence=px.colors.sequential.Plasma)
st.sidebar.plotly_chart(fig_pie_pop_Black, use_container_width=True)

top_states_female = gdf_filtered.nlargest(10, "Female Population")
fig_pie_pop_Female = px.pie(top_states_female, names="State", values="Female Population",
                      title="Top 10 States by Female Population",
                      color_discrete_sequence=px.colors.sequential.Plasma)
st.sidebar.plotly_chart(fig_pie_pop_Female , use_container_width=True)



# Metrics Section
st.subheader("Key Metrics")
st.markdown("""
    <style>
        .metric-box {
            border: 2px solid #440154;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            background-color: #f0f0f0;
            font-size: 18px;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<div class='metric-box'><b>Total Population (2000)</b><br>{gdf_filtered['Population in 2000'].sum():,}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'><b>Total Population (2003)</b><br>{gdf_filtered['Population in 2003'].sum():,}</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-box'><b>Total Male Population</b><br>{gdf_filtered['Male Population'].sum():,}</div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-box'><b>Total Female Population</b><br>{gdf_filtered['Female Population'].sum():,}</div>", unsafe_allow_html=True)


# Tabs
tab1, tab2, tab3 = st.tabs(["Population", "Race Distribution", "Gender Distribution"])

with tab1:
    st.subheader("Population Data and Maps")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 States by Population")
        top_states = gdf_filtered.nlargest(10, "Population in 2003").reset_index()
        st.dataframe(top_states[["State", "Population in 2000", "Population in 2003"]])
        
    
    with col2:
        top_states = gdf_filtered.nlargest(10, "Population in 2000").reset_index()
        fig_bar_pop_2000 = px.bar(top_states,x="State",
                y="Population in 2000",title="Top 10 States by Population in 2000",
                color="State",width=550,color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig_bar_pop_2000)

        
    fig_pop2000 = px.choropleth_mapbox(gdf_filtered, geojson=gdf_filtered.geometry, locations=gdf_filtered.index,
                                       color="Population in 2000",
                                       color_continuous_scale="Viridis_r",
                                       mapbox_style="carto-positron",
                                       zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                                       opacity=0.5,height=600,width=1100,
                                       title="Population in 2000",
                                       hover_name="State",
                                       hover_data={"Population in 2000":":,.1f"})
    fig_pop2000.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_pop2000)
    fig_pop2003 = px.scatter_mapbox(gdf,
                                    lat=gdf.centroid.y,
                                    lon=gdf.centroid.x,
                                    size="Population in 2003",
                                    color="Population in 2003",
                                    color_continuous_scale="Viridis_r",
                                    size_max=50,zoom=3,height=600,width=1100,
                                    center={"lat": 37.0902, "lon": -95.7129},
                                    mapbox_style="carto-positron",
                                    title="Population in 2003 (Bubble Map)",
                                    hover_name="State",hover_data={"Population in 2003":":,.1f"})
    fig_pop2003.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_pop2003)


with tab2:
    st.subheader("Race Distribution Data and Maps")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 States by Race Population")
        top_race_states = gdf_filtered.nlargest(10, "White Population").reset_index()
        st.dataframe(top_race_states[["State", "White Population", "Black Population"]])
       
    with col2:
        fig_bar_race = px.bar(top_race_states, x="State", y="White Population",
            title="Top 10 States by White Population",color="State",width=550
            ,color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig_bar_race)
    
    fig_black = px.choropleth_mapbox(gdf_filtered, geojson=gdf_filtered.geometry, locations=gdf_filtered.index,
                                     color="Black Population",
                                     color_continuous_scale="Viridis_r",
                                     mapbox_style="carto-positron",
                                     zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                                     opacity=0.5,height=600,width=1100,
                                     title="Black Population",
                                     hover_name="State",
                                     hover_data={"Black Population":":,.1f"})
    fig_black.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_black)
    fig_white = px.scatter_mapbox(gdf,
                                  lat=gdf.centroid.y,lon=gdf.centroid.x,
                                  size="White Population",color="White Population",
                                  color_continuous_scale="Viridis_r",
                                  size_max=50,zoom=3,height=600,width=1100,
                                  center={"lat": 37.0902, "lon": -95.7129},
                                  mapbox_style="carto-positron",
                                  title="White Population (Bubble Map)",
                                  hover_name="State",hover_data={"White Population":":,.1f"})
    fig_white.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_white)

with tab3:
    st.subheader("Gender Distribution Data and Maps")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 States by Gender Population")
        top_gender_states = gdf_filtered.nlargest(10, "Male Population").reset_index()
        st.dataframe(top_gender_states[["State", "Male Population", "Female Population"]])
    
    with col2:
        fig_bar_gender = px.bar(top_gender_states,x="State",y="Male Population",
            title="Top 10 States by Male Population",color="State",width=550
            ,color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig_bar_gender)
        
    fig_males = px.choropleth_mapbox(gdf_filtered, geojson=gdf_filtered.geometry, locations=gdf_filtered.index,
                                     color="Male Population",
                                     color_continuous_scale="Viridis_r",
                                     mapbox_style="carto-positron",
                                     zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                                     opacity=0.5,height=600,width=1100,
                                     hover_name="State",hover_data={"Male Population":":,.1f"},
                                     title="Male Population")
    fig_males.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_males)
    fig_females = px.scatter_mapbox(gdf,
                                    lat=gdf.centroid.y,lon=gdf.centroid.x,
                                    size="Female Population",color="Female Population",
                                    color_continuous_scale="Viridis_r",
                                    size_max=50,zoom=3,
                                    height=600,width=1100,
                                    center={"lat": 37.0902, "lon": -95.7129},
                                    mapbox_style="carto-positron",
                                    title="Female Population (Bubble Map)",
                                    hover_name="State",
                                    hover_data={"Female Population":":,.1f"})
    fig_females.update_layout(margin=dict(l=25, r=25, t=25, b=25))
    st.plotly_chart(fig_females)
