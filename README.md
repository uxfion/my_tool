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

```python
from my_tool.openai_tool import ChatClient
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv("./my_tool/.env")
    config = {
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "base_url": os.environ.get("OPENAI_BASE_URL"),
        "model": "gpt-3.5-turbo-1106",
        "concurrency": 10,
        "rpm": 300
    }

    client = ChatClient(**config)

    # 普通聊天
    normal_prompt = "中国首都在哪里？"
    print(client.chat(normal_prompt))
```

