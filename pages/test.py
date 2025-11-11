import streamlit as st
import pandas as pd
import pickle as pkl


rankings = pd.read_parquet('./data/rankings.parquet')
rankings.insert(0, "Position", range(1, len(rankings) + 1))
players = rankings['Player']
players_list = players.tolist()

with open('./data/summaries_unclassified.pkl', 'rb') as file:
    summaries = pkl.load(file)

event_set = reversed(list(summaries.keys()))

url_player = st.query_params["id"]

default_index = None
if url_player in players_list:
    default_index = players_list.index(url_player)

with st.sidebar:
    selected_player = st.selectbox("Choose a Player", options=players, index=default_index)
    selected_id = selected_player.lower().replace("_","")

print(selected_player)


col1, col2 = st.columns([0.1,0.7], width=600, vertical_alignment='bottom', border=False)

with col1:
    st.image('https://mc-heads.net/avatar/' + selected_player, width=800)

with col2:
    st.title(selected_player + ' ```#' + str(rankings.loc[selected_id]['Position']) + '```')

st.write(
    'Rating: ```' + str(int(rankings.loc[selected_id]['Rating'])) + 
    '``` Peak: ```' + str(int(rankings.loc[selected_id]['Peak'])) + 
    '``` Events: ```' + str(rankings.loc[selected_id]['Events']) + 
    '```'
    )

filtered_event_set = []

filtered_event_set = [
    event_name for event_name in event_set  
    if (not selected_player or selected_player.lower() in [x.lower() for x in summaries[event_name]['players']])
]

player_events_df = pd.DataFrame(columns=['Event', 'Date', 'Position', 'Rating', 'Global', 'EP', 'AP', 'Score', 'New Rating', 'Rating Change', 'New Global', 'Global Change'])

for event in filtered_event_set:
    summary_results = summaries[event]['results']
    player_events_df.loc[event] = [
        event, 
        summaries[event]['date'],
        summary_results.loc[selected_id]['Position'],
        summary_results.loc[selected_id]['Rating'],
        summary_results.loc[selected_id]['Global'],
        summary_results.loc[selected_id]['EP'],
        summary_results.loc[selected_id]['AP'],
        summary_results.loc[selected_id]['Score'],
        summary_results.loc[selected_id]['New Rating'],
        summary_results.loc[selected_id]['Rating Change'],
        summary_results.loc[selected_id]['New Global'],
        summary_results.loc[selected_id]['Global Change']
    ]

for col in ['Rating', 'Rating Change', 'New Rating']:
    player_events_df[col] = player_events_df[col].round(0).astype('int64')

for col in ['EP', 'AP', 'Score']:
    player_events_df[col] = player_events_df[col].round(1).astype('float')

rc_abs_max = player_events_df['Rating Change'].abs().max()/3
gc_abs_max = player_events_df['Global Change'].abs().max()/3


with st.container(horizontal_alignment='center'):

    st.dataframe(
        player_events_df.style.text_gradient(
                cmap='RdYlGn', subset=['Rating Change'],vmin=-rc_abs_max,vmax=rc_abs_max
            ).text_gradient(
                cmap='RdYlGn', subset=['Global Change'],vmin=-gc_abs_max,vmax=gc_abs_max
            ).set_properties(
                subset=['EP', 'AP', 'Score'],
                **{'color':'dimgray'}
            ), 
        hide_index=True, 
        width='content',
        column_config={
        'Position': st.column_config.NumberColumn(format='#%d'),
        'Date': st.column_config.DateColumn(format = 'iso8601'),
        'Rating': st.column_config.NumberColumn('Old Rating'),
        'Global': st.column_config.NumberColumn("Old Global", format = "#%d"),
        'EP': st.column_config.NumberColumn(format="%.1f"),
        'AP': st.column_config.NumberColumn(format="%.1f"),
        'Score': st.column_config.NumberColumn(format="%.1f"),
        'Rating Change': st.column_config.NumberColumn("",format='%+.0f'),
        'New Global': st.column_config.NumberColumn(format = "#%d"),
        'Global Change': st.column_config.NumberColumn("",format='%+.0f'),
        },

    )
        
st.query_params["id"] = selected_player
