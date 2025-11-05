import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.title('Rating History')
st.caption('I: Inactivity | S: Start')


# Load Data

data = pd.read_parquet('data/rankings.parquet')
data.insert(0, "", range(1, len(data) + 1))
for col in data.select_dtypes(include=['float']).columns:
    data[col] = data[col].round(0)

st.write("Player Count:", data.shape[0])

st.dataframe(
    data,
    column_config={
        "" : st.column_config.NumberColumn(format = "%d.", pinned = True),
        "Avatar" : st.column_config.ImageColumn("", pinned = True),
        "Player" : st.column_config.TextColumn(pinned = True),
        "Rating" : st.column_config.NumberColumn(format = "%f",
            pinned = True),
        "Peak" : st.column_config.NumberColumn(pinned = True),
        "Events" : st.column_config.NumberColumn(pinned = True),
        "I" : st.column_config.NumberColumn(pinned = True),
    },
    hide_index=True,
)

st.download_button("Download Full Data (.csv)", data=pd.read_parquet('data/rankings.parquet').to_csv(), file_name='rating_history.csv')

col1, col2 = st.columns(2)

with col1:
    m = st.number_input("Players", value=10, min_value=1, max_value=len(data))

with col2:
    n = st.number_input("Events", value=30)

plot_data_wide = data.reset_index().drop(
    columns = ["", "Avatar", "Rating", "Peak", "Events", "I", "index"]
).head(m).set_index("Player").T.iloc[-n:,:]
plot_data_wide.reset_index()
plot_data_wide['SortOrder'] = range(len(plot_data_wide))
plot_data_wide = plot_data_wide.reset_index().rename(columns={'index': 'Event'})
plot_data_long = plot_data_wide.melt(
    id_vars=['Event', 'SortOrder'],  
    var_name='Player',            
    value_name='Rating'           
)
player_order = plot_data_long['Player'].unique()


chart = alt.Chart(plot_data_long, height=600).mark_line(point=alt.OverlayMarkDef(size=20), size=1.5).encode(
    
    x=alt.X('Event', 
        sort=alt.SortField('SortOrder')
    ),
    
    y=alt.Y('Rating',
        scale=alt.Scale(domain=[min(plot_data_long["Rating"]) - 100,max(plot_data_long["Rating"]) + 100])
    ),

    color=alt.Color('Player', 
        sort=player_order
    ).scale(scheme='darkmulti'),

    tooltip=['Event', 'Player', 'Rating']

).interactive()


st.altair_chart(chart)