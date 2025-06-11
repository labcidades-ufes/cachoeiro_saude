import os
import requests
import geopandas as gpd
from urllib.parse import urlencode
import requests
import gzip
import shutil


def download_limites_municipios():
    # URL base do serviço WFS
    base_url = "https://ide.geobases.es.gov.br/geoserver/ows"

    # Definir os parâmetros WFS para a requisição
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typename": "geonode:idaf_limite_municipal_2018_11",  # Ajustar conforme necessário
        "outputFormat": "application/json"  # Usando GeoJSON como formato de saída
    }

    # Construir a URL completa para a requisição
    url = f"{base_url}?{urlencode(params)}"

    print("Baixando arquivo limites_municipios_ES.geojson")
    # Realizar a requisição para o servidor WFS
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Criar o diretório "data" se não existir
        # os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)

        caminho_arquivo = os.path.join(
            "..", "dados", "dados_baixados", "limites_municipios_ES.geojson")

        # Salvar o resultado GeoJSON no arquivo
        total_tamanho = int(response.headers.get(
            'content-length', 0))  # Tamanho total do arquivo
        tamanho_downloaded = 0

        with open(caminho_arquivo, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                tamanho_downloaded += len(chunk)
                progresso = (tamanho_downloaded / total_tamanho) * \
                    100 if total_tamanho > 0 else 100
                # Atualiza a mesma linha
                print(f"Progresso do download: {progresso:.2f}%", end='\r')

        print("\nArquivo limites_municipios_ES.geojson salvo.")
    else:
        print(f"Falha ao baixar os dados WFS. Status code: {response.status_code}")

# Verificar se o arquivo já existe
#if not os.path.exists(caminho_arquivo):


def download_unidades_saude_ES():
    # URL base do serviço WFS
    base_url = "https://ide.geobases.es.gov.br/geoserver/ows"

    # Definir os parâmetros WFS para a requisição
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typename": "geonode:edificacoes_saude",  # Ajustar conforme necessário
        "outputFormat": "application/json"  # Usando GeoJSON como formato de saída
    }

    # Construir a URL completa para a requisição
    url = f"{base_url}?{urlencode(params)}"

    print("Baixando arquivo unidades_saude_ES.geojson ...")
    # Realizar a requisição para o servidor WFS
    response = requests.get(url)

    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Definir o caminho do arquivo para salvar
        caminho_arquivo = os.path.join(
            "..", "dados", "dados_baixados", "unidades_saude_ES.geojson")

        # Salvar o resultado GeoJSON no arquivo
        total_tamanho = int(response.headers.get(
            'content-length', 0))  # Tamanho total do arquivo
        tamanho_downloaded = 0

        with open(caminho_arquivo, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                tamanho_downloaded += len(chunk)
                progresso = (tamanho_downloaded / total_tamanho) * \
                    100 if total_tamanho > 0 else 100
                # Atualiza a mesma linha
                print(f"Progresso do download: {progresso:.2f}%", end='\r')

        print("\nArquivo unidades_saude_ES.geojson salvo.")
    else:
        print(f"Falha ao baixar os dados WFS. Status code: {response.status_code}")
# else:
#    print("O arquivo já existe, nenhum download necessário.")


def download_population_cachoeiro():
    url = "https://geodata-eu-central-1-kontur-public.s3.amazonaws.com/kontur_datasets/kontur_population_BR_20231101.gpkg.gz"
    nome_arquivo_gpkg = "kontur_population_BR_20231101.gpkg"

    # Caminho para salvar o arquivo baixado
    caminho_arquivo_gz = os.path.join(
        "..", "dados", "dados_baixados", nome_arquivo_gpkg + ".gz")
    caminho_arquivo_gpkg = os.path.join(
        "..", "dados", "dados_baixados", nome_arquivo_gpkg)

    # Baixar o arquivo
    print("Baixando arquivo kontur_population_BR_20231101.gpkg ...")
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        # with open(caminho_arquivo_gz, "wb") as f:
        #     shutil.copyfileobj(response.raw, f)
        # print("Download concluído.")

        total_tamanho = int(response.headers.get('content-length', 0))
        tamanho_downloaded = 0

        # Salvar o arquivo compactado
        with open(caminho_arquivo_gz, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                tamanho_downloaded += len(chunk)
                progresso = (tamanho_downloaded / total_tamanho) * \
                    100 if total_tamanho > 0 else 100
                print(f"Progresso do download: {progresso:.2f}%", end='\r')
        print("\nDownload concluído.")

        # Descompactar o arquivo .gz
        print("Descompactando arquivo kontur_population_BR_20231101.gpkg ...")
        with gzip.open(caminho_arquivo_gz, "rb") as f_in:
            with open(caminho_arquivo_gpkg, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print("Descompactação concluída.")
        print("Arquivo kontur_population_BR_20231101.gpkg salvo.")
    else:
        print(f"Falha ao baixar os dados. Status code: {response.status_code}")

    # Remove o arquivo .gz, se desejar
    os.remove(caminho_arquivo_gz)
