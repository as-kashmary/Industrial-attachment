# 1) Download the multilingual-e5 embedding model via SentenceTransformer
from sentence_transformers import SentenceTransformer

embed_model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
embed_model.save("models/multilingual-e5-large-instruct")

# 2) Download the Llama-3-3B GGUF file via the HF Hub downloader
from huggingface_hub import hf_hub_download

# Adjust repo_id/filename if needed
gguf_path = hf_hub_download(
    repo_id="Aspen77/llama-3-3b-instruct-extract-pii-Q4_K_M-GGUF",
    filename="llama-3-3b-instruct-extract-pii-q4_k_m.gguf",
    cache_dir="models"
)
print("Saved GGUF model to:", gguf_path)