#!/usr/bin/env python3
"""Check rate limits for available models"""

import google.generativeai as genai

key = "AIzaSyC1zDsanc_RvfhTO4hWaV6dZCT5Sof5Gf8"
genai.configure(api_key=key)

# Focus on the best models
priority_models = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemma-3-27b-it",
    "gemma-3-12b-it"
]

print("=" * 80)
print("Model Limits & Capabilities")
print("=" * 80)

for model_name in priority_models:
    try:
        model_info = genai.get_model(f"models/{model_name}")
        print(f"\n📊 {model_name}")
        print(f"   Input Token Limit:  {model_info.input_token_limit:,}")
        print(f"   Output Token Limit: {model_info.output_token_limit:,}")
        
        # Try to get rate limit info if available
        if hasattr(model_info, 'rate_limit'):
            print(f"   Rate Limits: {model_info.rate_limit}")
            
    except Exception as e:
        print(f"\n❌ {model_name}: Could not get info - {e}")

print("\n" + "=" * 80)
print("💡 RECOMMENDATION:")
print("   - gemini-3-flash-preview (latest, likely highest limits)")
print("   - gemini-2.5-flash-lite (stable, good performance)")
print("=" * 80)
