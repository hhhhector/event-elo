import streamlit as st
st.set_page_config(layout="wide")


main_page = st.Page("pages/main_page.py", title="Home")
rating_history = st.Page("pages/rating_history.py", title="Rating History")
event_results = st.Page("pages/event_results.py", title="Event Results")
event_history = st.Page("pages/event_history.py", title="Event History")
test = st.Page("pages/test.py", title='Test')

pg = st.navigation({"Minecraft Event Elo" : [main_page, rating_history, event_results, event_history, test]}, position='sidebar')

pg.run()