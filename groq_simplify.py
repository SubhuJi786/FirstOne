import openai
import os
from config import AZURE_OPENAI_API_KEY, ENDPOINT_URL, DEPLOYMENT_NAME


def simplify(text):
    """Simplify text using Azure OpenAI"""
    try:
        client = openai.AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
            azure_endpoint=ENDPOINT_URL
        )

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system",
                 "content": "Simplify any given content for a 6th-grade level student in simple words."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error simplifying text: {str(e)}"