import json

from openai import OpenAI
import base64
from timeit import default_timer as timer
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
  base_url=os.getenv("OPENAI_BASE_URL"),
  api_key=os.getenv("OPENAI_API_KEY"),
)

def pdf2json(file):
    with open("src/example.txt") as f:
        example = f.read()

    with open("src/prompt.txt") as f:
        prompt = f.read()

    with open(file, "rb") as f:
        data = f.read()

    base64_string = base64.b64encode(data).decode("utf-8")
    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL"),
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "filename": "input.pdf",
                            "file_data": f"data:application/pdf;base64,{base64_string}",
                        },
                        {
                            "type": "input_text",
                            "text": prompt,
                        },
                    ],
                },
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f'Пример:\n\n{example}',
                        }
                    ]
                }
            ],
            extra_body={
                "reasoning": {
                    "exclude": True
                }
            },
        )
    except Exception as e:
        if e.status_code == 429:
            return["RATE_LIMIT", e]

    try:
        return response.output_text.strip('"').replace("```json", '').replace("```", '').strip()
    except Exception as e:
        return [f"ERROR", e]
