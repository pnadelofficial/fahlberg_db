from sql_utils import DatabaseManager
import streamlit as st
import pandas as pd
from auth_utils import Authentication, setup_submodule  
import os
import plotly.express as px

if st.session_state.get('submodule_setup') is None:
    setup_submodule()

config_path = os.path.join('sensitive_data_for_fahlberg_interview_db', 'config.yaml')
db_path = os.path.join('sensitive_data_for_fahlberg_interview_db', 'db.sql')

st.title('Crosstab Demo')

auth = Authentication(config_path)
auth.login()
auth.display()
db = DatabaseManager(path=db_path)


if st.session_state['authentication_status']:
    df = pd.read_sql_query('SELECT * FROM interviewee', db.conn)
    column_a = st.selectbox('Select column A', df.columns, index=None, format_func=lambda x: x.replace('_', ' ').title())
    if column_a:
        column_b = st.selectbox('Select column B', list(set(df.columns)-{column_a}), index=None, format_func=lambda x: x.replace('_', ' ').title())
        if column_b:
            crosstab = pd.crosstab(df[column_a], df[column_b])
            fig = px.imshow(crosstab)
            st.plotly_chart(fig)
            # st.dataframe(crosstab)
