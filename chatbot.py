import requests
import os
from dotenv import load_dotenv
load_dotenv()

ACCESS_TOKEN = os.getenv('META_WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.getenv('META_WHATSAPP_PHONE_ID')
TEST_USER_NUMBER = os.getenv('TEST_USER_PHONE')  # Sandbox/test number

def send_whatsapp_alert(instance_name, latitude, longitude, to_number=None):
    """
    Send a WhatsApp alert via Meta Cloud API.
    - to_number: phone number in E.164 format (e.g., '15551234567').
                 If None, uses the TEST_USER_NUMBER for testing.
    """
    # Debug: Check if environment variables are loaded
    print(f"[DEBUG] ACCESS_TOKEN: {'Set' if ACCESS_TOKEN else 'Not set'}")
    print(f"[DEBUG] PHONE_NUMBER_ID: {'Set' if PHONE_NUMBER_ID else 'Not set'}")
    print(f"[DEBUG] TEST_USER_NUMBER: {'Set' if TEST_USER_NUMBER else 'Not set'}")
    
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("[SYSTEM] WhatsApp API credentials not configured properly")
        return
    
    if to_number is None:
        to_number = TEST_USER_NUMBER
    
    if not to_number:
        print("[SYSTEM] No phone number configured for WhatsApp alert")
        return

    # Use v18.0 instead of v22.0 (more stable version)
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": f"🚨 WILDFIRE ALERT 🚨\nLocation: {latitude}, {longitude}\nSource: Camera {instance_name}\nEvacuate immediately. Stay safe."
        }
    }
    
    print(f"[DEBUG] Sending WhatsApp alert to {to_number}")
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] Payload: {payload}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response text: {response.text}")
        
        if response.status_code == 200:
            print(f"[SYSTEM] WhatsApp alert sent for {instance_name} to {to_number}")
        else:
            print(f"[SYSTEM] Failed to send alert: {response.text}")
    except Exception as e:
        print(f"[SYSTEM] Exception sending WhatsApp alert: {e}")
