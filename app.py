import streamlit as st
import json
import time
from aegis_proxy import SecureGateway

# --- 1. Configuration & Setup ---
st.set_page_config(
    page_title="AEGIS | Secure AI Gateway",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Performance: Cached Initialization ---
# @st.cache_resource is CRITICAL. It ensures we only load the heavy 
# NLP models ONCE. Without this, the app would reload the models on every interaction, causing massive delays.
@st.cache_resource
def get_gateway():
    try:
        return SecureGateway()
    except Exception as e:
        # Fail gracefully if the .env or key is wrong
        st.error(f"🔥 FATAL: Gateway Initialization Failed. Check your .env file.\nError: {e}")
        return None
    
# Initialize the backend
gateway = get_gateway()

# --- 3. UI Layout ---
with st.sidebar:
    st.header("🛡️ Aegis Control Panel")

    # Status Indicator
    if gateway:
        st.success("✅ System Status: ONLINE")
        st.info(f"🔒 Encryption: AES-256 (Fernet)")
        st.info(f"🧠 NLP Engine: Presidio + spaCy")
    else:
        st.error("❌ System Status: OFFLINE")
        st.stop() # Stop execution if backend failed

    st.markdown("---")
    st.markdown("**Session Telemetry:**")
    #Simulation of user context
    user_id = st.text_input("Operator ID", value="SEC-OPS-ALPHA", help="Simulates the ID of the employee using the AI.")
    session_id = st.text_input("Session ID", value="SES-2026-X99", disabled=True)

#Main Content Area
st.title("🛡️ AEGIS Proxy Interface")
st.markdown("""
**Objective:** Intercept and sanitize prompts before they reach public LLMs (OpenAI/Anthropic).
**Status:** Monitoring for PII (SSN, Email) and Secrets (API Keys).
""")

st.markdown("---")

# --- 4. Input Section ---
col1, col2 = st.columns([2,1])

with col1:
    raw_input = st.text_area(
        "📝 Incoming Prompt", 
        height=150, 
        placeholder="Type a prompt here to test the shield...\nExample: 'Debug this code. My key is sk-proj-12345 and email is dev@company.com'",
        help="This simulates an employee trying to send data to ChatGPT."
    )

with col2:
    st.markdown("### ⚡ Actions")
    st.write("Ready to scan prompt for sensitive entities.")
    scan_btn = st.button("🛡️ SCAN & PROTECT", type="primary", use_container_width=True)

 # --- 5. Logic & Results ---
if scan_btn:
    if not raw_input.strip():
        st.warning("⚠️ Input is empty. Please enter a prompt.")
    else:
        # Visual feedback for the user (The "Processing" spinner)
        with st.spinner("🤖 Aegis AI is scanning for threats..."):
            # A slight artificial delay to let the user feel the "work" happening (optional UX touch)
            time.sleep(0.6) 
            
            # CALL THE BACKEND
            sanitized_text, encrypted_blob = gateway.process_prompt(raw_input, user_id=user_id)

        # ERROR HANDLING: Check if the backend returned our custom error string
        if "ERROR:" in sanitized_text:
            st.error(sanitized_text)
        else:
            # --- 6. Display Results (Side by Side) ---
            st.subheader("📊 Inspection Results")

            res_col1, res_col2 = st.columns(2)

            with res_col1:
                st.success("✅ Sanitized Output (Safe for LLM)")
                st.code(sanitized_text, language="text")
                st.caption("Standard NLP models + Custom Regex filters applied.")
            
            with res_col2:
                st.warning("🔐 Encrypted Audit Log (Stored Internally)")
                st.code(encrypted_blob, language="text", wrap_lines=True)
                st.caption("This data is legally retrievable via the encryption key, but invisible to the AI provider.")
            
            # --- 7. SOC Telemetry ---
            st.markdown("---")
            st.markdown("### 📡 SIEM Log Preview")
            with st.expander("View JSON Payload (Sent to Splunk/Sentinel)", expanded=False):
                # Reconstruct the log for display purposes
                log_display = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "event": "AI_PROMPT_SANITIZED",
                    "actor": user_id,
                    "action": "PII_SCRUBBED",
                    "original_length": len(raw_input),
                    "sanitized_length": len(sanitized_text),
                    "encryption_verify": encrypted_blob[:10] + "..."
                }
                st.json(log_display)
