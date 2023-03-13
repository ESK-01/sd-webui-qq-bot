import re
import requests
import random
import json
from hashlib import md5


from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

# test_str = 'masterpiece, 动画风格,女孩, ((anime screencap)),1girl,vampire <lora:nanakusa_nazuna_offset:1> 参数{高=512,宽=512}'

def ChToEn(text_str):
    # 定义中英文符号映射字典
    symbol_dict = {
        '，': ',',
        '。': '.',
        '；': ';',
        '：': ':',
        '？': '?',
        '！': '!',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '（': '(',
        '）': ')',
        '【': '[',
        '】': ']',
        '《': '<',
        '》': '>',
        '、': '/',
        '—': '-'
    }
    # 使用正则表达式检测中文符号
    pattern = '[，。；：？！“”‘’（）【】《》、—]'
    # 使用 sub 方法替换中文符号为英文符号
    english_str = re.sub(pattern, lambda x: symbol_dict[x.group()], text_str)
    return english_str

# 百度翻译函数入口
def baidu_translate_api(query):
    appid = '填入你自己的'
    appkey = '填入你自己的'
    from_lang = 'zh'
    to_lang =  'en'
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path
    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    en_text = ''
    for i in result["trans_result"]:
        en_text += i['dst']
    
    # 一些合理的翻译替换,大概吧
    en_text = en_text.replace("genie","elf")

    return en_text
# 腾讯翻译函数入口
def tencent_translate_api(query):
    try:
        cred = credential.Credential("填入你自己的", "填入你自己的")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)
        req = models.TextTranslateRequest()
        params = {
            "SourceText": query,
            "Source": "zh",
            "Target": "en",
            "ProjectId": 0,
        }
        req.from_json_string(json.dumps(params))
        resp = client.TextTranslate(req)
        en_str = str(resp.TargetText)

        #一些合理的翻译替换,大概吧
        en_str = en_str.replace("genie","elf")

        if en_str[-1]=='.':
            en_str = en_str[:-1]
        return en_str
    except TencentCloudSDKException as err:
        print(err)
        return "tencent translation error"


def zh_to_en(text):
    text = ChToEn(text)
    # 提取参数
    match = re.search(r'参数\{(.+?)\}', text)
    parameter = match.group(1) if match else ''
    msg_str = text.replace(f'参数{{{parameter}}}', '')

    # 分离中英文
    zh_msg_str = ''
    en_msg_str = ''
    prev_str = ''
    is_lora=''
    for char in msg_str:
        if char=="<" or is_lora=="<":
            if char=="<":
                is_lora = char

            en_msg_str += char
            if char==">":
                is_lora = char
            continue

        if '\u4e00' <= char <= '\u9fa5':
                zh_msg_str = zh_msg_str+char
                prev_str = char
        elif '\u4e00' <= prev_str <= '\u9fa5' and (char==',' or char==' '):
            zh_msg_str = zh_msg_str+','
            continue
        else:
            en_msg_str += char
            prev_str = char

    # 翻译
    is_translate = 0
    t_msg_str = ''
    if len(zh_msg_str)>=1:
        print('原文:',zh_msg_str)
        t_msg_str = tencent_translate_api(zh_msg_str)
        is_translate = 1 
    msg_str = en_msg_str + ',' + t_msg_str 
    return msg_str,parameter,is_translate



