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
    data[col] = data[col].round(0).astype('int64')
players = data["Player"]

player_filter = st.selectbox("Player", options = sorted(players), index=None)
if player_filter is not None:
    start_pos = data.index.get_loc(player_filter.lower().replace("_",""))
else:
    start_pos = 0

string_to_find = player_filter

def highlight_row(row):

    if not string_to_find:
        return [''] * len(row)

    contains_string = row.astype(str).str.contains(string_to_find, case=False).any()
    
    if contains_string:
        style = 'background-color: #0b0a0cff; color: #EAE151; font-weight: bold;'
        return [style] * len(row)
    else:
        return [''] * len(row)

st.dataframe(
    data.iloc[max(0,start_pos - 4) - max(start_pos + 6, data.shape[0]): min(start_pos + 6, data.shape[0]) - min(0,start_pos - 4)].style.apply(
                highlight_row, axis=1
            ).text_gradient(
                cmap='RdYlGn', subset = ['Rating', 'Peak'] + list(data.columns[7:]), axis=None
            ),
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
    height=round(36.5+35.05*10)

)

with st.expander('Full History'):
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
    st.download_button("Download Full History (.csv)", data=pd.read_parquet('data/rankings.parquet').to_csv(), file_name='rating_history.csv')

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