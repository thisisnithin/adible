from typing import Optional, Type, Any

from openai import OpenAI, BaseModel
from dotenv import load_dotenv

load_dotenv(dotenv_path="server/.env")

oai_client = OpenAI()


def oai_complete(query:str, sys_prompt: Optional[str] = "You are a helpful assistant.") -> str:
    completion = oai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": query
            }
        ]
    )
    return completion.choices[0].message.content

def oai_complete_structured(query:str, response_model: Type, sys_prompt: Optional[str] = "You are a helpful assistant.") -> Any:
    completion = oai_client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system","content": sys_prompt},
            {"role": "user", "content": query}
        ],
        response_format=response_model
    )
    return completion.choices[0].message.parsed