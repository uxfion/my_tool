# My Tool

This is a Python package named `my_tool`. It is used for my own convenience.

## Quick Start

### Setup

```bash
pip install git+https://github.com/uxfion/my_tool.git
wget https://raw.githubusercontent.com/uxfion/my_tool/main/.env.example -O .env
# config your own api
vim .env
```

### Use in Python

- Necessary configuration.

```python
from my_tool.openai_tool import *
import os
from dotenv import load_dotenv


load_dotenv()
config = {
    "api_key": os.environ.get("OPENAI_API_KEY"),
    "base_url": os.environ.get("OPENAI_BASE_URL"),
    "model": "gpt-3.5-turbo-1106",
    "concurrency": 10,
    "rpm": 300
}
```

- Single chat.

```python
client = ChatClient(**config)

# single chat
normal_prompt = "鲁迅为什么打周树人？"
print(client.chat(normal_prompt))

# single chat with JSON response
content = "1.这是第一句话。2.这是第二句话。3.这是第三句话。"
prompt = f"{content}\n将这段话断句，不要修改原来段落中的任何字符。"
json_schema = '''{
    "sents": "sents_list",
    "count": "len_of_sents_list"
}'''
# return as a dict
result = client.chat_json(prompt, json_schema)
print(result)
count = result["count"]
sents = result["sents"]
print(count)
print(sents)
```




