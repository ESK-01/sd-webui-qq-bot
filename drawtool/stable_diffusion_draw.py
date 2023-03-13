import re
import numpy as np
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
import os
import uuid
import datetime
from drawtool.translate import zh_to_en


def save_image(img):
    # 获取当前日期并格式化为'YYYY-MM-DD'字符串
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")

    # 创建保存图像的目录（如果目录不存在）
    save_dir = os.path.join('C:', os.sep, 'Users', 'ikaros', 'code', 'nakuru-project-master', 'data', 'draw_image', today)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # # 生成随机的UUID字符串作为文件名
    # filename = str(uuid.uuid4())

    # 读取图像文件
    # img = Image.open('image.png')

    # 拼接文件路径
    file_path = os.path.join(save_dir,now.strftime("%Y-%m-%d_%H-%M-%S") + '.png')

    # 保存图像文件
    img.save(file_path)
    return file_path


def payload_std(text_str):
    # 使用 replace 方法替换指定字符
    text_str = text_str.replace('#画', '').replace('高', 'height').replace('宽', 'width').replace('模型',"model_sw")
    text_en ,parameter,is_t= zh_to_en(text_str)#翻译中文
    if is_t==1:
        print('翻译结果',text_en)
    # 将字符串按逗号分割成一个列表
    tokens = parameter.split(',')
    # 创建一个字典，用于存储变量名和对应的值
    var_dict = {}
    # 遍历列表中的每个元素
    for token in tokens:
        # 如果元素中包含等号，则将其分割成变量名和值
        if '=' in token:
            var_name, var_value = token.split('=')
            # 将变量名和对应的值存储到字典中
            var_dict[var_name] = int(var_value)
    
    model_sw = var_dict.get('model_sw',99)
    if model_sw ==99:

        payload = json.load(open("modeljson/default.json"))
    else:
        from modeljson.model_config import model_sw_list
        model_list = model_sw_list()
        model_sw = int(np.clip(model_sw,1,len(model_sw_list())))
        base_path = "modeljson/"
        jsonname = model_list[str(model_sw)].replace("3d\\","").replace("25d\\","").replace("2d\\","").replace(".pt","").replace(".ckpt","").replace(".safetensors","")
        model_config_json  = base_path + '/' + jsonname + '.json'
        payload = json.load(open(model_config_json))

        #切换模型后重写default.json 文件
        json.dump(payload, open("modeljson/default.json", 'w'))

    payload.update(var_dict)

    if var_dict.get('model_sw'):
        payload.pop('model_sw')

    text_en =text_en.lower()
    payload['prompt'] = text_en + payload['prompt']#+"<lora:chunmomoLora_v11:1>"

    #参数限制,防止传入恶意参数
    payload['height'] = int(np.clip(payload['height'],256,1280))
    payload['width'] = int(np.clip(payload['width'],256,1280))
    payload["denoising_strength"] = float(np.clip(payload["denoising_strength"],0,1))
    payload['steps'] = int(np.clip(payload['steps'],1,150))
    payload["cfg_scale"] = float(np.clip(payload["cfg_scale"],0.1,100))
    return payload,text_en ,is_t

def ai_draw(qqmessage):
    payload,text_en ,is_t = payload_std(qqmessage)
    url = "http://127.0.0.1:7860"

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()
    j = 0
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image_path = save_image(image)
    return image_path,image , text_en ,is_t