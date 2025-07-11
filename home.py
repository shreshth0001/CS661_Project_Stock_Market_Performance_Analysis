import streamlit as st
import os
st.title("Hello and welcome to stock market analyzer")

folder_path = 'data/processed'
csv_files = [f
             for f in os.listdir(folder_path)
             if f.endswith('.csv')]


