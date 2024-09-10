import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit as st

class Authentication:
    def __init__(self, config_file):
        with open(config_file) as file:
            config = yaml.load(file, Loader=SafeLoader)
        self.config = config
        self.authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['pre-authorized']
        )
        
    def login(self):
        self.authenticator.login()
    
    def display(self):
        if st.session_state['authentication_status']:
            self.authenticator.logout()
            st.write(f'Welcome *{st.session_state["name"]}*')
        elif st.session_state['authentication_status'] is False:
            st.error('Username/password is incorrect')
        elif st.session_state['authentication_status'] is None:
            st.warning('Please enter your username and password')
    
    