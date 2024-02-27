from io import BytesIO
# from PIL import Image
import base64

import os
from dotenv import load_dotenv
import json
from openai import OpenAI

# Load environment variables
load_dotenv()

class CustomOpenAIModel:
    def __init__(self, name):
        self.name = name
        # print(f"Using a model name of {self.name}")
        config = json.load(open("config.json"))
        # print(f"model is: {config['llms'][self.name].get('slug')}\nendpoint is {config['llms'][self.name].get('endpoint')}")
        self.client = OpenAI(
            api_key="EMPTY", # There is no API key
            base_url=config['llms'][self.name].get('endpoint')
        )
        self.hparams = config['hparams']
        self.hparams.update(config['llms'][self.name].get('hparams') or {})

    def make_request(self, conversation, add_image=None, max_tokens=None):
        config = json.load(open("config.json"))
        conversation = [{"role": "user" if i % 2 == 0 else "assistant", "content": content} for i, content in enumerate(conversation)]
    
        if add_image:
            buffered = BytesIO()
            add_image.convert("RGB").save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            img_str = f"data:image/jpeg;base64,{img_str}"
            
            conversation[0]['content'] = [{"type": "text", "text": conversation[0]['content']},
                                          {
                                            "type": "image_url",
                                            "image_url": {
                                              "url": img_str
                                            }
                                          }
                                          ]
        kwargs = {
            "messages": conversation,
            "max_tokens": max_tokens,
        }
        kwargs.update(self.hparams)
    
        for k,v in list(kwargs.items()):
            if v is None:
                del kwargs[k]

        out = self.client.chat.completions.create(
            model=config['llms'][self.name].get('slug'),
            **kwargs
        )
    
        return out.choices[0].message.content

if __name__ == "__main__":
    import sys
    #q = sys.stdin.read().strip()
    q = "hello there"
    print(q+":", CustomOpenAIModel("Mistral-7B-Instruct-v0.1").make_request([q]))
