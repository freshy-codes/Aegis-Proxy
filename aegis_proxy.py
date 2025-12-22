import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Load environment variables
load_dotenv()

# Initialize the Shield
KEY = os.getenv("ENCRYPTION_KEY").encode()
cipher = Fernet(KEY)

# The Engine: Processing the AI Logic
def secure_ai_proxy(user_input):
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    #1. The Shield: Encrypt the RAW Input
    encrypted_original = cipher.encrypt(user_input.encode())

    #2. The Shield: Scanning for PII (SSNs, Emails, API Keys)
    results = analyzer.analyze(text=user_input, entities=["SSN", "EMAIL_ADDRESS", "API_KEY", "PHONE_NUMBER", "CREDIT_CARD"], language='en')

    #3. The Strategy: Anonymize the sensitive data
    anonymized_result = anonymizer.anonymize(
        text=user_input, 
        analyzer_results=results
        )
    
    sanitized_text = anonymized_result.text

    #4. GRC Logging: Proof of compliance
    print(f"[GRC LOG]: Scan Complete.")
    print(f"[GRC LOG]: Encrypted Evidence: {encrypted_original[:20]}...") # Show just a bit

    return sanitized_text, encrypted_original

#TEST CASE
raw_prompt = "My email is john.doe@company.com and my card is 4111-1111-1111-1111"
sanitized, encrypted = secure_ai_proxy(raw_prompt)

print(f"\n✅ SHIELD ACTIVE")
print(f"Original (Invisible to AI): {raw_prompt}")
print(f"To LLM (Safe): {sanitized}")
print(f"Stored in Audit Log (Encrypted): {encrypted}")

