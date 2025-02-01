import json
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_textract.type_defs import DetectDocumentTextResponseTypeDef

# Constantes
IMAGE_FILE_PATH = "images/lista-material-escolar.jpeg"
RESPONSE_FILE_PATH = "response.json"
TEXTRACT_CLIENT_NAME = "textract"

def carregar_imagem(image_file_path: str) -> bytes:
    """Carrega a imagem como bytes."""
    with open(image_file_path, "rb") as image_file:
        return image_file.read()

def chamar_textract(image_bytes: bytes) -> DetectDocumentTextResponseTypeDef:
    """Chama a API do Textract para detectar o texto na imagem."""
    textract_client = boto3.client(TEXTRACT_CLIENT_NAME)
    try:
        response = textract_client.detect_document_text(Document={"Bytes": image_bytes})
        return response
    except ClientError as error:
        print(f"Erro ao chamar o Textract: {error}")
        return None

def salvar_resposta(response: DetectDocumentTextResponseTypeDef) -> None:
    """Salva a resposta do Textract em um arquivo JSON."""
    with open(RESPONSE_FILE_PATH, "w") as response_file:
        json.dump(response, response_file, indent=4)  # Adicionado indentação para melhor legibilidade

def extrair_linhas_da_resposta(response_file_path: str) -> list[str]:
    """Extrai as linhas de texto da resposta do Textract."""
    try:
        with open(response_file_path, "r") as response_file:
            response_data: DetectDocumentTextResponseTypeDef = json.load(response_file)
            blocks = response_data["Blocks"]
            lines: list[str] = [block["Text"] for block in blocks if block["BlockType"] == "LINE"]
            return lines
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Erro ao processar o arquivo de resposta: {error}")
        return []

if __name__ == "__main__":
    image_bytes = carregar_imagem(IMAGE_FILE_PATH)
    if image_bytes:
        response = chamar_textract(image_bytes)
        if response:
            salvar_resposta(response)
            lines = extrair_linhas_da_resposta(RESPONSE_FILE_PATH)
            for line in lines:
                print(line)

