import os

def find_lora(path):
    extensions = ['.ckpt', '.pt', '.safetensors']
    lora = []
    for filename in os.listdir(path):
        name, ext = os.path.splitext(filename)
        if ext in extensions:
            lora.append(name)
    return '\n'.join(lora)

# path = r'C:\Users\ikaros\stable-diffusion-webui\models\Lora'
# lora_str = find_lora(path)
# print(lora_str)
