import sys
import os

# Ensure backend root is on the path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gemini_service import extract_events_from_email

subject = "Hexaware Technologies - Mock Assessment - Segue Hiring 2027"

body = """Dear Candidate,

Congratulations! We have received your application for our Segue Hiring Process 2027.

As part of the Hiring process, we will be conducting a mandatory Mock Assessment today at 4:50 PM. The purpose of this assessment is to help you verify your system setup and avoid any technical issues during the actual hiring process. The assessment will remain active till tonight and please note that completion of this Mock Assessment is mandatory.

Please find the attached System Requirements PDF for your reference. We kindly request that you to go through all the instructions carefully and make the necessary arrangements in advance to avoid any last-minute issues.

Step 1: Check Your System and Internet
  * Ensure that you have admin access to your laptop/desktop.
  * Use Windows 10 / Windows 11 / Mac only.

Step 2: Disable/Remove (Very Important)
  * Disable antivirus.
  * Turn off Windows Defender and Firewall.

We wish you all the best!

Thank you.

Regards,
Campus Recruitment Team,
Mail: Campusconnect@hexaware.com
"""

print("=== Running Gemini extraction test ===")
print(f"Subject: {subject}")
print("Calling extract_events_from_email()...\n")

result = extract_events_from_email(subject, body)

print("=== Gemini Output ===")
import json
print(json.dumps(result, indent=2))
print(f"\nTotal events extracted: {len(result)}")
