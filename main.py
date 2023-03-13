from nakuru import (
    CQHTTP,
    GroupMessage,
    Notify,
    GroupMessageRecall,
    FriendRequest
)
from nakuru.entities.components import Plain, Image
import pdb 
from drawtool.stable_diffusion_draw import ai_draw
from drawtool.nsfw_detection import predict_image
from drawtool.lora_search import find_lora
from drawtool.embeddings_search import find_embeddings
import base64
from PIL import Image as im
import traceback

global pre_payload 
pre_payload = None
app = CQHTTP(
    host="127.0.0.1",
    port=5700,
    http_port=8000,
    token="TOKEN" # 可选，如果配置了 Access-Token
)

@app.receiver("GroupMessage")
async def _(app: CQHTTP, source: GroupMessage):
    # 通过纯 CQ 码处理
    if source.raw_message == "戳":
        await app.sendGroupMessage(source.group_id, f"[CQ:poke,qq={source.user_id}]")
    # 通过消息链处理
    chain = source.message
    type = source.type
    self_id = source.self_id
    # self_tiny_id = source.self_tiny_id
    sub_type = source.sub_type
    message_id = source.message_id
    # guild_id = source.guild_id
    # channel_id = source.channel_id
    user_id = source.user_id#发言者qq号
    message = source.message
    sender = source.sender
    raw_message = source.raw_message
    group_id = source.group_id
    # print(raw_message)

    # pdb.set_trace()
    # if isinstance(chain[0], Plain):
    #     if chain[0].text == "看":

    #         await app.sendGroupMessage(source.group_id, [
    #             Plain(text="看"),
    #             Image.fromFileSystem("D:/data/1.png")
    #         ])

    # if isinstance(chain[0], Plain):
    #     # pdb.set_trace()
    try:


        if '#画' in raw_message :
            image_path,ai_img,text_en ,is_translate= ai_draw(raw_message)
            
            x_checked_image, has_nsfw_concept = predict_image(ai_img.copy())
            # x_checked_image = has_nsfw_concept = 'True'#屏蔽nsfw检测

            print('has_nsfw_concept:',has_nsfw_concept)
            if str(has_nsfw_concept[0])=='True':
                message_back = "画好了但是NSFW审核不通过"+str(sender.nickname)+' ' + raw_message[:20]
                await app.sendGroupMessage(source.group_id,message_back )
            else:
                # pdb.set_trace()
                if is_translate==0:
                    message_back = "画好了"+'@'+str(sender.nickname)+' ' + raw_message[:20]
                    await app.sendGroupMessage(source.group_id, [
                    Plain(text=message_back),
                    Image.fromFileSystem(image_path)])
                else:
                    message_back = '@'+str(sender.nickname) + "画好了,检测到中文尝试翻译为:" + text_en
                    await app.sendGroupMessage(source.group_id, [
                    Plain(text=message_back),
                    Image.fromFileSystem(image_path)])

        if '#help' in raw_message:

            message_back = "当前可用命令:\n  #画 \n  #查看lora \n  #lora使用方法  \n  #模型列表  \n  #查看emb"
            await app.sendGroupMessage(source.group_id,message_back )


        if '#查看lora' in raw_message:
            lora_path = r'C:\Users\ikaros\stable-diffusion-webui\models\Lora'
            lora_str = find_lora(lora_path)
            message_back = "当前可用lora:"+lora_str
            await app.sendGroupMessage(source.group_id,message_back )

        if '#查看emb' in raw_message:
            emb_path = r'C:\Users\ikaros\stable-diffusion-webui\embeddings'
            emb_str = find_embeddings(emb_path)
            message_back = "emb使用方法:<emb名字>,保护中文名字必须使用<>避免翻译\n当前可用emb:\n"+emb_str
            await app.sendGroupMessage(source.group_id,message_back )

        if '#help' in raw_message:

            message_back = "当前可用命令:\n  #画 \n  #查看lora \n  #lora使用方法  \n  #模型列表"
            await app.sendGroupMessage(source.group_id,message_back )

        if '#lora使用方法' in raw_message:

            message_back = "<lora:lora名字:权重>\n 例子:\n     <lora:Lora_ningningxiunu:1>"
            await app.sendGroupMessage(source.group_id,message_back )

        if '#模型列表' in raw_message:

            message_back = " 编号:         模型名字\n1 : chilloutmix_NiCkpt#3d写实风\n 2 :  GuoFeng3        ,#国风2.5d\n 使用方法例子提示词后面增加:  参数{高=768,宽=512,模型=1},\n\n不确认下一张图片是否会被更改,建议每次都加上"
            await app.sendGroupMessage(source.group_id,message_back )

    except Exception as e:
        traceback.print_exc()
        await app.sendGroupMessage(source.group_id,"出错啦!,问题已经记录,请等待修复" )#假的
    #         ai_draw
    #     if chain[0].text == "看":
    #         image_path = 'D:\data\1.png'
    #         await app.sendGroupMessage(source.group_id, [
    #             Plain(text="看"),
    #             Image.fromFileSystem("D:/data/1.png")
    #         ])

# @app.receiver("GroupMessageRecall")
# async def _(app: CQHTTP, source: GroupMessageRecall):
#     await app.sendGroupMessage(source.group_id, "你撤回了一条消息")

# @app.receiver("Notify")
# async def _(app: CQHTTP, source: Notify):
#     if source.sub_type == "poke" and source.target_id == 114514:
#         await app.sendGroupMessage(source.group_id, "不许戳")

@app.receiver("FriendRequest")
async def _(app: CQHTTP, source: FriendRequest):
    await app.setFriendRequest(source.flag, True)

app.run()