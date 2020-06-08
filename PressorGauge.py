import streamlit as st

st.title("My Streamlit App")

clicked = st.button("CLICK ME")
if clicked:
    st.balloons()
