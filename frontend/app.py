import streamlit as st
import requests
import about
import diagnostic

# Page config must be the absolute first Streamlit command
st.set_page_config(
    page_title="MindMantra | AI Diagnostic",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

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
# PAGE ROUTER
# ==========================================
if page == "AI Diagnostic Engine":
    diagnostic.show_diagnostic(is_online, safe_rerun)
elif page == "About the Project":
    about.about()

# --- Global Footer ---
st.markdown("---")
st.caption("© 2025 Final Year Project | School of Engineering, Pokhara University – Nepal")