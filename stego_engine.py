from stegano import lsb
import base64

class StegoEngine:
    """Handles hiding and extracting data + key within Image LSBs."""
    
    # Radar detection ke liye secret tag
    MAGIC_HEADER = "STEGOSHIELD_V2"

    def hide_payload(self, image_path: str, encrypted_bytes: bytes, key_bytes: bytes, output_path: str):
        msg_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
        key_b64 = base64.b64encode(key_bytes).decode('utf-8')
        
        # Package Banaya: HEADER ||| CHABI ||| ENCRYPTED_DATA
        payload = f"{self.MAGIC_HEADER}|||{key_b64}|||{msg_b64}"
        
        try:
            secret_image = lsb.hide(image_path, payload)
            secret_image.save(output_path)
            return True
        except Exception as e:
            raise ValueError("IMAGE_TOO_SMALL")

    def detect_payload(self, image_path: str) -> bool:
        """Radar: Check karta hai ke image mein data hai ya nahi."""
        try:
            hidden_text = lsb.reveal(image_path)
            if hidden_text and hidden_text.startswith(self.MAGIC_HEADER):
                return True
            return False
        except:
            return False

    def extract_payload(self, image_path: str) -> tuple:
        """Image se Chabi aur Data dono nikal kar deta hai."""
        try:
            hidden_text = lsb.reveal(image_path)
            if not hidden_text or not hidden_text.startswith(self.MAGIC_HEADER):
                return None, None
                
            parts = hidden_text.split("|||")
            if len(parts) != 3:
                return None, None
                
            key_bytes = base64.b64decode(parts[1])
            msg_bytes = base64.b64decode(parts[2])
            return msg_bytes, key_bytes
        except Exception:
            return None, None