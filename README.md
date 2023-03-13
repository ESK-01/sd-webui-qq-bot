使用方法:
1.stable-diffusion-webui/webui-user.bat 
    修改:
    
    set COMMANDLINE_ARGS=--api

2.修改这个函数:from diffusers.pipelines.stable_diffusion.safety_checker import StableDiffusionSafetyChecker

                adjustment = -0.020 #这里修改,不让过杀很高,值越小,标准越宽松

            for concept_idx in range(len(special_cos_dist[0])):
                concept_cos = special_cos_dist[i][concept_idx]
                concept_threshold = self.special_care_embeds_weights[concept_idx].item()
                result_img["special_scores"][concept_idx] = round(concept_cos - concept_threshold + adjustment, 3)
                if result_img["special_scores"][concept_idx] > 0:
                    result_img["special_care"].append({concept_idx, result_img["special_scores"][concept_idx]})
                    adjustment = -0.011 #这里修改,不让过杀很高,值越小,标准越宽松

3.modeljson\model_config.py

    填写自己供给群使用的模型的名字
    创建模型对应的json文件,用来存储模型的默认设置.
    modeljson\default.json,复制一个模型的内容就可以了.qq使用命令切换模型时内容会更改

4.启动 cmd运行 .\go-cqhttp.exe
    扫码或者其他,登录自己的qq

5.运行 main.py 程序
