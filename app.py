import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Health Metrics Calculator", page_icon="⚖️", layout="centered")

# Custom CSS for UI cards
st.markdown("""
    <style>
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .status-low { background-color: #2e7d32; }      /* Green */
    .status-med { background-color: #f9a825; }      /* Orange/Yellow */
    .status-high { background-color: #c62828; }     /* Red */
    .status-info { background-color: #1565c0; }     /* Blue */
    </style>
    """, unsafe_allow_html=True)

def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return weight / (height_m ** 2)

def get_bmi_category(bmi):
    if bmi < 18.5: return "Underweight", "status-info"
    elif 18.5 <= bmi < 25: return "Healthy Weight", "status-low"
    elif 25 <= bmi < 30: return "Overweight", "status-med"
    else: return "Obese", "status-high"

def get_waist_risk(waist, sex):
    if sex == "Male":
        if waist < 94: return "Low Risk", "status-low"
        if 94 <= waist < 102: return "Increased Risk", "status-med"
        return "High Risk", "status-high"
    else: # Female
        if waist < 80: return "Low Risk", "status-low"
        if 80 <= waist < 88: return "Increased Risk", "status-med"
        return "High Risk", "status-high"

# App Interface
st.title("🩺 Adult Health Metrics Calculator")
st.write("Calculate your metrics, and see how you are doing!")

# Data Entry Form
with st.form(key="health_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        sex = st.selectbox("Biological Sex", ["Male", "Female"])
        height = st.number_input("Height (cm)", min_value=50, max_value=250, value=170)
        
    with col2:
        weight = st.number_input("Weight (kg)", min_value=10, max_value=300, value=70)
        waist = st.number_input("Waist Circumference (cm)", min_value=30, max_value=200, value=85)
        
    submit_button = st.form_submit_button(label="Submit Results")

# Execute when user clicks submit
if submit_button:
    if age < 20:
        st.warning("⚠️ Adult BMI categories do not apply to individuals under 20. Your data was not logged.")
    else:
        st.divider()
        bmi = calculate_bmi(weight, height)
        bmi_label, bmi_class = get_bmi_category(bmi)
        waist_label, waist_class = get_waist_risk(waist, sex)

        st.subheader("Your Results")
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.markdown(f"""
                <div class="metric-card {bmi_class}">
                    <p style="font-size:0.9rem; margin-bottom:5px;">BMI SCORE</p>
                    <h1 style="margin:0; color:white;">{bmi:.1f}</h1>
                    <p style="margin:0;">{bmi_label}</p>
                </div>
                """, unsafe_allow_html=True)
                
        with res_col2:
            st.markdown(f"""
                <div class="metric-card {waist_class}">
                    <p style="font-size:0.9rem; margin-bottom:5px;">WAIST RISK</p>
                    <h1 style="margin:0; color:white;">{waist} cm</h1>
                    <p style="margin:0;">{waist_label}</p>
                </div>
                """, unsafe_allow_html=True)

        # --- BACKGROUND DATA TRACKER EXTRACTION ---
        try:
            # Establish connection to Google Sheet
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # Formulate the data object
            new_row = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Age": age,
                "Sex": sex,
                "BMI": round(bmi, 1),
                "Waist": waist,
                "BMI_Status": bmi_label,
                "Metabolic_Risk": waist_label
            }])
            
            # Read sheet and safely append data
            existing_df = conn.read()
            updated_df = pd.concat([existing_df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.caption("✅ Data log recorded anonymously.")
        except Exception as e:
            st.caption("⚠️ System busy. Displaying calculations only.")
