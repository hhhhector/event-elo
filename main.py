import streamlit as st

main_page = st.Page("main_page.py", title="Main")
rating_history = st.Page("rating_history.py", title="Rating History")
event_results = st.Page("event_results.py", title="Event Results")
event_history = st.Page("event_history.py", title="Event History")


pg = st.navigation([main_page, rating_history, event_results, event_history])

pg.run()