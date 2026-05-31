import zlib
from cryptography.fernet import Fernet

class CryptoEngine:
    """Handles Ephemeral AES encryption and Compression (No files saved, no passwords)."""
    
    def lock_data(self, data_bytes: bytes) -> tuple:
        # 1. Data ko compress karna taake image mein jagah bache
        compressed_data = zlib.compress(data_bytes)
        
        # 2. Ek bilkul nayi aur unique chabi (key) banana
        ephemeral_key = Fernet.generate_key()
        cipher_suite = Fernet(ephemeral_key)
        
        # 3. Data ko lock karna
        encrypted_data = cipher_suite.encrypt(compressed_data)
        
        # Dono cheezein wapas bhejna taake image mein pack ho sakein
        return encrypted_data, ephemeral_key

    def unlock_data(self, encrypted_data: bytes, ephemeral_key: bytes) -> bytes:
        try:
            # 1. Image se nikali hui chabi se lock kholna
            cipher_suite = Fernet(ephemeral_key)
            decrypted_compressed_data = cipher_suite.decrypt(encrypted_data)
            
            # 2. Data ko wapas decompress karna
            original_data = zlib.decompress(decrypted_compressed_data)
            return original_data
        except Exception:
            raise ValueError("DECRYPTION_FAILED")