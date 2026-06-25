import streamlit as st
import requests
import time
import random
import about
# --- Configuration ---
API_BASE_URL = "http://localhost:8000/api"

# Page config must be the absolute first Streamlit command
st.set_page_config(
    page_title="MindMantra | AI Diagnostic",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Motivational Quotes Pool ---
MOTIVATIONAL_QUOTES = [
    "\"You don't have to control your thoughts. You just have to stop letting them control you.\" — Dan Millman",
    "\"Healing takes time, and asking for help is a courageous step. You are never alone in this journey.\"",
    "\"Your mental health is a priority. Your happiness is essential. Your self-care is a necessity.\"",
    "\"It is okay to not be okay, but you don't have to navigate it in silence.\"",
    "\"This feeling will pass. You are stronger, more resilient, and more capable than you think.\"",
    "\"You are not your illness. You have an individual story, a beautiful mind, and a bright future.\"",
    "\"Self-care is how you take your power back.\" — Lalah Delia",
    "\"Sometimes the bravest thing you can do is just to take things one day at a time.\""
]

# --- Backward-Compatible Rerun Helper ---
def safe_rerun():
    """Ensures compatibility across all Streamlit versions."""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# --- Connection Diagnostic Check ---
def check_backend_health():
    """Quickly ping backend to verify it is online and responsive."""
    try:
        response = requests.get("http://localhost:8000/", timeout=1.5)
        if response.status_code == 200:
            return True, response.json().get("status", "online")
    except Exception:
        pass
    return False, "offline"

# --- Session State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
if 'user_text' not in st.session_state:
    st.session_state.user_text = ""
if 'matched_symptoms' not in st.session_state:
    st.session_state.matched_symptoms = []
if 'confirmed_symptom_ids' not in st.session_state:
    st.session_state.confirmed_symptom_ids = []
if 'diagnostic_data' not in st.session_state:
    st.session_state.diagnostic_data = {}
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'quote' not in st.session_state:
    st.session_state.quote = random.choice(MOTIVATIONAL_QUOTES)

def reset_session():
    st.session_state.step = 'input'
    st.session_state.user_text = ""
    st.session_state.matched_symptoms = []
    st.session_state.confirmed_symptom_ids = []
    st.session_state.diagnostic_data = {}
    st.session_state.current_q_index = 0
    # Pick a fresh quote when restarting
    st.session_state.quote = random.choice(MOTIVATIONAL_QUOTES)

# --- Helper API Functions ---
def fetch_semantic_matches(text):
    try:
        response = requests.post(
            f"{API_BASE_URL}/match-symptoms", 
            json={"user_text": text, "threshold": 0.35},
            timeout=5.0
        )
        response.raise_for_status()
        return response.json().get("matches", [])
    except Exception as e:
        st.error(f"❌ Backend Connection Error: {e}")
        return []

def fetch_diagnosis(symptom_ids):
    try:
        response = requests.post(
            f"{API_BASE_URL}/diagnose", 
            json={"symptom_ids": symptom_ids},
            timeout=3.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Diagnosis Engine Error: {e}")
        return {}

def fetch_precautions(illness_name):
    try:
        response = requests.get(
            f"{API_BASE_URL}/precautions", 
            params={"condition": illness_name},
            timeout=3.0
        )
        response.raise_for_status()
        return response.json().get("precautions", [])
    except Exception as e:
        return ["Please consult a healthcare professional for specific guidance."]

# --- Sidebar Navigation & System Status ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["AI Diagnostic Engine", "About the Project"])

st.sidebar.markdown("---")
st.sidebar.title("⚙️ System Status")
is_online, status_msg = check_backend_health()

if is_online:
    st.sidebar.success(f"● Backend Service: {status_msg.upper()}")
else:
    st.sidebar.error("● Backend Service: OFFLINE")
    if st.sidebar.button("🔄 Retry Connection"):
        safe_rerun()

# ==========================================
# PAGE 1: AI DIAGNOSTIC ENGINE (MAIN PAGE)
# ==========================================
if page == "AI Diagnostic Engine":
    st.title("🧠 MindMantra v2.0")
    st.markdown("### Mental Health Condition Predictor")
    
    # Render the dynamic motivational quote block beautifully at the top
    st.markdown(f"> {st.session_state.quote}")
    st.write("") # Spacer

    if not is_online:
        st.warning("⚠️ MindMantra is currently offline. Please start the FastAPI backend server in your terminal to continue.")
        st.stop()

    # STEP 1: FREE TEXT INPUT
    if st.session_state.step == 'input':
        st.write("Describe how you are feeling in your own words. The AI will analyze your text to find core symptoms.")
        
        text_input = st.text_area("How have you been feeling lately?", 
                                  placeholder="e.g., I've been feeling extremely tired, I can't concentrate on my work, and I'm always worried...",
                                  height=150)
        
        if st.button("Analyze Symptoms", type="primary"):
            if len(text_input.strip()) < 10:
                st.warning("Please provide a bit more detail so the AI can understand.")
            else:
                with st.spinner("Running NLP Semantic Search..."):
                    matches = fetch_semantic_matches(text_input)
                    if matches:
                        st.session_state.matched_symptoms = matches
                        st.session_state.step = 'confirm_symptoms'
                        safe_rerun()
                    else:
                        st.info("No strong symptom matches found. Try describing your physical or emotional state differently.")

    # STEP 2: CONFIRM NLP MATCHES
    elif st.session_state.step == 'confirm_symptoms':
        st.success("Analysis Complete!")
        st.write("We extracted the following clinical symptoms from your description:")
        
        selected_ids = []
        for sym in st.session_state.matched_symptoms:
            if st.checkbox(f"**{sym['name'].replace('_', ' ').title()}** (Confidence: {sym['score']*100:.0f}%)", value=True):
                selected_ids.append(sym['id'])
                
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Proceed to Diagnosis", type="primary"):
                if not selected_ids:
                    st.error("Please select at least one symptom to proceed.")
                else:
                    st.session_state.confirmed_symptom_ids = selected_ids
                    with st.spinner("Consulting Diagnostic Engine..."):
                        diag_data = fetch_diagnosis(selected_ids)
                        st.session_state.diagnostic_data = diag_data
                        
                        if diag_data.get('complete') or not diag_data.get('next_questions'):
                            st.session_state.step = 'results'
                        else:
                            st.session_state.step = 'questions'
                    safe_rerun()
        with col2:
            if st.button("Go Back"):
                st.session_state.step = 'input'
                safe_rerun()

    # STEP 3: DYNAMIC FOLLOW-UP QUESTIONS
    elif st.session_state.step == 'questions':
        questions = st.session_state.diagnostic_data.get("next_questions", [])
        
        if st.session_state.current_q_index < len(questions):
            current_q = questions[st.session_state.current_q_index]
            st.progress((st.session_state.current_q_index) / len(questions), text="Diagnostic Interview Progress")
            
            st.markdown(f"### Question {st.session_state.current_q_index + 1}")
            st.info(current_q['text'])
            st.write("Please reflect on this. Does this apply to you?")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Yes, it applies", key=f"yes_{st.session_state.current_q_index}"):
                    st.session_state.current_q_index += 1
                    safe_rerun()
            with col2:
                if st.button("No / Not sure", key=f"no_{st.session_state.current_q_index}"):
                    st.session_state.current_q_index += 1
                    safe_rerun()
        else:
            with st.spinner("Finalizing Results..."):
                time.sleep(1)
                st.session_state.step = 'results'
                safe_rerun()

    # STEP 4: RESULTS & PRECAUTIONS
    elif st.session_state.step == 'results':
        st.balloons()
        st.header("Diagnostic Results")
        
        top_conditions = st.session_state.diagnostic_data.get("top_conditions", [])
        
        if not top_conditions:
            st.warning("We could not match your symptoms to a specific illness in our database with high confidence.")
        else:
            primary_condition = top_conditions[0]
            st.success(f"### Primary Match: {primary_condition['illness_name']}")
            st.write(f"**Relevance Score:** {primary_condition['score']*100:.1f}% based on provided symptoms.")
            
            st.markdown("---")
            st.markdown("### Recommended Precautions")
            
            precautions = fetch_precautions(primary_condition['illness_name'])
            for idx, prec in enumerate(precautions):
                st.markdown(f"✅ {prec}")
                
            if len(top_conditions) > 1:
                st.markdown("---")
                st.markdown("**Other possible considerations:**")
                for cond in top_conditions[1:3]:
                    st.caption(f"- {cond['illness_name']} ({cond['score']*100:.1f}%)")

        st.markdown("---")
        if st.button("Start New Session", type="primary"):
            reset_session()
            safe_rerun()


# ==========================================
# PAGE 2: ABOUT THE PROJECT
# ==========================================
elif page == "About the Project":
    about.about()
    
   
    
st.markdown("---")
st.caption("© 2025 Final Year Project | School of Engineering, Pokhara University – Nepal")