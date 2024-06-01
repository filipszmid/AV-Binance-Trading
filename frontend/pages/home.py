import os

import streamlit as st

from frontend import utils


def fix_paths():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)


fix_paths()

intro_markdown = utils.read_markdown_file("../../README.md")

st.markdown(intro_markdown, unsafe_allow_html=True)
