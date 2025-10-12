import requests

# ---------------- CONFIG ----------------
MT_ENDPOINT = "https://canvas.iiit.ac.in/sandboxbeprod/check_model_status_and_infer/67b86729b5cc0eb92316383c"      # e.g., "https://api.anuvaad.bhashini.ai/translate/en-hi"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjhlYTY3ZDZiOTNlM2JlYzkwMWZkOTc3Iiwicm9sZSI6Im1lZ2F0aG9uX3N0dWRlbnQifQ.D_lwUftpnNSFbBs0_9uG4P86Z2p6kMZ9PC1GkqZd8mg"
# ----------------------------------------

def translate_text(text: str):
    headers = {"access-token": ACCESS_TOKEN, "Content-Type": "application/json"}
    payload = {"input_text": text}

    response = requests.post(MT_ENDPOINT, headers=headers, json=payload, verify=False)
    response.raise_for_status()  # Raise error if request failed
    data = response.json()

    if data.get("status") != "success":
        raise RuntimeError(f"Translation failed: {data}")

    return data["data"]["output_text"]


if __name__ == "__main__":
    text = "Hello, how are you?"
    translated = translate_text(text)
    print("Original:", text)
    print("Translated:", translated)
