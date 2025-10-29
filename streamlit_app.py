import streamlit as st
import pandas as pd
import numpy as np

st.title("Event Elo")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

chart_data = pd.DataFrame(
     np.random.randn(2000, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)

x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)