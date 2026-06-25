import streamlit as st

def about():
    st.title("ℹ️ About the Project")
    st.markdown("## Mind Mantra: AI Powered Mental Health Support System")
    
    st.write(
        "This project is a final year capstone project developed by a **Computer Engineering student** "
        "from the **School of Engineering, Pokhara University**. It is an AI-powered Mental Health Support System "
        "designed to assist individuals who are experiencing mental health challenges."
    )
    
    st.markdown("### The system offers:")
    st.markdown("- **Symptom-based prediction** of mental health conditions.")
    st.markdown("- **Actionable precautions** to assist individuals on their recovery journey.")
    
    st.write(
        "The goal of this platform is to provide accessible mental health support and encourage "
        "people to talk about their mental well-being without fear of judgment."
    )
    st.write('Explore the first version of MindMantra: https://mindmantra.streamlit.app/')
    
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    
    # Using a structured callout container for the disclaimer text to make it stand out
    st.info(
        "This platform is intended for **educational and research purposes only**. It is not a substitute "
        "for professional medical advice, diagnosis, or treatment. Always seek the guidance of a qualified "
        "mental health professional with any questions or concerns you may have regarding a medical condition.\n\n"
        "The recommendations provided by this system are based on available data and AI models and may not "
        "be fully accurate. The developer and affiliated institutions are not liable for any decisions made "
        "based on the information provided by this system.\n\n"
        "By using this platform, you agree to this disclaimer and understand that the system does not provide "
        "licensed medical or psychiatric care."
    )
    