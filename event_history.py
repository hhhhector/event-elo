import streamlit as st
import pandas as pd
import numpy as np

st.title('Event History')

DATE_COLUMN = 'date'


def load_data():
    data = pd.read_json("data/event_history.json")
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data = load_data()
data = data.rename(columns = {'event' : 'Event', 'date': 'Date', 'participant_count': 'Participant Count', 'participants': 'Participants'})
data.set_index('Event', inplace=True)

st.dataframe(data.style.format({"Date": lambda t: t.strftime("%Y-%m-%d")}))

selected_event = st.selectbox(label="Select:", options = data.index)

details = pd.DataFrame(data.loc[selected_event]['Participants']).rename(columns={0: 'Participant'})
details[""] = np.arange(1, len(details) + 1)
details.set_index("", inplace=True)
st.write("Participant Count:", data.loc[selected_event]["Participant Count"])
st.write("Date:", data.loc[selected_event]["Date"])

st.table(details)