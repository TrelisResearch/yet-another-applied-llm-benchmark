import os
from dotenv import load_dotenv
import json
from openai import OpenAI

# Load environment variables
load_dotenv()

# Retrieve the env variables
model = os.getenv('MODEL')
api_endpoint = os.getenv('API_ENDPOINT')

openai_api_base = api_endpoint + '/v1'

class CustomOpenAIModel:
    def __init__(self, name):
        config = json.load(open("config.json"))
        self.client = OpenAI(
            api_key="EMPTY", # There is no API key
            base_url=openai_api_base,
        )
        self.name = name
        self.hparams = config['hparams']
        self.hparams.update(config['llms']['custom_openai'].get('hparams') or {})

    def make_request(self, conversation, add_image=None, max_tokens=None):
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
            model=model,
            **kwargs
        )
    
        return out.choices[0].message.content

if __name__ == "__main__":
    import sys
    #q = sys.stdin.read().strip()
    q = "hello there"
    print(q+":", OpenAIModel("gpt-3.5-turbo").make_request([q]))
