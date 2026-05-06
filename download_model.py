import os
import requests

def download_file(url, local_filename):
    print(f"Downloading {url} to {local_filename}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    print("Download complete.")

if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    url = "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    local_path = "models/llama3.1-8b-instruct.gguf"
    download_file(url, local_path)
