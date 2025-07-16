import os
from groq import Groq

# Explicitly load .env from the current directory
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

def test_groq_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    print("GROQ_API_KEY:", api_key)  # For debugging
    if not api_key:
        print("GROQ_API_KEY not found in environment variables.")
        return

    try:
        client = Groq(api_key=api_key)
        prompt = "Say hello world as a JSON object."
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.2,
            top_p=0.9,
            stream=False
        )
        print("Groq API call succeeded!")
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("Groq API call failed.")
        print("Error:", e)

if __name__ == "__main__":
    test_groq_api_key()