#!/usr/bin/env python3
"""Check actual rate limits by testing rapid requests"""

import google.generativeai as genai
import time

key = "AIzaSyC1zDsanc_RvfhTO4hWaV6dZCT5Sof5Gf8"
genai.configure(api_key=key)

# Models to test
models_to_test = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite", 
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",  # For comparison
]

print("=" * 80)
print("Testing Rate Limits (Requests Per Minute)")
print("=" * 80)
print("\nNote: Google Gemini API Free Tier typical limits:")
print("  - gemini-1.5-flash: 15 RPM, 1,500 RPD")
print("  - gemini-2.5-flash: ~2 RPM, 20 RPD")
print("  - Lite models: Higher limits (often 60+ RPM)")
print("\n" + "=" * 80)

for model_name in models_to_test:
    print(f"\n🔍 Testing: {model_name}")
    
    try:
        model = genai.GenerativeModel(model_name)
        
        # Try 10 rapid requests to test RPM
        start_time = time.time()
        success_count = 0
        
        for i in range(10):
            try:
                response = model.generate_content("Hi")
                success_count += 1
                print(".", end="", flush=True)
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    print(f"\n   ❌ Hit rate limit at request {i+1}")
                    break
                else:
                    print(f"\n   ❌ Error: {str(e)[:50]}")
                    break
        
        elapsed = time.time() - start_time
        
        if success_count == 10:
            print(f"\n   ✅ Completed {success_count} requests in {elapsed:.1f}s")
            rpm_estimate = int((success_count / elapsed) * 60)
            print(f"   📊 Estimated RPM: ~{rpm_estimate}+")
        else:
            print(f"\n   ⚠️  Completed {success_count}/10 requests")
            
    except Exception as e:
        print(f"   ❌ Failed to test: {e}")
    
    # Small delay between model tests
    time.sleep(2)

print("\n" + "=" * 80)
print("💡 BEST MODEL: gemini-2.5-flash-lite or gemini-3-flash-preview")
print("   (Highest input tokens + likely highest rate limits)")
print("=" * 80)
