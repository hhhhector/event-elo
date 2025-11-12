import streamlit as st
import pandas as pd
import pickle as pkl
import altair as alt

rankings = pd.read_parquet('./data/rankings.parquet')
rankings.insert(0, "Position", range(1, len(rankings) + 1))
players = rankings['Player']
players_list = players.tolist()

with open('./data/summaries_unclassified.pkl', 'rb') as file:
    summaries = pkl.load(file)


default_index = 0

if 'player_selector' in st.session_state:
    default_index = None
else:
    try: 
        url_player = st.query_params["id"]
        if url_player in players_list:
            default_index = players_list.index(url_player)
    except KeyError:
        pass 
    

with st.sidebar:
    selected_player = st.selectbox("Choose a Player", options=players, index=default_index, key='player_selector')
    if selected_player is not None:
        selected_id = selected_player.lower().replace("_","")

if selected_player is not None:

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


    col1, col2 = st.columns(2)

    with col1:
        m = st.slider("Players", value = 10, min_value = 1, max_value = len(rankings))

    with col2:
        n = st.slider("Events", value = rankings.shape[1] - 8, min_value = 1, max_value = rankings.shape[1] - 8)

    for col in rankings.select_dtypes(include=['float']).columns:
        rankings[col] = rankings[col].round(0).astype('int64')

    plot_data_wide = rankings[rankings["Player"] == selected_player].reset_index().drop(
        columns = ["Avatar", "Rating", "Peak", "Events", "I", "index"]
    ).head(m).set_index("Player").T.iloc[-n:,:]
    plot_data_wide.reset_index()
    plot_data_wide['SortOrder'] = range(len(plot_data_wide))
    plot_data_wide = plot_data_wide.reset_index().rename(columns={'index': 'Event'})
    plot_data_long = plot_data_wide.melt(
        id_vars=['Event', 'SortOrder'],  
        var_name='Player',            
        value_name='Rating'           
    )


    chart = alt.Chart(plot_data_long, height=600).mark_line(point=alt.OverlayMarkDef(size=100, opacity=0), size=1.5).encode(
        
        x=alt.X('Event', 
            sort=alt.SortField('SortOrder')
        ),
        
        y=alt.Y('Rating',
            scale=alt.Scale(domain=[min(plot_data_long["Rating"]) - 100,max(plot_data_long["Rating"]) + 100])
        ),

        color=alt.value('#EAE151'),

        tooltip=['Event', 'Rating']

    ).interactive()

    st.altair_chart(chart)

    event_set = reversed(list(summaries.keys()))

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

else:
    st.write('?')
    
st.query_params["id"] = selected_player
