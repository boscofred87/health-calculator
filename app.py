import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Health Metrics Calculator", page_icon="⚖️", layout="centered")

# ==========================================
# 🔐 CONFIGURATION: SET YOUR ADMIN PASSWORD HERE
# ==========================================
ADMIN_PASSWORD = "edisader" 

# ==========================================
# 🎨 BACKGROUND IMAGE & GLASS UI STYLING
# ==========================================
BACKGROUND_IMAGE_URL = "https://unsplash.com"

st.markdown(f"""
    <style>
    /* Full screen background image */
    .stApp {{
        background-image: url("{BACKGROUND_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Frosted glass white backing for form blocks and titles */
    [data-testid="stForm"], .stMarkdown, .stMetric, [data-testid="stExpander"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }}
    
    /* Clear custom colors for results cards */
    .metric-card {{
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }}
    .status-low {{ background-color: #2e7d32; }}      /* Green */
    .status-med {{ background-color: #f9a825; }}      /* Orange/Yellow */
    .status-high {{ background-color: #c62828; }}     /* Red */
    .status-info {{ background-color: #1565c0; }}     /* Blue */

    /* 🛡️ PERMANENT GLOBAL BLANKET BLOCKER FOR GITHUB HOOKS 🛡️ */
    header, [data-testid="stHeader"] {{
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }}
    
    /* Extra aggressive fallbacks to catch fork links, logos, and floating containers */
    iframe[title="streamlitApp"], .viewerBadge_container__176oo, .styles_viewerBadge__1yB5_, 
    .viewerBadge_link__1S137, [data-testid="stGitHubIcon"], a[href*="github.com"], 
    .stDeployButton, Button[title="View source code on GitHub"],
    div[class*="Profile"], div[class*="Badge"], [data-testid="stConnectionStatus"],
    .styles_floatingContainer__2wK_A, div[class*="floatingContainer"], footer, .stActionButton {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 📐 MEDICAL FORMULA FUNCTIONS
# ==========================================
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

# Establish connection to Google Sheet globally
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 📊 SIDEBAR: ADMIN DASHBOARD LOGIN
# ==========================================
st.sidebar.title("⚙️ Management")
with st.sidebar.expander("🔐 Admin Login"):
    input_password = st.text_input("Enter Password", type="password")
    
    if input_password == ADMIN_PASSWORD:
        st.success("Access Granted!")
        show_dashboard = True
    elif input_password != "":
        st.error("Incorrect password.")
        show_dashboard = False
    else:
        show_dashboard = False

# ==========================================
# 🖥️ MAIN LOGIC DISPLAY CHOICE
# ==========================================
if show_dashboard:
    st.title("📊 Analytics Dashboard (Admin View)")
    st.write("Real-time summary statistics gathered from your spreadsheet submissions.")
    st.divider()

    try:
        # Read full current data from Google Sheets
        df = conn.read(ttl=0)
        
        if df.empty or len(df) == 0:
            st.info("The spreadsheet is currently empty. Waiting for user submissions!")
        else:
            # 1. High-Level Summary Metrics
            total_users = len(df)
            avg_age = df["Age"].mean() if "Age" in df.columns else 0
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Calculator Uses", f"{total_users} submissions")
            with col_m2:
                st.metric("Average User Age", f"{avg_age:.1f} years old")
                
            st.divider()
            
            # 2. Graphical Categorical Breakdown
            st.subheader("Distribution Breakdown")
            
            tab1, tab2 = st.tabs(["BMI Status Breakdown", "Raw Data Log Table"])
            
            with tab1:
                if "BMI_Status" in df.columns:
                    bmi_counts = df["BMI_Status"].value_counts().reset_index()
                    bmi_counts.columns = ["Category", "Count"]
                    st.bar_chart(data=bmi_counts, x="Category", y="Count", color="#1565c0")
                else:
                    st.warning("Historical data columns mismatch. Try running a clean submission.")
                    
            with tab2:
                st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
                
    except Exception as e:
        st.error("Could not fetch analytics. Please check your Google Sheets permissions.")
        st.caption(f"Technical error reference: {e}")

else:
    # --- DEFAULT MAIN VIEW: THE USER ACCESSIBLE CALCULATOR ---
    st.title("🩺 Adult Health Metrics Calculator")
    st.write("Calculate your metrics, and see how you are doing!")

    # Data Entry Form
    with st.form(key="health_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=None, placeholder="Type your age...")
            sex = st.selectbox("Biological Sex", ["Male", "Female"])
            height = st.number_input("Height (cm)", min_value=50, max_value=250, value=None, placeholder="e.g. 170")
            
        with col2:
            weight = st.number_input("Weight (kg)", min_value=10, max_value=300, value=None, placeholder="e.g. 70")
            waist = st.number_input("Waist Circumference (cm)", min_value=30, max_value=200, value=None, placeholder="e.g. 85")
            
        submit_button = st.form_submit_button(label="Submit Results")

    # Execute calculations and upload when user clicks submit
    if submit_button:
        if age is None or height is None or weight is None or waist is None:
            st.error("⚠️ Please fill in all the empty fields before submitting your metrics.")
        elif age < 20:
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

            # Log to Google Sheets
            try:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Age": age,
                    "Sex": sex,
                    "BMI": round(bmi, 1),
                    "Waist": waist,
                    "BMI_Status": bmi_label,
                    "Metabolic_Risk": waist_label
                }])
                
                existing_df = conn.read(ttl=0)
                updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("✅ Data log recorded anonymously.")
            except Exception as e:
                st.caption("⚠️ Data logging fallback. Calculations generated successfully.")
