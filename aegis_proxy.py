import os
import json
import logging
from typing import Tuple, Optional
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

# Load environment variables
load_dotenv()

# Configure Structured Logging for SIEM integration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AegisProxy')

class SecureGateway:
    """
    AEGIS Proxy: Encapsulates encryption, PII detection, and anonymization.
    Refactored for performance and UI integration.
    """

    # Configuration: Entities to scrub
    SENSITIVE_ENTITIES = ["SSN", "EMAIL_ADDRESS", "API_KEY", "PHONE_NUMBER", "CREDIT_CARD"]
    def __init__(self, encryption_key: Optional[str] = None):
        # 1. Setup Encryption (Fernet)
        key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY is missing from .env")
        
        try:
            self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception as e:
            raise ValueError(f"CRITICAL: Invalid ENCRYPTION_KEY format: {e}")
        
        # 2. Setup Engines (Loaded ONCE here for performance)
        logger.info("🛡️ Aegis Initializing NLP Engines...")
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # 3. Add Custom API Key Recognizer
        self._register_custom_recognizers()
        logger.info("✅ Aegis Proxy Shield Active.")

    def _register_custom_recognizers(self):
        """Standard NLP misses random API keys; we use regex to catch them."""
        api_key_pattern = Pattern(name="api_key_pattern", regex=r"(sk-[a-zA-Z0-9\-\_]{10,})", score=0.8)
        api_key_recognizer = PatternRecognizer(supported_entity="API_KEY", patterns=[api_key_pattern])
        self.analyzer.registry.add_recognizer(api_key_recognizer)
    
    def process_prompt(self, user_input: str, user_id: str = "Unknown") -> Tuple[str, str]:
        """Main logic: Encrypts raw data and returns a sanitized version."""

        if not user_input:
            return "", ""
        
        try:
            # A. The Shield: Encrypt the RAW Input for Audit Logs
            encrypted_blob = self.cipher.encrypt(user_input.encode()).decode()

            # B. The Scan: Search for PII + Secrets
            results = self.analyzer.analyze(
                text=user_input, 
                entities=self.SENSITIVE_ENTITIES, 
                language='en'
            )

            # C. The Strategy: Anonymize the sensitive data
            anonymized_result = self.anonymizer.anonymize(
                text=user_input, 
                analyzer_results=results
            )

            sanitized_text = anonymized_result.text

            # D. GRC Logging: Send metadata to SIEM
            log_payload = {
                "event": "AI_Prompt_Sanitized",
                "user_id": user_id,
                "risk score": len(results) * 10
            }
            logger.info(json.dumps(log_payload))

            return sanitized_text, encrypted_blob
        
        except Exception as e:
            logger.error(f"Aegis processing error: {e}")
            return "ERROR: Security Gateway Failure.", ""
        
# --- Local Test Case ---
if __name__ == "__main__":
    try:
        gateway = SecureGateway()
        raw_test = "My email is test@example.com and key is sk-proj-12345abcde"
        safe, secret = gateway.process_prompt(raw_test, user_id="DEV_TEST")

        print(f"\n✅ SHIELD Verified")
        print(f"Original (Encrypted): {secret[:20]}...")
        print(f"To LLM (Sanitized): {safe}")
    except Exception as e:
        print(f"❌ Setup Failed: {e}")

