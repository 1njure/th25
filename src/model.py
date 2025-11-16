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
    with open("example.txt") as f:
        example = f.read()

    with open(file, "rb") as f:
        data = f.read()

    base64_string = base64.b64encode(data).decode("utf-8")

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
                        "text": "Собери всю важную для бухгалтерии информацию в виде JSON-структуры. Названия полей должны быть написаны на английском языке, а их содержимое - в оригинале, если это возможно. Дополнительных комментариев не нужно, только JSON.",
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
    try:
        return response.output_text
    except Exception as e:
        print(e)
        return f"Произошла ошибка!\n\n{e}"
