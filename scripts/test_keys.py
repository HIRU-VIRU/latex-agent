#!/usr/bin/env python3
"""Test Gemini API keys and check rate limits"""

import google.generativeai as genai

keys = [
    "AIzaSyAVORcu0lByRE9H-RSL3aDFd-HTtzcsea4",
    "AIzaSyAwAAxhONCZUtT709MxptnB2gDy-1M5YTg",
    "AIzaSyC1zDsanc_RvfhTO4hWaV6dZCT5Sof5Gf8"
]

models = [
    "gemini-1.5-flash",      # 1500 req/day free tier
    "gemini-2.0-flash-lite", # Higher limit
    "gemini-2.5-flash"       # 20 req/day (EXHAUSTED)
]

print("=" * 60)
print("Testing Gemini API Keys & Models")
print("=" * 60)

for i, key in enumerate(keys, 1):
    print(f"\n🔑 Key {i}: {key[:25]}...")
    genai.configure(api_key=key)
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hi")
            print(f"  ✅ {model_name:25} - Working!")
        except Exception as e:
            error = str(e)
            if "429" in error or "quota" in error.lower():
                print(f"  ❌ {model_name:25} - QUOTA EXCEEDED")
            elif "404" in error:
                print(f"  ⚠️  {model_name:25} - Model not available")
            else:
                print(f"  ❌ {model_name:25} - Error: {error[:50]}")

print("\n" + "=" * 60)
print("✅ RECOMMENDATION: Use gemini-1.5-flash (1500 req/day)")
print("=" * 60)
