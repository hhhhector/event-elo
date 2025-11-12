import streamlit as st
import pandas as pd
import numpy as np

st.title('Event History')

st.markdown("""
<style>
.white-link {
    color: white !important; 
    text-decoration: none !important; 
}

.white-link:hover {
    color: #aaa !important;
    text-decoration: none !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        '<a href="https://discord.gg/74dTEfaNFc" target="_blank" class="white-link">Discord</a>', 
        unsafe_allow_html=True
    )

data = pd.read_json("data/event_history.json")
data['date'] = pd.to_datetime(data['date'])
data = data.rename(columns = {'event' : 'Event', 'date': 'Date', 'player_count': 'Player Count', 'players': 'Players'})
data.set_index('Event', inplace = True)
data2 = pd.concat([data.drop('Players', axis = 1), data['Players'].apply(pd.Series).rename(columns = lambda x: f'{x+1}')], axis=1)

st.write("Event Count:", data.shape[0])
st.write("Latest Event: ```", data.tail(1).index.values[0], '```')

st.dataframe(data[::-1].style.format({"Date": lambda t: t.strftime("%Y-%m-%d")}),
    column_config={
        'Date':st.column_config.DateColumn(),
        'Players':st.column_config.ListColumn(width=1200)
    }
)

with st.expander("Better Format (for Exporting)"):
    st.dataframe(data2[::-1].style.format({"Date": lambda t: t.strftime("%Y-%m-%d")}))

# Event Details

st.header('Event Details')

selected_event = st.selectbox(label="Select Event:", options = reversed(data.index))

details = pd.DataFrame(data.loc[selected_event]['Players']).rename(columns = {0: 'Player'})
details[""] = np.arange(1, len(details) + 1)
details.set_index("", inplace=True)
details.index.name = "Position"

st.write("Date:", data.loc[selected_event]["Date"].strftime("```%Y-%m-%d```"))
st.write("Player Count:", data.loc[selected_event]["Player Count"])

st.dataframe(details, height = round(36.5+35.05*len(details)))
