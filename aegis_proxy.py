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

    

    #Mock GRC Logging: Proof of compliance
    print(f"[GRC LOG]: Request scanned. PII Redacted: {len(results) > 0}")

    #In a real app, this sanitized_text would be sent to the AI model
    return sanitized_text

#TEST CASE
raw_prompt = "Hey GPT, can you help me draft an email to john.doe@company.com regarding credit card 4111-1111-1111-1111?"
print(f"Original: {raw_prompt}")
print(f"Sanitized: {secure_ai_proxy(raw_prompt)}")

