# Image-Based Secret Communication System (IBSCS) 🔐🖼️

A secure, modern desktop-web application that encapsulates secret data (text messages, audio recordings, or custom files) inside standard PNG images using advanced steganography and cryptography techniques.

## 🚀 Key Features
* **Multi-Payload Support:** Hide raw text strings, generic external files, or direct microphone-recorded voice notes.
* **Dual-Layer Security:** Combines **AES-128 encryption** (via Python's `cryptography` Fernet implementation) with **LSB (Least Significant Bit) Steganography**.
* **Smart Payload Compression:** Integrates `zlib` data compression before the embedding phase to maximize the storage capacity within pixel grids.
* **Ephemeral Key Encapsulation:** Implements a passwordless system by generating unique, one-time symmetric keys on-the-fly and packing them securely inside the image itself alongside the encrypted data.
* **Real-time Radar Scanner:** Features an built-in "Secret Checker" module to instantly scan an image matrix and detect if a hidden protocol payload exists.
* **Elegant UI:** Built with a clean, hardware-accelerated dark glassmorphism theme using Streamlit.

---

## 🛠️ Tech Stack
* **Frontend Framework:** Streamlit (Python web-app framework)
* **Steganography Engine:** `stegano` (LSB manipulation library)
* **Cryptographic Layer:** `cryptography` (Fernet symmetric encryption tokens)
* **Compression Pipeline:** Built-in `zlib` binaries

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/MuhammadFaisalBinAfzal/image-based-secret-communication-system.git](https://github.com/MuhammadFaisalBinAfzal/image-based-secret-communication-system.git)
   cd image-based-secret-communication-system