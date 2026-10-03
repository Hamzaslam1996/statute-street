"""Checks that both keys work. Run: python test_keys.py"""
import os, requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

print("1) Testing Claude key...")
try:
    msg = Anthropic().messages.create(
        model="claude-sonnet-5-5", max_tokens=20,
        messages=[{"role": "user", "content": "Reply with just: OK"}])
    print("   Claude says:", msg.content[0].text)
except Exception as e:
    print("   Claude FAILED:", e)

print("2) Testing Bright Data key...")
try:
    r = requests.post(
        "https://api.brightdata.com/request",
        headers={"Authorization": f"Bearer {os.environ['BRIGHTDATA_API_TOKEN']}",
                 "Content-Type": "application/json"},
        json={"zone": os.environ["BRIGHTDATA_ZONE"],
              "url": "https://geo.brdtest.com/welcome.txt?product=unlocker&method=api",
              "format": "raw"},
        timeout=90)
    print("   Bright Data status:", r.status_code, "|", r.text[:120].strip())
except Exception as e:
    print("   Bright Data FAILED:", e)
