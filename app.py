import streamlit as st
from sql_utils import DatabaseManager
from auth_utils import Authentication, setup_submodule
from datetime import datetime
import os

if st.session_state.get('submodule_setup') is None:
    setup_submodule()

config_path = os.path.join('sensitive_data_for_fahlberg_interview_db', 'config.yaml')
db_path = os.path.join('sensitive_data_for_fahlberg_interview_db', 'db.sql')

st.title('Base de datos de entrevistas de Fahlberg')

auth = Authentication(config_path)
auth.login()
auth.display()

db = DatabaseManager(path=db_path)

if st.session_state['authentication_status']:
    update_or_add = st.radio('Actualizar o agregar datos', ['Agregar nuevo entrevistado', 'Actualizar entrevistado existente'])
    if update_or_add == 'Actualizar entrevistado existente':
        st.subheader('Actualizar entrevistado existente')
        case_no = st.selectbox('Número de caso en Excel', db.cur.execute("SELECT case_no FROM interviewee").fetchall(), format_func=lambda x: x[0]) 
        case_no = case_no[0]
        data = db.cur.execute(f"SELECT * FROM interviewee WHERE case_no={case_no}").fetchone()
        if data:
            st.write('Update the following fields:') # not translated
            with st.expander('Detalles de la entrevista'):
                pseudonym = st.text_input('Seudónimo', value=data[2])
                recorded = st.checkbox('Grabación', value=data[3])
                consent = st.selectbox('Consentimiento', ['Si', 'No', 'Parcial'], index=['Si', 'No', 'Parcial'].index(data[4]))
                if consent == 'Parcial':
                    partial_consent = st.text_area('Consentimiento parcial', value=data[5])
                else:
                    partial_consent = None
                past_interviews = st.number_input('Número total de entrevistas', value=data[6])
                past_dates = []
                for i in range(past_interviews):
                    prev_date = datetime.strptime(data[7].split(', ')[i], '%Y-%m-%d')
                    past_date = st.date_input(f'Fecha de entrevista {i+1}', key=i, value=prev_date)
                    past_dates.append(past_date)
                past_dates = ', '.join([str(past_date) for past_date in past_dates])
                your_name = st.text_input('Nombre', value=data[8])
                poss_interviewers = list(set(["Anjuli","Kathy","Laura","Justin","Other"] + data[9].split(', ')))
                interviewer = st.multiselect('Entrevistador', poss_interviewers, default=data[9].split(', '))
                if 'Otro' in interviewer:
                    interviewer.append(st.text_input('Otro Entrevistador', value=interviewer[-1]))
                    interviewer.remove('Otro')
                interviewer = ', '.join(list(set(interviewer)))
            with st.expander('Información demográfica'):
                age_range = st.selectbox('Rango de edad', ['Menor de 18 años', '18-29', '30-59', '60+'], index=['Menor de 18 años', '18-29', '30-59', '60+'].index(data[10]))
                gender = st.selectbox('Género', ['Masculino', 'Femenino', 'Trans', 'No binario'], index=['Masculino', 'Femenino', 'Trans', 'No binario'].index(data[11]))
                country = st.selectbox('País', ['Honduras', 'El Salvador', 'US', 'Otro'], index=['Honduras', 'El Salvador', 'US', 'Otro'].index(data[12]))
            with st.expander('Información profesional'):
                poss_profession_type = list(set(['Sector de Transporte ', 'Negocios pequeño', 'Estudiante universitario o Profesor', 'Trabajador o voluntario de ONG ', 'Afiliación con el gobierno', 'Otro'] + data[13].split(', ')))
                profession_type = st.multiselect('Tipo de profesiones', poss_profession_type, default=data[13].split(', '))
                profession_type = ', '.join(profession_type)
                professional_title = st.text_input('Titulo professional', value=data[14])
                st.divider()

                works_gov = st.checkbox('Trabaja para el Gobierno', value=data[15])
                if works_gov:
                    geographic_level = st.multiselect('Nivel geográfico', ['Nacional', 'Municipal', 'Comunidad'], default=data[16].split(', '))
                    geographic_level = ', '.join(geographic_level)
                    sector = st.selectbox('Sector', ['Servicios sociales', 'Security', 'Otro'], index=['Servicios sociales', 'Security', 'Otro'].index(data[17])) # security not translated
                    st.divider()
                
                works_org = st.checkbox('Works for Organization', value=data[18]) # not translated
                if works_org:
                    country_of_organization = st.multiselect('Country of Organization', ['Honduras', 'El Salvador', 'US', 'Other'], default=data[19].split(', ')) # not translated
                    country_of_organization = ', '.join(country_of_organization)
                    geographic_reach = st.multiselect('Geographic Reach', ['Nacional', 'Municipal', 'Comunidad'], default=data[20].split(', '))
                    geographic_reach = ', '.join(geographic_reach)
                    years_of_operation = st.selectbox('Tiempo de trabajo', ['Menos de 5 años', '5-9 años', '10-19 años', '20+ años'], index=['Menos de 5 años', '5-9 años', '10-19 años', '20+ años'].index(data[21]))
                    formality = st.selectbox('Formalidad', ['ONG formal', 'Colectivo informal', 'En proceso de formalización'], index=['ONG formal', 'Colectivo informal', 'En proceso de formalización'].index(data[22]))
                    types_of_activities = st.multiselect('Tipos de actividades', ['Defensa de derechos y políticas públicas', "Apoyo a víctimas", "Educación y desarrollo social", "Investigación y periodismo", "Redes y plataformas", "Otro"], default=data[23].split(', '))
                    types_of_activities = ', '.join(types_of_activities)
                    types_of_violence = st.multiselect('Tipos de violencia', ['Violencia de pandillas', 'Delitos comunes', 'Violencia sexual', 'Violencia estatal', 'Otro'], default=data[24].split(', '))
                    types_of_violence = ', '.join(types_of_violence)
                    org_works_in_conflict_zone = st.checkbox('La organización trabaja en zonas de conflicto', value=data[25])
                
            with st.expander('Ha vivido experiencias de violencia'):
                cur_lives_in_conflict_zone = st.checkbox('Actualmente vive en una zona de conflicto', value=data[26])
                if cur_lives_in_conflict_zone:
                    cur_name_of_conflict_zone = st.text_input('Nombre de la zona de conflicto actual', value=data[27])
                    gang_faction = st.selectbox('Facción de pandillas', ['MS-13', 'Barrio-18', 'Otro'], index=['MS-13', 'Barrio-18', 'Otro'].index(data[28]))
                    st.divider()
                
                pre_lives_in_conflict_zone = st.checkbox('Anteriormente vivió en una zona de conflicto', value=data[29])
                if pre_lives_in_conflict_zone:
                    pre_name_of_conflict_zone = st.text_input('Nombre de la zona de conflicto anterior', value=data[30])
                    st.divider()
                
                works_in_conflict_zone = st.checkbox('Trabaja en una zona de conflicto', value=data[31])
                lived_experience_of_violence = st.checkbox('Experiencia vivida de violencia', value=data[32])
                if lived_experience_of_violence:
                    violence_type = st.multiselect('Tipos de violencia', ['Violencia de pandillas', 'Delitos comunes', 'Violencia sexual', 'Violencia estatal', 'Otro'], default=data[33].split(', '))
                    if 'Violencia de pandillas' in violence_type:
                        gang_violence_type = st.multiselect('Tipos de violencia', ['Violencia de pandillas', 'Delitos comunes', 'Violencia sexual', 'Violencia estatal', 'Otro'], default=data[34].split(', '))
                        gang_violence_types = ', '.join(gang_violence_type)
                    if 'Delitos comunes' in violence_type:
                        random_violence_type = st.multiselect('Tipo de violencia aleatoria', ['Robo a mano armada', 'Robo sin arma', 'Secuestro', 'Allanamiento de morada', 'Otro'], default=data[35].split(', '))
                        random_violence_types = ', '.join(random_violence_type)
                    if 'Violencia sexual' in violence_type:
                        intimate_violence_type = st.multiselect('Tipo de violencia íntima', ['Agresión sexual', 'Violencia de pareja', 'Violencia contra personas LGBTQ', 'Otro'], default=data[36].split(', '))
                        intimate_violence_types = ', '.join(intimate_violence_type)
                    if 'Violencia estatal' in violence_type:
                        state_violence_type = st.multiselect('Tipo de violencia estatal', ['Miedo a la detención', 'Detención arbitraria de familiares cercanos', 'Violencia policial', 'Violencia en prisión', 'Represión política', 'Otro'], default=data[37].split(', '))
                        state_violence_types = ', '.join(state_violence_type)
                    if 'Otro' in violence_type:
                        other_violence_type = st.text_input('Otro tipo de violencia', value=data[38])
                        other_violence_types = ', '.join(other_violence_type)
                    st.divider()
                    violence_types = ', '.join(violence_type)
                    if 'Violencia de pandillas' not in violence_type:
                        gang_violence_types = ''
                    if 'Delitos comunes' not in violence_type: # from communes
                        random_violence_types = ''
                    if 'Violencia sexual' not in violence_type:
                        intimate_violence_types = ''
                    if 'Violencia estatal' not in violence_type:
                        state_violence_types = ''
                    if 'Otro' not in violence_type:
                        other_violence_types = ''
            if st.button('Actualizar'):
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
                st.success('Datos del entrevistado agregado correctamente')
        else:
            st.error('No se encontraron datos para este número de caso')
    else:
        st.subheader('Agregar nuevo entrevistado')
        case_no = '',
        date = '',
        pseudonym = '',
        recorded = '',
        consent = '',
        partial_consent = '',
        past_interviews = '',
        past_dates = '',
        your_name = '',
        interviewer = '',
        age_range = '',
        gender = '',
        country = '',
        profession_type = '',
        professional_title = '',
        works_in_gov = '',
        geographic_level = '',
        sector = '',
        works_in_org = '',
        country_of_organization = '',
        geographic_reach = '',
        years_of_operation = '',
        formality = '',
        types_of_activities = '',
        types_of_violence = '',
        org_works_in_conflict_zone = '',
        currently_lives_in_conflict = '',
        cur_name_of_conflict = '',
        gang_faction = '',
        pre_lives_in_conflict_zone = '',
        prev_name_of_conflict = '',
        works_in_conflict = '',
        lived_experience_of_violence = '',
        violence_types = '',
        gang_violence_types = '',
        random_violence_types = '',
        intimate_violence_types = '',
        state_violence_types = '',
        other_violence_types = ''
        # interview details
        with st.expander('Detalles de la entrevista'):
            case_no = st.text_input('Case number from Excel')
            date = st.date_input("Fecha de hoy")
            pseudonym = st.text_input('Seudónimo')
            recorded = st.checkbox('Grabación')
            consent = st.selectbox('Consentimiento', ['Si', 'No', 'Parcial'])
            if consent == 'Parcial':
                partial_consent = st.text_area('Parcial consentimiento')
            else:
                partial_consent = None
            past_interviews = st.number_input('Número total de entrevistas', value=1)   
            past_dates = []
            for i in range(past_interviews):
                past_date = st.date_input(f'Fecha de entrevista {i+1}', key=i)
                past_dates.append(past_date)
            your_name = st.text_input('Nombre')
            interviewer = st.multiselect('Entrevistador', ["Anjuli","Kathy","Laura","Justin","Otro"]) # db side, add in other to write in
            if 'Otro' in interviewer:
                interviewer.append(st.text_input('Otro entrevistador'))
                interviewer.remove('Otro')

            past_dates = ', '.join([str(past_date) for past_date in past_dates])
            interviewer = ', '.join(interviewer)
        
        # demographic information
        with st.expander('Información demográfica'):
            age_range = st.selectbox('Rango de edad', ['Menor de 18 años', '18-29', '30-59', '60+'])
            gender = st.selectbox('Género', ['Masculino', 'Femenino', 'Trans', 'No binario'])
            country = st.selectbox('País', ['Honduras', 'El Salvador', 'US', 'Otro'])
        
        # professional information
        with st.expander('Información profesional'):
            profession_type = st.multiselect('Tipo de profesiones', ['Sector de Transporte ', 'Negocios pequeño', 'Estudiante universitario o Profesor', 'Trabajador o voluntario de ONG ', 'Afiliación con el gobierno', 'Otro'])
            profession_type = ', '.join(profession_type)
            professional_title = st.text_input('Titulo professional')
            st.divider()

            works_gov = st.checkbox('Trabaja para el Gobierno')
            if works_gov:
                geographic_level = st.multiselect('Nivel geográfico', ['Nacional', 'Municipal', 'Comunidad'])
                geographic_level = ', '.join(geographic_level)
                sector = st.selectbox('Sector', ['Servicios sociales', 'Security', 'Otro']) # security not translated
                st.divider()

            works_org = st.checkbox('Works for Organization') # not translated
            if works_org: 
                country_of_organization = st.multiselect('Country of Organization', ['Honduras', 'El Salvador', 'US', 'Other']) # not translated
                country_of_organization = ', '.join(country_of_organization)
                geographic_reach = st.multiselect('Geographic Reach', ['Nacional', 'Municipal', 'Comunidad']) # not translated
                geographic_reach = ', '.join(geographic_reach)
                years_of_operation = st.selectbox('Tiempo de trabajo', ['Menos de 5 años', '5-9 años', '10-19 años', '20+ años'])
                formality = st.selectbox('Formalidad', ['ONG formal', 'Colectivo informal', 'En proceso de formalización'])
                types_of_activities = st.multiselect('Tipos de actividades', ['Defensa de derechos y políticas públicas', "Apoyo a víctimas", "Educación y desarrollo social", "Investigación y periodismo", "Redes y plataformas", "Otro"])
                types_of_activities = ', '.join(types_of_activities)
                types_of_violence = st.multiselect('Tipos de violencia', ['Violencia de pandillas', 'Delitos comunes', 'Violencia sexual', 'Violencia estatal', 'Otro'])
                types_of_violence = ', '.join(types_of_violence)
                org_works_in_conflict_zone = st.checkbox('La organización trabaja en zonas de conflicto')
        
        with st.expander('Ha vivido experiencias de violencia'):
            cur_lives_in_conflict_zone = st.checkbox('Actualmente vive en una zona de conflicto') 
            if cur_lives_in_conflict_zone:
                cur_name_of_conflict_zone = st.text_input('Nombre de la zona de conflicto actual')
                gang_faction = st.selectbox('Facción de pandillas', ['MS-13', 'Barrio-18', 'Otro'])
                st.divider()
            
            pre_lives_in_conflict_zone = st.checkbox('Anteriormente vivió en una zona de conflicto')
            if pre_lives_in_conflict_zone:
                pre_name_of_conflict_zone = st.text_input('Nombre de la zona de conflicto anterior')
                st.divider()
            
            works_in_conflict_zone = st.checkbox('Trabaja en una zona de conflicto')
            lived_experience_of_violence = st.checkbox('Experiencia vivida de violencia')
            if lived_experience_of_violence:
                violence_type = st.multiselect('Tipos de violencia', ['Violencia de pandillas', 'Delitos comunes', 'Violencia sexual', 'Violencia estatal', 'Otro'])
                if 'Violencia de pandillas' in violence_type:
                    gang_violence_type = st.multiselect('Tipo de violencia de pandillas', ['Desplazamiento forzado', 'Extorsión', 'Reclutamiento', 'Agresión sexual', 'Otro'])
                    gang_violence_types = ', '.join(gang_violence_type)
                if 'Delitos comunes' in violence_type:
                    random_violence_type = st.multiselect('Tipo de violencia aleatoria', ['Robo a mano armada', 'Robo sin arma', 'Secuestro', 'Allanamiento de morada', 'Otro'])
                    random_violence_types = ', '.join(random_violence_type)
                if 'Violencia sexual' in violence_type:
                    intimate_violence_type = st.multiselect('Tipo de violencia íntima', ['Agresión sexual', 'Violencia de pareja', 'Violencia contra personas LGBTQ', 'Otro'])
                    intimate_violence_types = ', '.join(intimate_violence_type)
                if 'Violencia estatal' in violence_type:
                    state_violence_type = st.multiselect('Tipo de violencia estatal', ['Miedo a la detención', 'Detención arbitraria de familiares cercanos', 'Violencia policial', 'Violencia en prisión', 'Represión política', 'Otro'])
                    state_violence_types = ', '.join(state_violence_type)
                if 'Otro' in violence_type:
                    other_violence_type = st.text_input('Otro tipo de violencia')
                    other_violence_types = ', '.join(other_violence_type)
                st.divider()
                violence_types = ', '.join(violence_type)
                if 'Violencia de pandillas' not in violence_type:
                    gang_violence_types = ''
                if 'Delitos comunes' not in violence_type: # from communes
                    random_violence_types = ''
                if 'Violencia sexual' not in violence_type:
                    intimate_violence_types = ''
                if 'Violencia estatal' not in violence_type:
                    state_violence_types = ''
                if 'Otro' not in violence_type:
                    other_violence_types = ''

        if st.button('Entregar'): # not translated; my own
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
            st.success('Datos del entrevistado actualizados correctamente')

    if st.button('View Interviewee Data'):
        data = db.cur.execute("SELECT * FROM interviewee").fetchall()
        st.write(data)
        