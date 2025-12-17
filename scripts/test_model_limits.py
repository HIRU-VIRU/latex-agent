#!/usr/bin/env python3
"""Test Gemini models to find one with highest request limits"""

import google.generativeai as genai

key = "AIzaSyC1zDsanc_RvfhTO4hWaV6dZCT5Sof5Gf8"
genai.configure(api_key=key)

models_to_test = [
    "gemma-3-1b-it",
    "gemma-3-4b-it",
    "gemma-3-12b-it",
    "gemma-3-27b-it",
    "gemma-3n-e4b-it",
    "gemma-3n-e2b-it",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash-lite-preview-09-2025",
    "gemini-3-flash-preview",
    "gemini-robotics-er-1.5-preview"
]

print("=" * 70)
print("Testing Models for Availability & Rate Limits")
print("=" * 70)

working_models = []

for model_name in models_to_test:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hi")
        print(f"✅ {model_name:45} - WORKING")
        working_models.append(model_name)
    except Exception as e:
        error = str(e)
        if "429" in error or "quota" in error.lower() or "exceeded" in error.lower():
            print(f"❌ {model_name:45} - QUOTA EXCEEDED")
        elif "404" in error or "not found" in error.lower():
            print(f"⚠️  {model_name:45} - NOT FOUND")
        elif "permission" in error.lower():
            print(f"⚠️  {model_name:45} - NO PERMISSION")
        else:
            print(f"❌ {model_name:45} - ERROR: {error[:30]}")

print("\n" + "=" * 70)
if working_models:
    print(f"✅ Working Models: {len(working_models)}")
    for m in working_models:
        print(f"   - {m}")
    print("\n💡 RECOMMENDATION: Try these models in order of preference")
else:
    print("❌ No working models found. All quotas may be exhausted.")
print("=" * 70)
