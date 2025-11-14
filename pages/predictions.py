import streamlit as st
import pickle as pkl
import matplotlib
import pandas as pd

st.title('Predictions')
st.caption('EP : Expected Placement\n\nNP are measures of event competitivity I\'m testing\n\nNP EP is the expected placement for a new player, NP RC First is the rating a new player would have if they won the event, NP RC Last is the rating a new player would have if they lost the event.')
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

with open('./data/predictions.pkl', 'rb') as file:
    predictions = pkl.load(file)

event_set = reversed(list(predictions.keys()))


for event_name in event_set:
    this_event = predictions[event_name]
    this_event_preds = this_event['predictions'].sort_values(by='EP')

    for col in ['Rating']:
        this_event_preds[col] = this_event_preds[col].round(0).astype('int64')

    for col in ['EP']:
        this_event_preds[col] = this_event_preds[col].round(1).astype('float')

    this_event_preds.insert(0, "Avatar", "https://mc-heads.net/avatar/" + this_event_preds["Player"])
    this_event_preds.insert(0, "", range(1, len(this_event_preds) + 1))
    this_event_preds = this_event_preds[['', 'Avatar', 'Player', 'Rating', 'Global', 'EP']]

    with st.container(horizontal_alignment='center'):

        st.header(this_event["event"] + ' Predictions')
        st.write('Date:', this_event['date'].strftime("```%Y-%m-%d```"))
        st.write("Player Count:", this_event["player_count"])
        
        for key, value in this_event['stats'].items():
            st.write(key + ":", round(value, 1))

        st.dataframe(
            this_event_preds.style.set_properties(
                subset=['EP'],
                **{'color':'dimgray'}
            ),  
            hide_index=True,
            width='content',
            height=round(36.5+0.5*35.05*len(this_event_preds)),
            column_config={
                "" : st.column_config.NumberColumn(format = "%d."),
                'Avatar': st.column_config.ImageColumn(""),
                'Player': st.column_config.TextColumn(),
                'Rating': st.column_config.NumberColumn('Old Rating'),
                'Global': st.column_config.NumberColumn("Old Global", format = "#%d"),
                'EP': st.column_config.NumberColumn(format="%.1f"),
            }
        )
