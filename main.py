import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# ---------------- CONFIGURATION ----------------
st.set_page_config(page_title="AI Plant Disease Identifier", page_icon="🌿")

# Configure Gemini API key securely
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------------- TITLE ----------------
st.title("🌿 AI-Based Plant Disease Identification System")
st.markdown("Upload or capture a leaf image to detect the plant disease, get remedies, precautions, and analysis.")

# ---------------- SESSION STATE ----------------
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

# ---------------- IMAGE INPUT SECTION ----------------
st.header("📸 Upload or Capture Leaf Image")

# Upload file option
uploaded_file = st.file_uploader("Upload a clear image of the affected leaf", type=["jpg", "jpeg", "png"])

# Camera toggle
if st.button("📷 Take Photo"):
    st.session_state.camera_active = not st.session_state.camera_active

# Show camera when active
if st.session_state.camera_active:
    st.info("Click the **round capture button** below to take a photo.")
    camera_input = st.camera_input("Capture image here")
    if camera_input is not None:
        st.session_state.uploaded_image = Image.open(camera_input)
        st.session_state.camera_active = False  # Auto-close camera after capture
else:
    camera_input = None

# Handle uploaded file
if uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file)

# ---------------- IMAGE DISPLAY ----------------
if st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Image", use_column_width=True)
    st.success("✅ Image loaded successfully")

    # ---------------- ANALYSIS BUTTON ----------------
    if st.button("🔍 Identify Disease & Get Analysis"):
        with st.spinner("Analyzing the leaf... Please wait ⏳"):
            try:
                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                st.session_state.uploaded_image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()

                # AI prompt
                prompt = """
You are an expert agricultural AI assistant.
Analyze the given leaf image and identify:
1. The plant name (based on image observation)
2. Disease Name
3. Cause/Pathogen
4. Symptoms
5. Severity Level (Low/Medium/High)
6. Precautions to prevent it
7. Treatment methods (organic and chemical)
8. Impact on crop yield or quality
9. Future preventive measures

Format the response in a clear and structured way.
"""

                # Use lightweight stable Gemini model
                model = genai.GenerativeModel("gemini-1.5-flash")

                # Retry mechanism for 429 or transient errors
                for attempt in range(3):
                    try:
                        response = model.generate_content([
                            prompt,
                            {"mime_type": "image/png", "data": img_bytes}
                        ])
                        break
                    except Exception as e:
                        if "429" in str(e):
                            st.warning("⚠️ API rate limit reached. Retrying in 10 seconds...")
                            time.sleep(10)
                        else:
                            raise e

                # Store and display response
                st.session_state.analysis_result = response.text
                st.subheader("🌾 Disease Detection & Analysis Report")
                st.markdown(st.session_state.analysis_result)

                # Download option
                st.download_button(
                    label="📥 Download Report",
                    data=st.session_state.analysis_result,
                    file_name="plant_disease_analysis.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

# ---------------- RESET FUNCTION ----------------
def trigger_reset():
    st.session_state.reset_triggered = True

st.button("🔄 Reset", on_click=trigger_reset)

# Handle reset outside callback
if st.session_state.reset_triggered:
    # Delay slightly for clean rerun
    time.sleep(0.2)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
