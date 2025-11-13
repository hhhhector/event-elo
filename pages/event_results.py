import streamlit as st
import pickle as pkl
import matplotlib
import pandas as pd

st.title('Event Results')
st.caption('EP : Expected Placement | AP : Actual Placement | Score : EP - AP\n\nNP are measures of event competitivity I\'m testing\n\nNP EP is the expected placement for a new player, NP RC First is the rating a new player would have if they won the event, NP RC Last is the rating a new player would have if they lost the event.')
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

rating_history = pd.read_parquet('./data/rating_history.parquet')
players = rating_history["Player"]
event_types = ["MCC", "BW", "FW", "PB", "MH", "MN", "BC", "FUW", "JC", "CT", "BB", "CH", "TT", "KG", "SD"]


with open('./data/summaries_unclassified.pkl', 'rb') as file:
    summaries = pkl.load(file)

event_set = reversed(list(summaries.keys()))

col1, col2, col3, col4 = st.columns(4)

with col1:
    search = st.text_input("Event Name", value=None)

with col2:
    player_filter = st.selectbox("Player", options = sorted(players), index=None)


filtered_event_set = []
if not search and not player_filter:
    filtered_event_set = list(event_set)
else:
    filtered_event_set = [
        event_name for event_name in event_set
        
        if (not search or search.lower() in event_name.lower())
        
        and (not player_filter or player_filter.lower() in [x.lower() for x in summaries[event_name]['players']])
    ]

filtered_event_set_details = [{'name' : x} for x in filtered_event_set]


for filtered_event_details in filtered_event_set_details:
    filtered_event_details['Date'] = summaries[filtered_event_details['name']]['date']
    filtered_event_details['NP EP'] = summaries[filtered_event_details['name']]['stats']['NP EP']
    filtered_event_details['NP RC First'] = summaries[filtered_event_details['name']]['stats']['NP RC First']
    filtered_event_details['NP RC Last'] = summaries[filtered_event_details['name']]['stats']['NP RC Last']

filtered_event_set_details = pd.DataFrame(filtered_event_set_details)

with col3:
    sort_order = st.selectbox('Sort By: ', options = ['Date', 'NP EP', 'NP RC First', 'NP RC Last'])

if len(filtered_event_set) != 0:
    filtered_event_set_details = filtered_event_set_details.sort_values(by = sort_order, ascending=False)

with col4:
    limit = st.number_input("Display Limit (max: " + str(len(filtered_event_set)) + ")", min_value=0, max_value=len(filtered_event_set), value=min(20,len(filtered_event_set)))
if len(filtered_event_set) != 0:
    filtered_event_set = filtered_event_set_details['name']
    filtered_event_set = filtered_event_set[0:limit]

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

st.write("Displaying", len(filtered_event_set), 'events')


for event_name in filtered_event_set:
    this_event = summaries[event_name]
    this_event_results = this_event['results']

    for col in ['Rating', 'Rating Change', 'New Rating']:
        this_event_results[col] = this_event_results[col].round(0).astype('int64')

    for col in ['EP', 'AP', 'Score']:
        this_event_results[col] = this_event_results[col].round(1).astype('float')

    this_event_results.insert(1, "Avatar", "https://mc-heads.net/avatar/" + this_event_results["Player"])
    this_event_results = this_event_results[['Position', 'Avatar', 'Player', 'Rating', 'Global', 'EP', 'AP', 'Score', 'New Rating', 'Rating Change', 'New Global', 'Global Change']]
    this_event_results = this_event_results.rename(columns = {'Position': ''})  

    rc_abs_max = this_event_results['Rating Change'].abs().max()/3
    gc_abs_max = this_event_results['Global Change'].abs().max()/3

    with st.container(horizontal_alignment='center'):

        st.header(this_event["event"] + ' Results')
        st.write('Date:', this_event['date'].strftime("```%Y-%m-%d```"))
        st.write("Player Count:", this_event["player_count"])
        
        for key, value in this_event['stats'].items():
            st.write(key + ":", round(value, 1))


        st.dataframe(
            this_event_results.style.apply(
                highlight_row, axis=1
            ).text_gradient(
                cmap='RdYlGn', subset=['Rating Change'],vmin=-rc_abs_max,vmax=rc_abs_max
            ).text_gradient(
                cmap='RdYlGn', subset=['Global Change'],vmin=-gc_abs_max,vmax=gc_abs_max
            ).set_properties(
                subset=['EP', 'AP', 'Score'],
                **{'color':'dimgray'}
            ),  
            hide_index=True,
            width='content',
            height=round(36.5+0.5*35.05*len(this_event_results)),
            column_config={
                '' : st.column_config.NumberColumn(format = "%d.",),
                'Avatar': st.column_config.ImageColumn(""),
                'Player': st.column_config.TextColumn(),
                'Rating': st.column_config.NumberColumn('Old Rating'),
                'Global': st.column_config.NumberColumn("Old Global", format = "#%d"),
                'EP': st.column_config.NumberColumn(format="%.1f"),
                'AP': st.column_config.NumberColumn(format="%.1f"),
                'Score': st.column_config.NumberColumn(format="%.1f"),
                'Rating Change': st.column_config.NumberColumn("",format='%+.0f'),
                'New Global': st.column_config.NumberColumn(format = "#%d"),
                'Global Change': st.column_config.NumberColumn("",format='%+.0f'),
            }
        )
