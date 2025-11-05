import streamlit as st
import pandas as pd
import pickle as pkl
import numpy as np

st.title('Minecraft ```Event``` Elo')
st.caption('by hector')
st.write('WELCOME to the new website more features coming SOON.')

rankings = pd.read_parquet('./data/rankings.parquet')

with open('./data/summaries_unclassified.pkl', 'rb') as file:
    summaries_unclassified = pkl.load(file)


rankings.insert(0, "", range(1, len(rankings) + 1))


col1, col2, col3 = st.columns(3)

with col1:

    top_50 = rankings.head(50).iloc[:,:6]
    top_50["Rating Change"] = rankings.head(50).iloc[:,-1] - rankings.head(50).iloc[:,-2]
    
    rc_abs_max = top_50['Rating Change'].abs().max()

    for col in top_50.select_dtypes(include=['float']).columns:
        top_50[col] = top_50[col].round(0).astype('int64')

    top_50['Rating Change'] = np.where(
        top_50['Rating Change'] == 0,
        np.nan,
        top_50['Rating Change'] 
    )

    top_50 = top_50[["", "Avatar", "Player", "Rating", "Rating Change", "Peak", "Events"]]

    def style_specific_cell(x):
        styler_df = pd.DataFrame('', index=x.index, columns=x.columns)

        for i in range(7):

            styler_df.iat[0, i] = 'color: #eac451' 
            styler_df.iat[1, i] = 'color: #888888'
            styler_df.iat[2, i] = 'color: #ea8451'
        
        return styler_df

    st.header("Top 50 Players")
    with st.container(horizontal_alignment='center'): 
        st.dataframe(top_50.style.apply(
                style_specific_cell,
                axis=None
            ).text_gradient(
                cmap='RdYlGn', subset=['Rating Change'],vmin=-rc_abs_max,vmax=rc_abs_max
            ),
            hide_index=True,
            column_config={
                "" : st.column_config.NumberColumn(format = "#%d"),
                "Avatar" : st.column_config.ImageColumn(""),
                'Player': st.column_config.TextColumn(width = 125),
                "Rating" : st.column_config.NumberColumn(format = "%f"),
                'Rating Change': st.column_config.NumberColumn("",format='%+.0f'),
                "Peak" : st.column_config.NumberColumn(),
                "Events" : st.column_config.NumberColumn(),
            },
            width="content",
            height=round(36.5+35.05*50),

        )

with col2:
    last_event = summaries_unclassified[list(summaries_unclassified.keys())[-1]]['results'][
        ['Position', 'Player', 'New Rating', 'Rating Change', 'New Global', 'Global Change']
    ]
    last_event.insert(1, "Avatar", "https://mc-heads.net/avatar/" + last_event["Player"])
    st.header("```" + str(list(summaries_unclassified.keys())[-1]) + "``` Results")


    for col in ['Rating Change', 'New Rating']:
        last_event.loc[:,col] = last_event[col].round(0).astype('int64')


    rc_abs_max = last_event['Rating Change'].abs().max()
    gc_abs_max = last_event['Global Change'].abs().max()


    with st.container(horizontal_alignment='center'): 
        st.dataframe(last_event.style.apply(
                style_specific_cell,
                axis=None
            ).text_gradient(
                cmap='RdYlGn', subset=['Rating Change'],vmin=-rc_abs_max,vmax=rc_abs_max
            ).text_gradient(
                cmap='RdYlGn', subset=['Global Change'],vmin=-gc_abs_max,vmax=gc_abs_max
            ),
        hide_index=True,
        column_config={
            "Position" : st.column_config.NumberColumn("",format = "#%d"),
            "Avatar" : st.column_config.ImageColumn(""),
            'Player': st.column_config.TextColumn(width = 125),
            "New Rating" : st.column_config.NumberColumn("Rating",format = "%f"),
            'Rating Change': st.column_config.NumberColumn("",format='%+.0f'),
            "New Global" : st.column_config.NumberColumn("Global",format = "#%d"),
            'Global Change': st.column_config.NumberColumn("",format='%+.0f'),
            "Events" : st.column_config.NumberColumn(),
        },
        height=round(36.5+35.05*len(last_event)),
        width='content'
    )

with col3:
    st.header('Changelog')
    ra_events = list(reversed(list(summaries_unclassified.keys())[-10:]))

    st.write('Recent Events:')
    for event in ra_events:
        st.write("```", event, "-", summaries_unclassified[event]['date'].strftime("%Y/%m/%d"), "```")
    st.subheader('TODO')
    st.markdown("""
    - Predictions Tab\n\n
    - Head to Head Tab\n\n
    - Player Tab (NEW)\n\n
    - Make Website Prettier\n\n
    - Make Code Prettier\n\n 
             """)