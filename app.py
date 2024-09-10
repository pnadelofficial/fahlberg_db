import streamlit as st
from sql_utils import DatabaseManager
from auth_utils import Authentication
from datetime import datetime
import os

st.title('Fahlberg Interview Database')

auth = Authentication(os.path.join('sensitive_data_for_fahlberg_interview_db', 'config.yaml'))
auth.login()
auth.display()

@st.cache_resource
def get_db():
    return DatabaseManager()
db = DatabaseManager()

if st.session_state['authentication_status']:
    update_or_add = st.radio('Update or Add Data', ['Add new interviewee', 'Update existing interviewee'])
    if update_or_add == 'Update existing interviewee':
        st.subheader('Update Interviewee Data')
        case_no = st.selectbox('Case Number', db.cur.execute("SELECT case_no FROM interviewee").fetchall(), format_func=lambda x: x[0]) 
        case_no = case_no[0]
        data = db.cur.execute(f"SELECT * FROM interviewee WHERE case_no={case_no}").fetchone()
        if data:
            st.write('Update the following fields:')
            with st.expander('Interivew details'):
                pseudonym = st.text_input('Pseudonym', value=data[2])
                recorded = st.checkbox('Recorded', value=data[3])
                consent = st.selectbox('Consent', ['Yes', 'No', 'Partial'], index=['Yes', 'No', 'Partial'].index(data[4]))
                if consent == 'Partial':
                    partial_consent = st.text_area('Partial Consent', value=data[5])
                else:
                    partial_consent = None
                past_interviews = st.number_input('Number of Total Interviews', value=data[6])
                past_dates = []
                for i in range(past_interviews):
                    prev_date = datetime.strptime(data[7].split(', ')[i], '%Y-%m-%d')
                    past_date = st.date_input(f'Date of Interview {i+1}', key=i, value=prev_date)
                    past_dates.append(past_date)
                past_dates = ', '.join([str(past_date) for past_date in past_dates])
                your_name = st.text_input('Your Name', value=data[8])
                poss_interviewers = list(set(["Anjuli","Kathy","Laura","Justin","Other"] + data[9].split(', ')))
                interviewer = st.multiselect('Interviewer', poss_interviewers, default=data[9].split(', '))
                if 'Other' in interviewer:
                    interviewer.append(st.text_input('Other Interviewer', value=interviewer[-1]))
                    interviewer.remove('Other')
                interviewer = ', '.join(list(set(interviewer)))
            with st.expander('Demographic Information'):
                age_range = st.selectbox('Age Range', ['Less than 18', '18-29', '30-59', '60+'], index=['Less than 18', '18-29', '30-59', '60+'].index(data[10]))
                gender = st.selectbox('Gender', ['Male', 'Female', 'Trans', 'Non-binary'], index=['Male', 'Female', 'Trans', 'Non-binary'].index(data[11]))
                country = st.selectbox('Country', ['Honduras', 'El Salvador', 'US', 'Other'], index=['Honduras', 'El Salvador', 'US', 'Other'].index(data[12]))
            with st.expander('Professional Information'):
                poss_profession_type = list(set(['Transportation Sector', 'Small business', 'College student or Professor', 'NGO Worker/Volunteer', 'Affliation with the government', 'Other'] + data[13].split(', ')))
                profession_type = st.multiselect('Profession Type', poss_profession_type, default=data[13].split(', '))
                profession_type = ', '.join(profession_type)
                professional_title = st.text_input('Professional Title', value=data[14])
                st.divider()

                works_gov = st.checkbox('Works for Government', value=data[15])
                if works_gov:
                    geographic_level = st.multiselect('Geographic Level', ['National', 'Municipal', 'Neighborhood'], default=data[16].split(', '))
                    geographic_level = ', '.join(geographic_level)
                    sector = st.selectbox('Sector', ['Social Services', 'Security', 'Other'], index=['Social Services', 'Security', 'Other'].index(data[17]))
                    st.divider()
                
                works_org = st.checkbox('Works for Organization', value=data[18])
                if works_org:
                    country_of_organization = st.multiselect('Country of Organization', ['Honduras', 'El Salvador', 'US', 'Other'], default=data[19].split(', '))
                    country_of_organization = ', '.join(country_of_organization)
                    geographic_reach = st.multiselect('Geographic Reach', ['National', 'Municipal', 'Neighborhood'], default=data[20].split(', '))
                    geographic_reach = ', '.join(geographic_reach)
                    years_of_operation = st.selectbox('Years of Operation', ['Less than 5 years', '5-9 years', '10-19 years', '20+ years'], index=['Less than 5 years', '5-9 years', '10-19 years', '20+ years'].index(data[21]))
                    formality = st.selectbox('Formality', ['Formal NGO', 'Informal Collective', 'In-Between'], index=['Formal NGO', 'Informal Collective', 'In-Between'].index(data[22]))
                    types_of_activities = st.multiselect('Types of Activities', ['Advocacy & Public Policy', "Support for Victims", "Education and Social Development", "Research & Journalism", "Networks & Platforms", "Other"], default=data[23].split(', '))
                    types_of_activities = ', '.join(types_of_activities)
                    types_of_violence = st.multiselect('Types of Violence', ['Gang Violence', 'Random Crime', 'Intimate Violence', 'State Violence', 'Other'], default=data[24].split(', '))
                    types_of_violence = ', '.join(types_of_violence)
                    org_works_in_conflict_zone = st.checkbox('Organization Works in Conflict Zone(s)', value=data[25])
                
            with st.expander('Lived Experience of Violence'):
                cur_lives_in_conflict_zone = st.checkbox('Currently lives in Conflict Zone', value=data[26])
                if cur_lives_in_conflict_zone:
                    cur_name_of_conflict_zone = st.text_input('Name of Current Conflict Zone', value=data[27])
                    gang_faction = st.selectbox('Gang Faction', ['MS-13', 'Barrio-18', 'Other'], index=['MS-13', 'Barrio-18', 'Other'].index(data[28]))
                    st.divider()
                
                pre_lives_in_conflict_zone = st.checkbox('Previously lives in Conflict Zone', value=data[29])
                if pre_lives_in_conflict_zone:
                    pre_name_of_conflict_zone = st.text_input('Name of Previous Conflict Zone', value=data[30])
                    st.divider()
                
                works_in_conflict_zone = st.checkbox('Works in Conflict Zone', value=data[31])
                lived_experience_of_violence = st.checkbox('Lived Experience of Violence', value=data[32])
                if lived_experience_of_violence:
                    violence_type = st.multiselect('Type of Violence', ['Gang Violence', 'Random Crime', 'Intimate Violence', 'State Violence', 'Other'], default=data[33].split(', '))
                    if 'Gang Violence' in violence_type:
                        gang_violence_type = st.multiselect('Type of gang violence', ['Forced displacement', 'Extortion', 'Recruitment', 'Sexual assault', 'Other'], default=data[34].split(', '))
                        gang_violence_types = ', '.join(gang_violence_type)
                    if 'Random Crime' in violence_type:
                        random_violence_type = st.multiselect('Type of random violence', ['Armed robbery', 'Unarmed robbery', 'Kidnapping', 'Home invasion', 'Other'], default=data[35].split(', '))
                        random_violence_types = ', '.join(random_violence_type)
                    if 'Intimate Violence' in violence_type:
                        intimate_violence_type = st.multiselect('Type of intimate violence', ['Sexual assault', 'IPV', 'Violence against LGBTQ', 'Other'], default=data[36].split(', '))
                        intimate_violence_types = ', '.join(intimate_violence_type)
                    if 'State Violence' in violence_type:
                        state_violence_type = st.multiselect('Type of state violence', ['Far of detention', 'Abritrary detention of close kin', 'Police violence', 'Violence in prison', 'Political repression', 'Other'], default=data[37].split(', '))
                        state_violence_types = ', '.join(state_violence_type)
                    if 'Other' in violence_type:
                        other_violence_type = st.text_input('Other Violence Type', value=data[38])
                        other_violence_types = ', '.join(other_violence_type)
                    st.divider()
                    violence_types = ', '.join(violence_type)
                    if 'Gang Violence' not in violence_type:
                        gang_violence_types = ''
                    if 'Random Crime' not in violence_type:
                        random_violence_types = ''
                    if 'Intimate Violence' not in violence_type:
                        intimate_violence_types = ''
                    if 'State Violence' not in violence_type:
                        state_violence_types = ''
                    if 'Other' not in violence_type:
                        other_violence_types = ''
            if st.button('Update'):
                db.update(
                    'interviewee',
                    case_no=case_no,
                    pseudonym=pseudonym,
                    recorded=recorded,
                    consent=consent,
                    partial_consent=partial_consent,
                    past_interviews=past_interviews,
                    past_dates=past_dates,
                    your_name=your_name,
                    interviewer=interviewer,
                    age_range=age_range,
                    gender=gender,
                    country=country,
                    profession_type=profession_type,
                    professional_title=professional_title,
                    works_in_gov=works_gov,
                    geographic_level=geographic_level,
                    sector=sector,
                    works_in_org=works_org,
                    country_of_organization=country_of_organization,
                    geographic_reach=geographic_reach,
                    years_of_operation=years_of_operation,
                    formality=formality,
                    types_of_activities=types_of_activities,
                    types_of_violence=types_of_violence,
                    org_works_in_conflict=org_works_in_conflict_zone,
                    currently_lives_in_conflict=cur_lives_in_conflict_zone,
                    cur_name_of_conflict=cur_name_of_conflict_zone,
                    gang_faction=gang_faction,
                    previously_lives_in_conflict=pre_lives_in_conflict_zone,
                    prev_name_of_conflict=pre_name_of_conflict_zone,
                    works_in_conflict=works_in_conflict_zone,
                    lived_experience_of_violence=lived_experience_of_violence,
                    violence_types=violence_types,
                    gang_violence_type=gang_violence_types,
                    random_crime_type=random_violence_types,
                    intimate_violence_type=intimate_violence_types,
                    state_violence_type=state_violence_types,
                    other_violence_type=other_violence_types
                )
        else:
            st.error('No data found for this case number')
    else:
        st.subheader('Add Interviewee Data')
        
        # interview details
        with st.expander('Interivew details'):
            case_no = st.text_input('Case Number from Excel')
            date = st.date_input("Today's date")
            pseudonym = st.text_input('Pseudonym')
            recorded = st.checkbox('Recorded')
            consent = st.selectbox('Consent', ['Yes', 'No', 'Partial'])
            if consent == 'Partial':
                partial_consent = st.text_area('Partial Consent')
            else:
                partial_consent = None
            past_interviews = st.number_input('Number of Total Interviews', value=1)   
            past_dates = []
            for i in range(past_interviews):
                past_date = st.date_input(f'Date of Interview {i+1}', key=i)
                past_dates.append(past_date)
            your_name = st.text_input('Your Name')
            interviewer = st.multiselect('Interviewer', ["Anjuli","Kathy","Laura","Justin","Other"]) # db side, add in other to write in
            if 'Other' in interviewer:
                interviewer.append(st.text_input('Other Interviewer'))
                interviewer.remove('Other')

            past_dates = ', '.join([str(past_date) for past_date in past_dates])
            interviewers = ', '.join(interviewer)
        
        # demographic information
        with st.expander('Demographic Information'):
            age_range = st.selectbox('Age Range', ['Less than 18', '18-29', '30-59', '60+'])
            gender = st.selectbox('Gender', ['Male', 'Female', 'Trans', 'Non-binary'])
            country = st.selectbox('Country', ['Honduras', 'El Salvador', 'US', 'Other'])
        
        # professional information
        with st.expander('Professional Information'):
            profession_type = st.multiselect('Profession Type', ['Transportation Sector', 'Small business', 'College student or Professor', 'NGO Worker/Volunteer', 'Affliation with the government', 'Other'])
            profession_type = ', '.join(profession_type)
            professional_title = st.text_input('Professional Title')
            st.divider()

            works_gov = st.checkbox('Works for Government')
            if works_gov:
                geographic_level = st.multiselect('Geographic Level', ['National', 'Municipal', 'Neighborhood'])
                geographic_level = ', '.join(geographic_level)
                sector = st.selectbox('Sector', ['Social Services', 'Security', 'Other'])
                st.divider()

            works_org = st.checkbox('Works for Organization')
            if works_org: 
                country_of_organization = st.multiselect('Country of Organization', ['Honduras', 'El Salvador', 'US', 'Other'])
                country_of_organization = ', '.join(country_of_organization)
                geographic_reach = st.multiselect('Geographic Reach', ['National', 'Municipal', 'Neighborhood'])
                geographic_reach = ', '.join(geographic_reach)
                years_of_operation = st.selectbox('Years of Operation', ['Less than 5 years', '5-9 years', '10-19 years', '20+ years'])
                formality = st.selectbox('Formality', ['Formal NGO', 'Informal Collective', 'In-Between'])
                types_of_activities = st.multiselect('Types of Activities', ['Advocacy & Public Policy', "Support for Victims", "Education and Social Development", "Research & Journalism", "Networks & Platforms", "Other"])
                types_of_activities = ', '.join(types_of_activities)
                types_of_violence = st.multiselect('Types of Violence', ['Gang Violence', 'Random Crime', 'Intimate Violence', 'State Violence', 'Other'])
                types_of_violence = ', '.join(types_of_violence)
                org_works_in_conflict_zone = st.checkbox('Organization Works in Conflict Zone(s)')
        
        with st.expander('Lived Experience of Violence'):
            cur_lives_in_conflict_zone = st.checkbox('Currently lives in Conflict Zone') 
            if cur_lives_in_conflict_zone:
                cur_name_of_conflict_zone = st.text_input('Name of Current Conflict Zone')
                gang_faction = st.selectbox('Gang Faction', ['MS-13', 'Barrio-18', 'Other'])
                st.divider()
            
            pre_lives_in_conflict_zone = st.checkbox('Previously lives in Conflict Zone')
            if pre_lives_in_conflict_zone:
                pre_name_of_conflict_zone = st.text_input('Name of Previous Conflict Zone')
                st.divider()
            
            works_in_conflict_zone = st.checkbox('Works in Conflict Zone')
            lived_experience_of_violence = st.checkbox('Lived Experience of Violence')
            if lived_experience_of_violence:
                violence_type = st.multiselect('Type of Violence', ['Gang Violence', 'Random Crime', 'Intimate Violence', 'State Violence', 'Other'])
                if 'Gang Violence' in violence_type:
                    gang_violence_type = st.multiselect('Type of gang violence', ['Forced displacement', 'Extortion', 'Recruitment', 'Sexual assault', 'Other'])
                    gang_violence_types = ', '.join(gang_violence_type)
                if 'Random Crime' in violence_type:
                    random_violence_type = st.multiselect('Type of random violence', ['Armed robbery', 'Unarmed robbery', 'Kidnapping', 'Home invasion', 'Other'])
                    random_violence_types = ', '.join(random_violence_type)
                if 'Intimate Violence' in violence_type:
                    intimate_violence_type = st.multiselect('Type of intimate violence', ['Sexual assault', 'IPV', 'Violence against LGBTQ', 'Other'])
                    intimate_violence_types = ', '.join(intimate_violence_type)
                if 'State Violence' in violence_type:
                    state_violence_type = st.multiselect('Type of state violence', ['Far of detention', 'Abritrary detention of close kin', 'Police violence', 'Violence in prison', 'Political repression', 'Other'])
                    state_violence_types = ', '.join(state_violence_type)
                if 'Other' in violence_type:
                    other_violence_type = st.text_input('Other Violence Type')
                    other_violence_types = ', '.join(other_violence_type)
                st.divider()
                violence_types = ', '.join(violence_type)
                if 'Gang Violence' not in violence_type:
                    gang_violence_types = ''
                if 'Random Crime' not in violence_type:
                    random_violence_types = ''
                if 'Intimate Violence' not in violence_type:
                    intimate_violence_types = ''
                if 'State Violence' not in violence_type:
                    state_violence_types = ''
                if 'Other' not in violence_type:
                    other_violence_types = ''

        if st.button('Submit'):
            db.insert(
                'interviewee',
                case_no=case_no,
                date=date,
                pseudonym=pseudonym,
                recorded=recorded,
                consent=consent,
                partial_consent=partial_consent,
                past_interviews=past_interviews,
                past_dates=past_dates,
                your_name=your_name,
                interviewer=interviewer,
                age_range=age_range,
                gender=gender,
                country=country,
                profession_type=profession_type,
                professional_title=professional_title,
                works_in_gov=works_gov,
                geographic_level=geographic_level,
                sector=sector,
                works_in_org=works_org,
                country_of_organization=country_of_organization,
                geographic_reach=geographic_reach,
                years_of_operation=years_of_operation,
                formality=formality,
                types_of_activities=types_of_activities,
                types_of_violence=types_of_violence,
                org_works_in_conflict=org_works_in_conflict_zone,
                currently_lives_in_conflict=cur_lives_in_conflict_zone,
                cur_name_of_conflict=cur_name_of_conflict_zone,
                gang_faction=gang_faction,
                previously_lives_in_conflict=pre_lives_in_conflict_zone,
                prev_name_of_conflict=pre_name_of_conflict_zone,
                works_in_conflict=works_in_conflict_zone,
                lived_experience_of_violence=lived_experience_of_violence,
                violence_types=violence_types,
                gang_violence_type=gang_violence_types,
                random_crime_type=random_violence_types,
                intimate_violence_type=intimate_violence_types,
                state_violence_type=state_violence_types,
                other_violence_type=other_violence_types
            )
            st.success('Interviewee data added successfully')

    if st.button('View Interviewee Data'):
        data = db.cur.execute("SELECT * FROM interviewee").fetchall()
        st.write(data)
        