import json
import os
import time

import boto3
import openai
from dotenv import load_dotenv
from model_config import MODEL_TO_PROVIDER

# Load environment variables
load_dotenv()

# Configuration
MODEL_STRING = "gpt-4.1-mini"
api_key = os.getenv("MODEL_API_KEY")
client = openai.OpenAI(api_key=api_key)
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-west-2")


def set_model(model_id: str) -> None:
    global MODEL_STRING
    MODEL_STRING = model_id
    print(f"Model changed to: {model_id}")


def chat(messages, persona):
    if not client:
        raise ValueError("OpenAI client not initialized. Please set MODEL_API_KEY in your .env file.")
    
    provider = MODEL_TO_PROVIDER[MODEL_STRING]

    if provider == "openai":
        print("Using openai: ", MODEL_STRING)
        system_prompt = None
        if messages and messages[0].get("role") == "system":
            system_prompt = messages[0]["content"]
            messages = messages[1:]

        t0 = time.time()
        out = client.responses.create(
            model=MODEL_STRING,
            instructions=system_prompt,
            input=messages,
            max_output_tokens=2000,
            temperature=0.5,
            store=False,
        )

        dt = time.time() - t0

        text = out.output_text.strip()

        tok_out = out.usage.output_tokens
        tok_in = out.usage.input_tokens
        total_tok = (
            tok_out + tok_in
            if tok_out is not None and tok_in is not None
            else len(text.split())
        )

        return text, dt, total_tok, (total_tok / dt if dt else total_tok)
    elif provider == "anthropic":
        print("Using anthropic: ", MODEL_STRING)
        t0 = time.time()

        claude_messages = [
            {"role": m["role"], "content": m["content"]} for m in messages
        ]

        response = bedrock_runtime.invoke_model(
            modelId=MODEL_STRING,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": claude_messages,
                    "max_tokens": 500,
                    "temperature": 0.5,
                }
            ),
        )

        dt = time.time() - t0
        body = json.loads(response["body"].read())

        text = "".join(
            part["text"] for part in body["content"] if part["type"] == "text"
        ).strip()
        total_tok = len(text.split())

        return text, dt, total_tok, (total_tok / dt if dt else total_tok)
    elif provider == "deepseek":
        print("Using deepseek: ", MODEL_STRING)
        t0 = time.time()

        prompt = messages[-1]["content"]

        formatted_prompt = (
            f"<｜begin▁of▁sentence｜><｜User｜>{prompt}<｜Assistant｜><think>\n"
        )

        response = bedrock_runtime.invoke_model(
            modelId=MODEL_STRING,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {
                    "prompt": formatted_prompt,
                    "max_tokens": 500,
                    "temperature": 0.5,
                    "top_p": 0.9,
                }
            ),
        )

        dt = time.time() - t0
        body = json.loads(response["body"].read())

        text = body["choices"][0]["text"].strip()
        total_tok = len(text.split())

        return text, dt, total_tok, (total_tok / dt if dt else total_tok)
    elif provider == "meta":
        print("Using meta (LLaMA): ", MODEL_STRING)
        t0 = time.time()

        prompt = messages[-1]["content"]

        formatted_prompt = (
            "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n"
            + prompt.strip()
            + "\n<|eot_id|>\n<|start_header_id|>assistant<|end_header_id|>\n"
        )

        response = bedrock_runtime.invoke_model(
            modelId=MODEL_STRING,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {"prompt": formatted_prompt, "max_gen_len": 512, "temperature": 0.5}
            ),
        )

        dt = time.time() - t0
        body = json.loads(response["body"].read())
        text = body.get("generation", "").strip()
        total_tok = len(text.split())

        return text, dt, total_tok, (total_tok / dt if dt else total_tok)
    elif provider == "mistral":
        print("Using mistral: ", MODEL_STRING)
        t0 = time.time()

        prompt = messages[-1]["content"]
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"

        response = bedrock_runtime.invoke_model(
            modelId=MODEL_STRING,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(
                {"prompt": formatted_prompt, "max_tokens": 512, "temperature": 0.5}
            ),
        )

        dt = time.time() - t0
        body = json.loads(response["body"].read())

        text = body["outputs"][0]["text"].strip()
        total_tok = len(text.split())

        return text, dt, total_tok, (total_tok / dt if dt else total_tok)

