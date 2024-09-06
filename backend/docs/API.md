# API

## 模型配置
### 获得tts模型信息
url: /demo/tts_model  
请求：Get  
参数：NA  
返回：
``` json
{
    "models": [
        "TTS_WIZ"
    ],
    "languages": [
        "EN",
        "IN"
    ]
}
```

### 获得同声传译模型信息
url: /demo/tranlate_model  
请求：Get  
参数：NA  
返回：
``` json
{
    "models": [
        "M4T-0830V1"
    ],
    "languages": [
        "EN",
        "IN"
    ]
}
```

## 对话记录
### 获得对话记录
url: /demo/history   
请求：Get  
参数：NA  
返回： 
``` json
[
    {
        "role": "client",
        "data": {
            "text": "",
            "type": "speech",
            "audio_id": "5c4e48b4-7195-457d-abad-12e3709be387"
        }
    },
    {
        "role": "staff",
        "data": {
            "text": "Hello sir, what would you like to eat today?",
            "type": "speech+text",
            "audio_id": "786ecc70-8ecc-4aa2-ac77-10e8fcd8c607"
        }
    }
]
```

### 清空对话记录
url: /demo/history   
请求：Delete  
参数：NA  
返回：
``` json
{
    "status": "ok"
}
```

### 获取audio file by id
url: /demo/audio/\<id>  
请求：Get  
参数：NA  
返回：二进制  


## 同声传译
### 文本翻译
url: /demo/text_translate  
请求：Post  
参数：
``` json
{
    "si_model": "M4T-0830V1",     // 翻译模型名称
    "source_language": "IN",      // 翻译源语种，取值从接口获取
    "target_language": "EN",      // 翻译后语种，取值从接口获取
    "output_type": "speech", // 输出格式，取值：[text | speech | speech+text]
    "use_tts": 1,   // 是否使用TTS生成语音，取值0和1，如果没有该参数就默认为0
    "tts_model": "TTS_WIZ",  // TTS模型名称
    "input": "Bagaimana kabarmu? Saya baik-baik saja."  // 输入文本
}
```
返回：
``` json
{
    "audio_id": "f7321645-05df-4903-88b3-52d47d5642f4"
}
// 若输出格式为text则audio_id为""
```

### 语音翻译
url: /demo/speech_translate  
请求：Post  
参数：
``` form-data
--form 'file=@"xxx"'       // 音频文件或录音文件
--form 'si_model="M4T-0830V1"'  // 翻译模型名称
--form 'source_language="EN"'   // 翻译源语种，取值从接口获取
--form 'target_language="EN"'   // 翻译后语种，取值从接口获取
--form 'output_type="speech"'   // 输出格式，取值：[text | speech | speech+text]
--form 'use_tts="0"'      // 是否使用TTS生成语音，取值0和1，如果没有该参数就默认为0
--form 'tts_model="TTS_WIZ"'    // TTS模型名称
```
返回：
``` json
{
    "audio_id": "f7321645-05df-4903-88b3-52d47d5642f4"
}
// 若输出格式为text则audio_id为""
```

## TTS
### tts文本转语音
url: /demo/tts_generate  
请求：Post  
参数：
``` json
{
    "tts_model": "TTS_WIZ",
    "target_language": "EN",
    "input": "how are you? I am fine."
}
```
返回：
``` json
{
    "audio_id": "61d218f4-44bd-4e30-bc8f-f0db054a54f6"
}
```