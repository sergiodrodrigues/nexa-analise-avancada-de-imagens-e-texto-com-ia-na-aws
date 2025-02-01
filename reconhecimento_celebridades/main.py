from pathlib import Path  # Importa o módulo pathlib para manipulação de paths de arquivos

import boto3  # Importa o SDK da AWS para Python (Boto3)
from mypy_boto3_rekognition.type_defs import (  # Importa definições de tipo para o Rekognition
    CelebrityTypeDef,
    RecognizeCelebritiesResponseTypeDef,
)
from PIL import Image, ImageDraw, ImageFont  # Importa a biblioteca Pillow (PIL) para manipulação de imagens

# Configuração (idealmente, isso deveria estar em um arquivo de configuração ou variáveis de ambiente)
REKOGNITION_CLIENT = boto3.client("rekognition")  # Cria um cliente do Rekognition
FONT_PATH = "Ubuntu-R.ttf"  # Define o caminho para a fonte a ser usada
CONFIDENCE_THRESHOLD = 90  # Define o limiar de confiança para identificar celebridades

def get_image_path(filename: str) -> Path:
    """Constrói e retorna um objeto Path para imagens."""
    return Path(__file__).parent / "images" / filename  # Constrói o path para a imagem

def recognize_celebrities(image_path: Path) -> RecognizeCelebritiesResponseTypeDef:
    """Reconhece celebridades em uma imagem usando a API do Rekognition."""
    try:
        with open(image_path, "rb") as image_file:  # Abre o arquivo de imagem para leitura binária
            return REKOGNITION_CLIENT.recognize_celebrities(Image={"Bytes": image_file.read()})  # Chama a API do Rekognition
    except Exception as e:  # Captura exceções como arquivo não encontrado, erros de API, etc.
        print(f"Erro ao reconhecer celebridades em {image_path}: {e}")  # Imprime a mensagem de erro
        return {}  # Retorna um dicionário vazio em caso de erro

def draw_celebrity_boxes(image_path: Path, output_path: Path, celebrities: list[CelebrityTypeDef]):
    """Desenha caixas delimitadoras e nomes em volta de celebridades reconhecidas em uma imagem."""
    try:
        image = Image.open(image_path)  # Abre a imagem usando Pillow
    except FileNotFoundError:  # Captura a exceção de arquivo não encontrado
        print(f"Erro: Imagem não encontrada em {image_path}")  # Imprime a mensagem de erro
        return  # Sai da função

    draw = ImageDraw.Draw(image)  # Cria um objeto Draw para desenhar na imagem
    try:
        font = ImageFont.truetype(FONT_PATH, 20)  # Carrega a fonte especificada
    except IOError:  # Captura a exceção de fonte não encontrada
        print(f"Erro: Fonte não encontrada em {FONT_PATH}. Usando fonte padrão.")  # Imprime a mensagem de erro
        font = ImageFont.load_default()  # Carrega a fonte padrão

    width, height = image.size  # Obtém a largura e altura da imagem

    for celebrity in celebrities:  # Itera sobre as celebridades reconhecidas
        box = celebrity["Face"]["BoundingBox"]  # type: ignore  # Obtém as coordenadas da caixa delimitadora
        left = int(box["Left"] * width)  # type: ignore  # Calcula a coordenada x do canto esquerdo
        top = int(box["Top"] * height)  # type: ignore  # Calcula a coordenada y do canto superior
        right = int((box["Left"] + box["Width"]) * width)  # type: ignore  # Calcula a coordenada x do canto direito
        bottom = int((box["Top"] + box["Height"]) * height)  # type: ignore  # Calcula a coordenada y do canto inferior

        confidence = celebrity.get("MatchConfidence", 0)  # Obtém o nível de confiança da identificação
        if confidence > CONFIDENCE_THRESHOLD:  # Verifica se o nível de confiança é maior que o limiar
            draw.rectangle([left, top, right, bottom], outline="red", width=3)  # Desenha um retângulo vermelho ao redor do rosto

            name = celebrity.get("Name", "Unknown")  # Obtém o nome da celebridade ou define como "Desconhecido"
            position = (left, top - 20)  # Calcula a posição para o texto com o nome

            # Desenha um fundo para o texto para melhor visualização
            bbox = draw.textbbox(position, name, font=font)  # Obtém as coordenadas da caixa delimitadora do texto
            draw.rectangle(bbox, fill="red")  # Desenha um retângulo vermelho como fundo para o texto
            draw.text(position, name, font=font, fill="white")  # Desenha o nome da celebridade em branco

    try:
        image.save(output_path)  # Salva a imagem com as anotações
        print(f"Imagem salva com resultados em: {output_path}")  # Imprime a mensagem de sucesso
    except Exception as e:  # Captura exceções durante o salvamento da imagem
        print(f"Erro ao salvar imagem: {e}")  # Imprime a mensagem de erro

def main():
    """Função principal para processar as imagens e reconhecer celebridades."""
    image_names = ["bbc.jpg", "msn.jpg", "neymar-torcedores.jpg"]  # Lista de nomes de arquivos de imagem
    image_paths = [get_image_path(name) for name in image_names]  # Cria uma lista de objetos Path para as imagens

    for image_path in image_paths:  # Itera sobre os paths das imagens
        response = recognize_celebrities(image_path)  # Chama a função para reconhecer celebridades

        if not response or not response.get("CelebrityFaces"):  # Verifica se a resposta está vazia ou não contém celebridades
            print(f"Nenhuma celebridade encontrada em: {image_path}")  # Imprime a mensagem de que nenhuma celebridade foi encontrada
            continue  # Pula para a próxima imagem

        output_path = get_image_path(f"{image_path.stem}-result.jpg")  # Define o path para a imagem de saída
        draw_celebrity_boxes(image_path, output_path, response["CelebrityFaces"])  # Chama a função para desenhar as caixas

if __name__ == "__main__":
    main()  # Chama a função principal se o script for executado diretamente
