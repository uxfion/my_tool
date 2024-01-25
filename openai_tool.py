import os
import openai
import json
import asyncio
import time
import datetime
from dotenv import load_dotenv


class ChatClient:
    def __init__(self, api_key, base_url, model="gpt-3.5-turbo-1106"):
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.default_model = model

    def chat(self, prompt, model=None):
        if model is None:
            model = self.default_model
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return completion.choices[0].message.content

    def chat_json(self, prompt, json_schema="{\"response\": \"content\"}", model=None):
        if model is None:
            model = self.default_model
        # 检查 expect_json_output 是否为有效的 JSON 字符串
        try:
            json.loads(json_schema)
        except json.JSONDecodeError:
            raise ValueError(f"\n\n==========\nJSON schema: {json_schema} is not a valid JSON string.")
        # final_prompt = f"{prompt} output JSON like {json_schema}"
        final_prompt = f"{prompt} \nPlease respond with your reply in JSON format. The JSON schema should be {json_schema}"
        # print(final_prompt)

        messages = [
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": final_prompt}
        ]

        completion = self.client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=messages
        )

        response = completion.choices[0].message.content
        try:
            json_response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError(f"\n\n==========\nFinal prompt: {final_prompt}\nResponse: {response}\nResponse is not a valid JSON format.")

        return json_response


class AsyncChatClient:
    def __init__(self, api_key, base_url, model="gpt-3.5-turbo-1106", concurrency=10, rpm=300):
        self.client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.default_model = model
        self.rpm = rpm
        self.delay = 60 / rpm
        self.semaphore = asyncio.Semaphore(concurrency)
        self.cut_off = 100
        if concurrency > rpm:
            raise ValueError(f"\n\n==========\nConcurrency: {concurrency} is larger than RPM: {rpm}.")
    
    async def chat(self, prompt, model=None):
        async with self.semaphore:
            if model is None:
                model = self.default_model
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            time.sleep(self.delay)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]} 任务开始：{prompt[:self.cut_off]!r}")
            start_time = time.time()
            completion = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            response = completion.choices[0].message.content
            wait_time = time.time() - start_time
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]} 任务完成：{prompt[:self.cut_off]!r}, 响应：{response[:self.cut_off]!r}, 耗时：{wait_time:5.2f} 秒")
            return response

    async def chat_json(self, prompt, json_schema="{\"response\": \"content\"}", model=None):
        async with self.semaphore:
            if model is None:
                model = self.default_model
            # 检查 expect_json_output 是否为有效的 JSON 字符串
            try:
                json.loads(json_schema)
            except json.JSONDecodeError:
                raise ValueError(f"\n\n==========\nJSON schema: {json_schema} is not a valid JSON string.")

            # final_prompt = f"{prompt} output JSON like {json_schema}"
            final_prompt = f"{prompt} \nPlease respond with your reply in JSON format. The JSON schema should be {json_schema}"
            # print(final_prompt)

            messages = [
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": final_prompt}
            ]
            time.sleep(self.delay)
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]} 任务开始：{prompt[:self.cut_off]!r}")
            start_time = time.time()
            completion = await self.client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=messages
            )

            response = completion.choices[0].message.content
            wait_time = time.time() - start_time
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')[:12]} 任务完成：{prompt[:self.cut_off]!r}, 响应：{response[:self.cut_off]!r}, 耗时：{wait_time:5.2f} 秒")
            try:
                json_response = json.loads(response)
            except json.JSONDecodeError:
                raise ValueError(f"\n\n==========\nFinal prompt: {final_prompt}\nResponse: {response}\nResponse is not a valid JSON format.")

            return json_response

    async def batch_chat(self, prompts, model=None):
        # tasks = [self.chat(prompt, model) for prompt in prompts]
        tasks = []
        for prompt in prompts:
            # 两种方式都可以
            # task = self.chat(prompt)
            task = asyncio.create_task(self.chat(prompt, model))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses


async def main():
    load_dotenv()
    config = {
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "base_url": os.environ.get("OPENAI_BASE_URL"),
        "model": "gpt-3.5-turbo-1106",
        "concurrency": 10,
        "rpm": 300
    }

    async_client = AsyncChatClient(**config)

    prompts = [
        "Hello, what's the weather today?",
        "Tell me a joke.",
        "How does quantum computing work?",
        "越南首都在哪？",
        "瑞士首都在哪？"
    ]

    responses = await async_client.batch_chat(prompts)

    print("\n\n\n")
    for prompt, response in zip(prompts, responses):
        print("============")
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")


if __name__ == "__main__":
    # client = ChatClient(**config)

    # # # 普通聊天
    # # normal_prompt = "中国首都在哪里？"
    # # print(client.chat(normal_prompt))

    # # JSON格式聊天
    # content = "1.这是第一句话。2.这是第二句话。3.这是第三句话。"
    # prompt = f"{content}\n将这段话断句，不要修改原来段落中的任何字符"
    # json_schema = '''{
    #     "sents": "sents_list",
    #     "count": "len_of_sents_list"
    # }'''
    # # print(client.chat_json(prompt, json_schema))
    # result = client.chat_json(prompt, json_schema)
    # count = result["count"]
    # sents = result["sents"]
    # print(count)
    # print(sents)
    asyncio.run(main())
