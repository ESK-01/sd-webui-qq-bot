import os

def find_embeddings(path):
    extensions = ['.ckpt', '.pt', '.safetensors']
    embeddings = []
    for filename in os.listdir(path):
        name, ext = os.path.splitext(filename)
        if ext in extensions:
            embeddings.append(name)
    return ' , '.join(embeddings)

# path = r'C:\Users\ikaros\stable-diffusion-webui\models\Lora'
# lora_str = find_lora(path)
# print(lora_str)
