import streamlit as st
import os
from crypto_engine import CryptoEngine
from stego_engine import StegoEngine

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="IBSCS Workspace", page_icon="🔐", layout="centered")
# --- CUSTOM CSS (Soft, Friendly Dark Theme) ---
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .glass-panel {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .main-title { font-size: 2.5rem; font-weight: 800; color: #f8fafc; text-align: center; margin-bottom: 0px;}
    .sub-title { font-size: 1.1rem; color: #94a3b8; text-align: center; margin-bottom: 30px;}
    .stButton>button {
        background-color: transparent; 
        border: 2px solid #38bdf8; 
        color: #38bdf8;
        border-radius: 12px; 
        transition: all 0.3s ease; 
        width: 100%;
        font-weight: bold;
        padding: 10px;
    }
    .stButton>button:hover { 
        background-color: #38bdf8; 
        color: #0f172a; 
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); 
    }
    .stDownloadButton>button { 
        background-color: #38bdf8; 
        color: #0f172a; 
        font-weight: bold; 
        border-radius: 12px;
    }
    .step-header { color: #e2e8f0; font-size: 1.2rem; font-weight: 600; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE ENGINES ---
if 'crypto' not in st.session_state: st.session_state.crypto = CryptoEngine()
if 'stego' not in st.session_state: st.session_state.stego = StegoEngine()
crypto, stego = st.session_state.crypto, st.session_state.stego

# --- HEADER SECTION ---
st.markdown("<div class='main-title'>🔐 IBSCS</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Image-Based Secret Communication System <br> <i>Securely encapsulate text, audio, and files within image.</i></div>", unsafe_allow_html=True)
# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["🔒 Lock a Secret", "🔓 Open a Secret", "📡 Secret Checker"])

# ==========================================
# TAB 1: LOCK A SECRET (HIDE DATA)
# ==========================================
with tab1:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='step-header'>Step 1: Upload Photo</div>", unsafe_allow_html=True)
    cover_image = st.file_uploader("Choose a nice cover photo (.PNG)", type=["png"], key="send_img")
    
    st.markdown("<div class='step-header' style='margin-top: 20px;'>Step 2: Hide Message</div>", unsafe_allow_html=True)
    payload_type = st.radio("What do you want to hide inside the photo?", ["Type a Message", "Upload a File", "Record a Voice Note 🎙️"])
    
    data_bytes = None
    
    if payload_type == "Type a Message":
        secret_data = st.text_area("Type your secret message here:")
        if secret_data:
            data_bytes = f"TEXT::{secret_data}".encode('utf-8')
            
    elif payload_type == "Upload a File":
        secret_file = st.file_uploader("Choose a file to hide (Keep it small)")
        if secret_file:
            data_bytes = f"FILE::{secret_file.name}::".encode('utf-8') + secret_file.getvalue()
            
    elif payload_type == "Record a Voice Note 🎙️":
        st.info("💡 **Tip:** Keep it short! Photos only have space for about 5-10 seconds of audio.")
        audio_file = st.audio_input("Tap to record your secret voice message")
        if audio_file:
            data_bytes = b"AUDIO::" + audio_file.getvalue()
    
    if st.button("Hide My Secret 🔒"):
        if cover_image and data_bytes:
            with open("temp_cover.png", "wb") as f: f.write(cover_image.getbuffer())
            
            try:
                with st.spinner("Doing some magic... 🪄"):
                    enc_data, ephemeral_key = crypto.lock_data(data_bytes)
                    stego.hide_payload("temp_cover.png", enc_data, ephemeral_key, "secured_image.png")
                
                st.success("Yay! 🎉 Your secret is safely locked inside the photo.")
                with open("secured_image.png", "rb") as f:
                    st.download_button("⬇️ Download Your Secret Photo", data=f, file_name="my_secret_photo.png", mime="image/png", use_container_width=True)
            except ValueError as e:
                st.error("Oops! ❌ The secret is too big for this photo. Try a larger photo or a shorter recording!")
        else:
            st.warning("⚠️ Please provide both a photo and a secret to hide.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: OPEN A SECRET (EXTRACT DATA)
# ==========================================
with tab2:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='step-header'>Step 1: Upload Photo</div>", unsafe_allow_html=True)
    secured_img_upload = st.file_uploader("Upload the photo containing the secret (.PNG)", type=["png"], key="recv_img")
    
    st.markdown("<div class='step-header' style='margin-top: 20px;'>Step 2: Read Message</div>", unsafe_allow_html=True)
    if st.button("Show Hidden Message 🔓"):
        if secured_img_upload:
            with open("temp_sec.png", "wb") as f: f.write(secured_img_upload.getbuffer())
            
            with st.spinner("Looking for secrets... 🔍"):
                enc_data, ephemeral_key = stego.extract_payload("temp_sec.png")
            
            if enc_data and ephemeral_key:
                try:
                    with st.spinner("Unlocking... 🔓"):
                        raw_data = crypto.unlock_data(enc_data, ephemeral_key)
                    
                    st.success("Secret unlocked successfully! ✨")
                    
                    if raw_data.startswith(b"TEXT::"):
                        text_msg = raw_data[6:].decode('utf-8')
                        st.info(f"**Your Hidden Message:**\n\n{text_msg}")
                        
                    elif raw_data.startswith(b"FILE::"):
                        parts = raw_data.split(b"::", 2)
                        file_name = parts[1].decode('utf-8')
                        file_content = parts[2]
                        st.info(f"📁 **Hidden File Found:** {file_name}")
                        st.download_button(f"⬇️ Download {file_name}", data=file_content, file_name=file_name, use_container_width=True)
                        
                    elif raw_data.startswith(b"AUDIO::"):
                        audio_content = raw_data[7:]
                        st.info("🎙️ **Hidden Voice Note Found:**")
                        st.audio(audio_content)
                        
                except Exception as e:
                    st.error("Oops! ❌ Could not read the secret. The photo might be damaged.")
            else:
                st.error("❌ No secrets found in this photo. It's just a normal picture!")
        else:
            st.warning("⚠️ Please upload a photo first.")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: SECRET CHECKER (DETECTION)
# ==========================================
with tab3:
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='step-header'>Secret Checker</div>", unsafe_allow_html=True)
    st.write("Not sure if a photo has a hidden message? Upload it here to do a quick check!")
    
    scan_img = st.file_uploader("Upload photo to check (.PNG)", type=["png"], key="scan_img")
    if scan_img:
        if st.button("Check Photo 🔍"):
            with open("temp_scan.png", "wb") as f: f.write(scan_img.getbuffer())
            with st.spinner("Checking..."):
                has_data = stego.detect_payload("temp_scan.png")
            
            if has_data:
                st.error("😲 **Wow!** There is definitely a secret message hiding inside this photo!")
            else:
                st.success("✅ **All Clear!** This looks like a completely normal photo.")
    st.markdown("</div>", unsafe_allow_html=True)
    
# --- FOOTER (How it works) ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🤔 Technical Architecture (How the Engine Works)"):
    st.write("Behind this clean gallery interface runs a sophisticated [advanced and complex] Steganography and Cryptography engine. Here is the technical workflow of how documents and audio are encapsulated [safely packed and hidden] into image matrices [the digital grid of pixels]:")
    
    st.markdown("🎙️ **1. Data Serialization [Converting data into a storable format] & Byte Conversion:**")
    st.write("Whether it's a recorded voice note, a text message, or a document, the input is immediately converted into a raw byte array [a basic sequence of digital 0s and 1s]. We prepend [add to the very beginning] a specific protocol header [an identifier tag like `AUDIO::` or `FILE::`] to this binary data. This metadata [extra information that describes the main data] allows the receiver engine to reconstruct [rebuild] the correct file format upon extraction.")
    
    st.markdown("🔒 **2. Ephemeral [Temporary, one-time use] Encryption & Compression:**")
    st.write("Before embedding, the byte array is compressed using `zlib` to optimize storage. Simultaneously, the Crypto Engine generates a unique, one-time symmetric key [a single key used for both locking and unlocking] (AES-128 via Fernet). The compressed bytes are then encrypted into ciphertext [scrambled, unreadable data]. Without this ephemeral key, the hidden payload [the actual secret file or message] is completely inaccessible.")
    
    st.markdown("🖼️ **3. LSB (Least Significant Bit) [The last and least important bit of data] Steganography:**")
    st.write("A digital image consists of pixels, where each pixel's color is defined by RGB byte values (0-255). The Stego Engine converts the encrypted ciphertext and the key into binary [0s and 1s]. It then replaces the Least Significant Bit (the 8th bit) of the image's RGB bytes with the payload's bits. Since the LSB has minimal impact on the actual color, the visual alteration is mathematically imperceptible [impossible for the human eye to notice].")
    
    st.markdown("🗝️ **4. Self-Contained Key Encapsulation [Packing the Key inside the Image]:**")
    st.write("To achieve a seamless, password-less experience, the ephemeral [temporary] AES key is encapsulated [securely enclosed] directly into the image's LSB alongside the encrypted payload. During extraction, the system parses [reads and analyzes] the hidden bits, retrieves the key, decrypts the ciphertext, reads the header, and automatically renders [displays or loads] the native audio player or file downloader.")