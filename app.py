import streamlit as st
from sql_utils import DatabaseManager
from auth_utils import Authentication, setup_submodule
from datetime import datetime
import os

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INTERVIEWERS = [
    "Anjuli", "Kathy", "Laura", "Justin",
    "Jennifer Ramirez", "Jazmín Marroquin", "Alejandro Manzur",
    "José Angel Moreno", "Obed Cruz", "Keren Castellanos",
    "Estefanía Valladares", "Katherine Martínez", "Otro",
]

AGE_RANGES      = ['Menor de 18 años', '18-29', '30-59', '60+']
GENDERS         = ['Masculino', 'Femenino', 'Trans', 'No binario', 'Desconocido o otro']
COUNTRIES       = ['Honduras', 'El Salvador', 'US', 'Otro']
PROFESSION_TYPES = [
    'Sector de Transporte', 'Negocios pequeño',
    'Estudiante universitario o Profesor', 'Trabajador o voluntario de ONG',
    'Afiliación con el gobierno', 'Otro',
]
GEO_LEVELS      = ['Nacional', 'Municipal', 'Comunidad']
SECTORS         = ['Servicios sociales', 'Seguridad', 'Otro']
ORG_YEARS       = ['Menos de 5 años', '5-9 años', '10-19 años', '20+ años']
FORMALITIES     = ['ONG formal', 'Colectivo informal', 'En proceso de formalización']
ACTIVITY_TYPES  = [
    'Defensa de derechos y políticas públicas', 'Apoyo a víctimas',
    'Educación y desarrollo social', 'Investigación y periodismo',
    'Redes y plataformas', 'Otro',
]
VIOLENCE_TYPES  = ['Violencia de pandillas', 'Delitos comunes', 'Violencia sexual', 'Violencia estatal', 'Otro']
GANG_VIOLENCE   = ['Desplazamiento forzado', 'Extorsión', 'Reclutamiento', 'Agresión sexual', 'Otro']
RANDOM_VIOLENCE = ['Robo a mano armada', 'Robo sin arma', 'Secuestro', 'Hurto', 'Invasión en la casa']
INTIMATE_VIOLENCE = [
    'Agresión sexual', 'Violencia de pareja / física', 'Violencia emocional de una pareja',
    'Violencia contra personas LGBTQ', 'Acoso y cosificación', 'Otro',
]
STATE_VIOLENCE  = [
    'Miedo a la detención', 'Detención arbitraria de familiares cercanos', 'Violencia policial',
    'Conflictos armados de la policia en la colonia', 'Violencia en prisión', 'Represión política',
    'Allanamiento de morada', 'Llamada anónima', 'Intimidación de policíales o militares',
    'Acoso de policiales o militares', 'Otro',
]
DISCRIMINATION_TYPES = [
    'Clase Social', 'Edad', 'Sexo', 'Orientación/Identidad sexual',
    'Discapacidad', 'Etnia', 'Lugar de procedencia', 'Condición de Salud', 'Otro',
]
GANG_FACTIONS   = ['MS-13', 'Barrio-18', 'Otro']
CONSENT_OPTIONS = ['Si', 'No', 'Parcial']
INTERVIEW_LOCALES = ['En Persona', 'Virtual']

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def multiselect_with_defaults(label, options, defaults_str, key=None):
    """
    Renders a multiselect pre-populated from a comma-separated string of defaults.
    Any saved values not in the current options list are added dynamically.
    """
    saved = [v.strip() for v in defaults_str.split(', ')] if defaults_str else []
    all_options = list(dict.fromkeys(options + [v for v in saved if v not in options]))
    kwargs = dict(default=saved)
    if key:
        kwargs['key'] = key
    return st.multiselect(label, all_options, **kwargs)


def render_violence_subfields(selected_types, defaults=None, key_suffix=""):
    """
    Renders conditional sub-fields for each selected violence type.
    Returns a dict of {field_name: comma-separated string}.
    defaults is a dict of field_name -> comma-separated string (for update mode).
    """
    defaults = defaults or {}
    results = {
        'gang_violence_type': '',
        'random_crime_type': '',
        'intimate_violence_type': '',
        'state_violence_type': '',
        'other_violence_type': '',
    }
    if 'Violencia de pandillas' in selected_types:
        sel = multiselect_with_defaults(
            'Tipo de violencia de pandillas', GANG_VIOLENCE,
            defaults.get('gang_violence_type', ''), key=f'gang{key_suffix}')
        results['gang_violence_type'] = ', '.join(sel)

    if 'Delitos comunes' in selected_types:
        sel = multiselect_with_defaults(
            'Delitos comunes', RANDOM_VIOLENCE,
            defaults.get('random_crime_type', ''), key=f'random{key_suffix}')
        results['random_crime_type'] = ', '.join(sel)

    if 'Violencia sexual' in selected_types:
        sel = multiselect_with_defaults(
            'Tipo de violencia íntima', INTIMATE_VIOLENCE,
            defaults.get('intimate_violence_type', ''), key=f'intimate{key_suffix}')
        results['intimate_violence_type'] = ', '.join(sel)

    if 'Violencia estatal' in selected_types:
        sel = multiselect_with_defaults(
            'Tipo de violencia estatal', STATE_VIOLENCE,
            defaults.get('state_violence_type', ''), key=f'state{key_suffix}')
        results['state_violence_type'] = ', '.join(sel)

    if 'Otro' in selected_types:
        val = st.text_input('Otro tipo de violencia',
                            value=defaults.get('other_violence_type', ''),
                            key=f'other{key_suffix}')
        results['other_violence_type'] = val

    return results


def fetch_row_as_dict(db, case_no):
    """Returns a single interviewee row as a dict, keyed by column name."""
    db.cur.execute("SELECT * FROM interviewee WHERE case_no = ?", (case_no,))
    columns = [desc[0] for desc in db.cur.description]
    row = db.cur.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

# ---------------------------------------------------------------------------
# Form sections  (return dicts so callers can collect all fields cleanly)
# ---------------------------------------------------------------------------

def render_interview_details(defaults=None):
    d = defaults or {}
    result = {}

    result['case_no']   = st.text_input('Número de caso en Excel', value=d.get('case_no', ''))
    result['date']      = st.date_input('Fecha de hoy',
                                         value=datetime.strptime(d['date'], '%Y-%m-%d').date()
                                         if d.get('date') else datetime.today())
    result['pseudonym'] = st.text_input('Seudónimo', value=d.get('pseudonym', ''))
    result['recorded']  = st.checkbox('Grabación', value=bool(d.get('recorded', False)))

    consent = st.selectbox('Consentimiento', CONSENT_OPTIONS,
                           index=CONSENT_OPTIONS.index(d['consent']) if d.get('consent') in CONSENT_OPTIONS else 0)
    result['consent'] = consent
    result['partial_consent'] = (
        st.text_area('Consentimiento parcial', value=d.get('partial_consent') or '')
        if consent == 'Parcial' else None
    )

    past_interviews = st.number_input('Número total de entrevistas', value=int(d.get('past_interviews', 1)), min_value=1)
    result['past_interviews'] = past_interviews

    saved_dates = d.get('past_dates', '').split(', ') if d.get('past_dates') else []
    past_dates = []
    for i in range(past_interviews):
        default_date = datetime.strptime(saved_dates[i], '%Y-%m-%d').date() if i < len(saved_dates) else datetime.today()
        past_dates.append(st.date_input(f'Fecha de entrevista {i+1}', key=f'past_date_{i}', value=default_date))
    result['past_dates'] = ', '.join(str(d) for d in past_dates)

    result['your_name'] = st.selectbox(
        'Local de Entrevista', INTERVIEW_LOCALES,
        index=INTERVIEW_LOCALES.index(d['your_name']) if d.get('your_name') in INTERVIEW_LOCALES else 0)

    saved_interviewers = d.get('interviewer', '').split(', ') if d.get('interviewer') else []
    all_interviewers = list(dict.fromkeys(INTERVIEWERS + saved_interviewers))
    interviewer = st.multiselect('Entrevistador', all_interviewers, default=saved_interviewers)
    if 'Otro' in interviewer:
        custom = st.text_input('Otro Entrevistador')
        interviewer = [v for v in interviewer if v != 'Otro'] + ([custom] if custom else [])
    result['interviewer'] = ', '.join(dict.fromkeys(interviewer))  # deduplicate, preserve order

    result['date'] = str(result['date'])  # convert datetime.date to string
    result['partial_consent'] = str(result['partial_consent']) or ''  # convert None to empty string

    return result


def render_demographic_info(defaults=None):
    d = defaults or {}
    result = {}
    result['age_range'] = st.selectbox(
        'Rango de edad', AGE_RANGES,
        index=AGE_RANGES.index(d['age_range']) if d.get('age_range') in AGE_RANGES else 0)
    result['gender'] = st.selectbox(
        'Género', GENDERS,
        index=GENDERS.index(d['gender']) if d.get('gender') in GENDERS else 0)
    result['country'] = ', '.join(
        multiselect_with_defaults('País', COUNTRIES, d.get('country', '')))
    return result


def render_professional_info(defaults=None):
    d = defaults or {}
    result = {}

    result['profession_type'] = ', '.join(
        multiselect_with_defaults('Tipo de profesiones', PROFESSION_TYPES, d.get('profession_type', '')))
    result['professional_title'] = st.text_input('Titulo profesional', value=d.get('professional_title', ''))
    st.divider()

    works_gov = st.checkbox('Trabaja para el Gobierno', value=bool(d.get('works_in_gov', False)))
    result['works_in_gov'] = works_gov
    result['geographic_level'] = ''
    result['sector'] = ''
    if works_gov:
        result['geographic_level'] = ', '.join(
            multiselect_with_defaults('Nivel geográfico', GEO_LEVELS, d.get('geographic_level', '')))
        result['sector'] = st.selectbox(
            'Sector', SECTORS,
            index=SECTORS.index(d['sector']) if d.get('sector') in SECTORS else 0)
    st.divider()

    works_org = st.checkbox('Trabaja para una organización', value=bool(d.get('works_in_org', False)))
    result['works_in_org'] = works_org
    result['country_of_organization'] = ''
    result['geographic_reach'] = ''
    result['years_of_operation'] = ''
    result['formality'] = ''
    result['types_of_activities'] = ''
    result['types_of_violence'] = ''
    result['org_works_in_conflict'] = False
    if works_org:
        result['country_of_organization'] = ', '.join(
            multiselect_with_defaults('País de la Organización', COUNTRIES, d.get('country_of_organization', '')))
        result['geographic_reach'] = ', '.join(
            multiselect_with_defaults('Alcance geográfico', GEO_LEVELS, d.get('geographic_reach', '')))
        result['years_of_operation'] = st.selectbox(
            'Tiempo que la organización está activa', ORG_YEARS,
            index=ORG_YEARS.index(d['years_of_operation']) if d.get('years_of_operation') in ORG_YEARS else 0)
        result['formality'] = st.selectbox(
            'Formalidad', FORMALITIES,
            index=FORMALITIES.index(d['formality']) if d.get('formality') in FORMALITIES else 0)
        result['types_of_activities'] = ', '.join(
            multiselect_with_defaults('Tipos de actividades', ACTIVITY_TYPES, d.get('types_of_activities', '')))
        result['types_of_violence'] = ', '.join(
            multiselect_with_defaults('Tipos de violencia', VIOLENCE_TYPES, d.get('types_of_violence', '')))
        result['org_works_in_conflict'] = st.checkbox(
            'La organización trabaja en zonas de conflicto', value=bool(d.get('org_works_in_conflict', False)))

    return result


def render_conflict_and_violence(defaults=None, key_suffix=""):
    d = defaults or {}
    result = {}

    # Current conflict zone
    cur_conflict = st.checkbox('Actualmente vive en una zona de conflicto',
                               value=bool(d.get('currently_lives_in_conflict', False)))
    result['currently_lives_in_conflict'] = cur_conflict
    result['cur_name_of_conflict'] = ''
    result['gang_faction'] = ''
    if cur_conflict:
        result['cur_name_of_conflict'] = st.text_input(
            'Nombre de la zona de conflicto actual', value=d.get('cur_name_of_conflict', ''))
        gf = d.get('gang_faction', '')
        result['gang_faction'] = st.selectbox(
            'Facción de pandillas', GANG_FACTIONS,
            index=GANG_FACTIONS.index(gf) if gf in GANG_FACTIONS else 0)
        st.divider()

    # Previous conflict zone
    prev_conflict = st.checkbox('Anteriormente vivió en una zona de conflicto',
                                value=bool(d.get('previously_lives_in_conflict', False)))
    result['previously_lives_in_conflict'] = prev_conflict
    result['prev_name_of_conflict'] = ''
    if prev_conflict:
        result['prev_name_of_conflict'] = st.text_input(
            'Nombre de la zona de conflicto anterior', value=d.get('prev_name_of_conflict', ''))
        st.divider()

    result['works_in_conflict'] = st.checkbox('Trabaja en una zona de conflicto',
                                              value=bool(d.get('works_in_conflict', False)))

    # Lived experience of violence
    lived = st.checkbox('Experiencia vivida de violencia',
                        value=bool(d.get('lived_experience_of_violence', False)))
    result['lived_experience_of_violence'] = lived
    result['violence_types'] = ''
    sub_defaults = {k: d.get(k, '') for k in ['gang_violence_type', 'random_crime_type',
                                               'intimate_violence_type', 'state_violence_type',
                                               'other_violence_type']}
    sub_results = {k: '' for k in sub_defaults}

    if lived:
        selected_violence = multiselect_with_defaults(
            'Tipos de violencia', VIOLENCE_TYPES, d.get('violence_types', ''),
            key=f'violence_types{key_suffix}')
        result['violence_types'] = ', '.join(selected_violence)
        sub_results = render_violence_subfields(selected_violence, sub_defaults, key_suffix)
        st.divider()

    result.update(sub_results)

    # Discrimination
    faced_discrimination = st.checkbox(
        '¿Existen otros tipos de discriminación identificados en este caso?',
        value=bool(d.get('discrimination_type', '')))
    result['discrimination_type'] = ''
    if faced_discrimination:
        result['discrimination_type'] = ', '.join(
            multiselect_with_defaults('Tipo de discriminación', DISCRIMINATION_TYPES,
                                      d.get('discrimination_type', '')))

    return result

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

if st.session_state.get('submodule_setup') is None:
    setup_submodule()
    st.session_state['submodule_setup'] = True

config_path = os.path.join('sensitive_data_for_fahlberg_interview_db', 'config.yaml')
db_path     = os.path.join('sensitive_data_for_fahlberg_interview_db', 'db.sql')

st.title('Base de datos de entrevistas de Fahlberg')

auth = Authentication(config_path)
auth.login()
auth.display()

db = DatabaseManager(path=db_path)

# ---------------------------------------------------------------------------
# Main form (authenticated users only)
# ---------------------------------------------------------------------------

if st.session_state.get('authentication_status'):
    name_of_user   = st.text_input('Nombre de la persona llenando este formulario.')
    mode           = st.radio('Modo', ['Agregar nuevo entrevistado', 'Actualizar entrevistado existente'])

    # -----------------------------------------------------------------------
    # UPDATE mode
    # -----------------------------------------------------------------------
    if mode == 'Actualizar entrevistado existente':
        st.subheader('Actualizar entrevistado existente')

        case_nos = db.cur.execute("SELECT case_no FROM interviewee").fetchall()
        if not case_nos:
            st.error('No hay datos en la base de datos. Por favor, agregue un nuevo entrevistado primero.')
            st.stop()

        print(case_nos, case_nos[0], type(case_nos), type(case_nos[0]))
        selected = st.selectbox('Número de caso', case_nos, format_func=lambda x: x[0])
        case_no  = selected[0]
        data     = fetch_row_as_dict(db, case_no)

        if not data:
            st.error('No se encontraron datos para este número de caso.')
        else:
            with st.expander('Detalles de la entrevista'):
                interview = render_interview_details(data)
            with st.expander('Información demográfica'):
                demographic = render_demographic_info(data)
            with st.expander('Información profesional'):
                professional = render_professional_info(data)
            with st.expander('Ha vivido experiencias de violencia'):
                conflict = render_conflict_and_violence(data, key_suffix='_update')

            if st.button('Actualizar'):
                try:
                    db.update('interviewee', case_no, **{k: v for k, v in {**interview, **demographic, **professional, **conflict}.items() if k != 'case_no'})
                    st.success('Datos del entrevistado actualizados correctamente.')
                except Exception as e:
                    st.error(str(e))

    # -----------------------------------------------------------------------
    # ADD mode
    # -----------------------------------------------------------------------
    else:
        st.subheader('Agregar nuevo entrevistado')

        with st.expander('Detalles de la entrevista'):
            interview = render_interview_details()
        with st.expander('Información demográfica'):
            demographic = render_demographic_info()
        with st.expander('Información profesional'):
            professional = render_professional_info()
        with st.expander('Ha vivido experiencias de violencia'):
            conflict = render_conflict_and_violence(key_suffix='_add')

        all_fields = {**interview, **demographic, **professional, **conflict}
        for k, v in all_fields.items():
            print(f"{k}: {v}, {type(v)}")  # debug

        if st.button('Entregar'):
            if not name_of_user:
                st.error('Por favor ingrese su nombre antes de enviar.')
                st.stop()
            if not interview.get('case_no'):
                st.error('Por favor ingrese el número de caso.')
                st.stop()

            try:
                db.insert('interviewee', user=name_of_user, **interview, **demographic, **professional, **conflict)
                st.success('Nuevo entrevistado agregado correctamente.')
            except Exception as e:
                st.error(str(e))


    # -----------------------------------------------------------------------
    # Debug view
    # -----------------------------------------------------------------------
    if st.button('Ver datos de entrevistados'):
        rows = db.cur.execute("SELECT * FROM interviewee").fetchall()
        st.write(rows)