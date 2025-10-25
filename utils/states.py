from typing import Dict, Optional
import streamlit as st

def set_state(
    state_name: str, state: Dict, force: Optional[bool] = False
) -> Dict | None:
    if state_name in st.session_state and not force:
        return
    st.session_state[state_name] = state
    if force:
        return st.session_state[state_name]
