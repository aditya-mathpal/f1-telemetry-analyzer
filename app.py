import streamlit as st
import fastf1
import matplotlib.pyplot as plt

# Cache to avoid repeated API calls
@st.cache_data
def get_schedule(year):
    return fastf1.get_event_schedule(year)

@st.cache_data
def get_session_data(year, circuit, session):
    session_obj = fastf1.get_session(year, circuit, session)
    session_obj.load()
    return session_obj

st.sidebar.header("Select")

year = st.sidebar.selectbox("Year:", ['Select Year'] + list(range(2025, 2017, -1)))

if year != 'Select Year':
    schedule = get_schedule(year)
    circuits = ['Select a Circuit'] + schedule['EventName'].tolist()
    selected_circuit = st.sidebar.selectbox("Circuit:", circuits)
    
    available_sessions = ['Select Session'] + ['Practice 1', 'Practice 2', 'Practice 3', 'Qualifying', 'Race']
    session_type = st.sidebar.selectbox("Session:", available_sessions)
    
    if selected_circuit != 'Select a Circuit' and session_type != 'Select Session':
        try:
            with st.spinner('Loading session data...'):
                session = get_session_data(year, selected_circuit, session_type)
                driver_mapping = dict(zip(session.results['FullName'], session.results['Abbreviation']))
                selected_driver_names = st.sidebar.multiselect("Drivers:", list(driver_mapping.keys()))
                selected_drivers = [driver_mapping[name] for name in selected_driver_names]
            if selected_drivers:
                with st.spinner('Loading telemetry...'):
                    lap, tel = [], []
                    for _ in selected_drivers:
                        fastest = session.laps.pick_drivers(_).pick_fastest()
                        lap.append(fastest)
                        tel.append(fastest.get_car_data().add_distance())
                fig, ax = plt.subplots(figsize = (12, 8))
                for i, (driver_code, telemetry) in enumerate(zip(selected_drivers, tel)):
                    driver_name = [name for name, code in driver_mapping.items() if code == driver_code][0]
                    ax.plot(telemetry['Distance'], telemetry['Speed'], label = driver_name, alpha = 0.7)
                ax.set_xlabel('Distance (m)', fontsize = 16)
                ax.set_ylabel('Speed (km/h)', fontsize = 16)
                ax.set_title(f'Speed Comparison - Fastest Lap - {selected_circuit} {year} {session_type}', fontsize = 20)
                ax.legend(fontsize = 14)
                ax.grid(True, alpha=0.3, linewidth = 1.5)
                st.pyplot(fig)
        except Exception as e:
            st.error(f'Error loading data: {str(e)}')