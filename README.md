# Image-Based Secret Communication System (IBSCS) 

A secure, modern desktop-web application that encapsulates secret data (text messages, audio recordings, or custom files) inside standard PNG images using advanced steganography and cryptography techniques. 

## Key Features
* **AI Cover Image Generation :** Generate beautiful, photorealistic cover images on-the-fly using integrated Hugging Face (Flux.1-schnell) or Pollinations AI models! No need to find your own images.
* **Multi-Payload Support:** Hide raw text strings, generic external files, or direct microphone-recorded voice notes.
* **Dual-Layer Security:** Combines **AES-128 encryption** (via Python's `cryptography` Fernet implementation) with **LSB (Least Significant Bit) Steganography**.
* **Smart Payload Compression:** Integrates `zlib` data compression before the embedding phase to maximize storage capacity within pixel grids.
* **Ephemeral Key Encapsulation:** Implements a passwordless system by generating unique, one-time symmetric keys on-the-fly and packing them securely inside the image itself alongside the encrypted data.
* **Real-time Radar Scanner:** Features a built-in "Secret Checker" module to instantly scan an image matrix and detect if a hidden protocol payload exists.
* **Elegant UI:** Built with a clean, hardware-accelerated dark glassmorphism theme using Streamlit.

---

## Tech Stack
* **Frontend Framework:** Streamlit (Python web-app framework)
* **AI & Machine Learning:** Hugging Face Inference API / Pollinations AI (Text-to-Image models)
* **Steganography Engine:** `stegano` (LSB manipulation library)
* **Cryptographic Layer:** `cryptography` (Fernet symmetric encryption tokens)
* **Compression Pipeline:** Built-in `zlib` binaries

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MuhammadFaisalBinAfzal/image-based-secret-communication-system.git
   cd image-based-secret-communication-system
   ```

2. **Create a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables (for AI generation):**
   Create a `.env` file in the root directory and add your keys (optional, standard cover images are used as fallback):
   ```
   HUGGINGFACE_API_TOKEN=your_token_here
   POLLINATIONS_API_KEY=your_key_here
   ```

5. **Run the App:**
   ```bash
   streamlit run app.py
   ```