## Copyright (C) 2024, Nicholas Carlini <nicholas@carlini.com>.
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO
import os
import base64
import requests
import json
import pickle
import time
import argparse

# Update imports with CustomOpenAIModel
from llms.runpod_model import CustomOpenAIModel
from llms.openai_model import OpenAIModel
from llms.anthropic_model import AnthropicModel
from llms.mistral_model import MistralModel
from llms.vertexai_model import VertexAIModel
from llms.cohere_model import CohereModel
from llms.moonshot_model import MoonshotAIModel

class LLM:
    def __init__(self, name="gpt-3.5-turbo", use_cache=True, override_hparams={}):
        self.name = name
        if 'gpt' in name:
            self.model = OpenAIModel(name)
        elif 'Mistral-7B-Instruct-v0.1' in name:
            # print("Selecting the Mistral-7B-Instruct-v0.1 custom model")
            self.model = CustomOpenAIModel(name)
        elif 'Mistral-7B-v0.1-chat-ORPO' in name:
            self.model = CustomOpenAIModel(name)
        elif 'Mistral-7B-v0.1-chat-SFT' in name:
            self.model = CustomOpenAIModel(name)
        elif 'TinyLlama-chat-ORPO' in name:
            self.model = CustomOpenAIModel(name)
        elif 'TinyLlama-chat-ORPO-beta0.2' in name:
            self.model = CustomOpenAIModel(name)
        elif 'TinyLlama-chat-SFT' in name:
            self.model = CustomOpenAIModel(name)
        elif 'openchat_3.5' in name:
            self.model = CustomOpenAIModel(name)
        elif 'Mixtral-8x7B-Instruct-v0.1' in name:
            self.model = CustomOpenAIModel(name)
        elif 'mixtral-instruct-awq' in name:
            self.model = CustomOpenAIModel(name)
        elif 'gemma-7b' in name:
            self.model = CustomOpenAIModel(name)
        elif 'Qwen1.5-7B-Chat' in name:
            self.model = CustomOpenAIModel(name)
        elif 'Qwen1.5-7B-Chat-AWQ' in name:
            self.model = CustomOpenAIModel(name)
        elif 'Qwen1.5-72B-Chat' in name:
            self.model = CustomOpenAIModel(name)
        # elif 'llama' in name:
        #     self.model = LLAMAModel(name)
        elif 'mistral' in name:
            # print(f"Selecting the {name} custom model")
            self.model = MistralModel(name)
        elif 'gemini' in name or 'bison' in name:
            self.model = VertexAIModel(name)
        elif 'claude' in name:
            self.model = AnthropicModel(name)
        elif 'moonshot' in name:
            self.model = MoonshotAIModel(name)            
        elif 'command' in name:
            self.model = CohereModel(name)
        else:
            raise ValueError(f"Unsupported model name: {name}")
        self.model.hparams.update(override_hparams)

        self.use_cache = use_cache
        if use_cache:
            try:
                if not os.path.exists("tmp"):
                    os.mkdir("tmp")
                self.cache = pickle.load(open(f"tmp/cache-{name.split('/')[-1]}.p","rb"))
            except:
                self.cache = {}
        else:
            self.cache = {}

    def __call__(self, conversation, add_image=None, max_tokens=2048, skip_cache=False):
        if type(conversation) == str:
            conversation = [conversation]

        cache_key = tuple(conversation) if add_image is None else tuple(conversation + [add_image.tobytes()])

        if cache_key in self.cache and not skip_cache and self.use_cache:
            
            print(self.name, "GETCACHE", repr(self.cache[cache_key]))
            if len(self.cache[cache_key]) > 0:
                return self.cache[cache_key]
            else:
                print("Empty cache hit")

        print(self.name, "CACHE MISS", repr(conversation))

        response = "Model API request failed"
        for _ in range(3):
            try:
                response = self.model.make_request(conversation, add_image=add_image, max_tokens=max_tokens)
                break
            except Exception as e:
                print("RUN FAILED", e)
                time.sleep(10)
                pass
        

        if self.use_cache and response != "Model API request failed":
            self.cache[cache_key] = response
            pickle.dump(self.cache, open(f"tmp/cache-{self.name.split('/')[-1]}.p","wb"))
        
        return response

llm = LLM("Mistral-7B-v0.1-chat-ORPO", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("Qwen1.5-7B-Chat-AWQ", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("Qwen1.5-7B-Chat", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("gemma-7b", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("mixtral-instruct-awq", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("Mixtral-8x7B-Instruct-v0.1", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("openchat_3.5", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("mistral-large-2402", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("mistral-large-2402", override_hparams={'temperature': 0.1}) # For a custom llm via runpod. Model name must match the HuggingFace Repo slug.
# llm = LLM("gpt-3.5-turbo", override_hparams={'temperature': 0.1})
#llm = LLM("command")
# llm = LLM("gpt-4-1106-preview")
#llm = LLM("claude-instant-1.2")
#llm = LLM("mistral-tiny")
#llm = LLM("gemini-pro", override_hparams={'temperature': 0.3}, use_cache=False)

#eval_llm = LLM("gpt-4-1106-preview")
eval_llm = LLM("gpt-4-0125-preview", override_hparams={'temperature': 0.1})
# eval_llm = LLM("gpt-3.5-turbo", override_hparams={'temperature': 0.1})

vision_eval_llm = LLM("gpt-4-vision-preview", override_hparams={'temperature': 0.1})
