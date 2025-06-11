import os
import geopandas as gpd


def obter_limite_municipio_cachoeiro_de_itapemirim():
    # Definir o caminho relativo
    caminho_municipios = os.path.join(
        "..", "dados", "dados_baixados", "limites_municipios_ES.geojson")

    # Carregar os dados
    gdf_municipios = gpd.read_file(caminho_municipios)

    # Filtra o limite da cidade de Cachoeiro de Itapemirim
    gdf_municipio_cachoeiro_de_itapemirim = gdf_municipios[gdf_municipios['nome']
                                                           == 'Cachoeiro de Itapemirim']

    # salvar
    gdf_municipio_cachoeiro_de_itapemirim.to_file(os.path.join(
        "..", "dados", "dados_tratados", "limite_municipio_cachoeiro_de_itapemirim.geojson"), driver='GeoJSON')
    print("Limite de municipio de Cachoeiro de Itapemirim criado.")


# Função para realizar a interseção e filtrar por Cachoeiro de Itapemirim
def obter_hexagonos_cachoeiro_de_itapemirim():
    # Definir o caminho relativo
    caminho_municipios = os.path.join(
        "..", "dados", "dados_tratados", "limite_municipio_cachoeiro_de_itapemirim.geojson")
    caminho_population = os.path.join(
        "..", "dados", "dados_baixados", "kontur_population_BR_20231101.gpkg")

    # Carregar os dados
    municipio_cachoeiro_de_itapemirim = gpd.read_file(caminho_municipios)
    population = gpd.read_file(caminho_population)

    # ajusta o crs
    municipio_cachoeiro_de_itapemirim = municipio_cachoeiro_de_itapemirim.to_crs(
        epsg=31984)
    population = population.to_crs(epsg=31984)

    # recorta o geodataframe de população pelo limite da cidade de Cachoeiro de Itapemirim
    intersected = gpd.overlay(
        population, municipio_cachoeiro_de_itapemirim, how='intersection')

    if intersected.empty:
        print("Nenhuma interseção encontrada para o município de Cachoeiro de Itapemirim.")

    # salva o arquivo
    intersected.to_file(os.path.join("..", "dados", "dados_tratados",
                        "population_cachoeiro_de_itapemirim_centroides.geojson"), driver='GeoJSON')
    print("População de Cachoeiro de Itapemirim criada.")


def obter_unidades_saude_cachoeiro_de_itapemirim():
    # Definir o caminho relativo
    caminho_geojson_unidades_saude_ES = os.path.join(
        "..", "dados", "dados_baixados", "unidades_saude_ES.geojson")

    # Carregar os dados
    gdf_unidades_saude_ES = gpd.read_file(caminho_geojson_unidades_saude_ES)

    # Filtrar as unidades de saúde pela cidade de Cachoeiro de Itapemirim
    gdf_unidades_saude_cachoeiro_de_itapemirim = gdf_unidades_saude_ES.loc[
        gdf_unidades_saude_ES['MUNICIPIO'] == 'Cachoeiro de Itapemirim']

    # Filtrar as unidades de saude por informações passadas pelo staff de Cachoeiro de Itapemirim
    # gdf_unidades_saude_cachoeiro_de_itapemirim = gdf_unidades_saude_cachoeiro_de_itapemirim.loc[
    #     (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('Estratégia de Sáude', na=False, case=False)
    #     | gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Araraí', na=False, case=False)
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Boa Vista', na=False, case=False))
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Santa Angélica', na=False, case=False))
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Floresta', na=False, case=False))
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Roseira', na=False, case=False)))
    #     & (~gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('Estratégia de Sáude da FamílIa III - Rua 13 de Maio', na=False, case=False))
    # ]

    # salva o arquivo
    gdf_unidades_saude_cachoeiro_de_itapemirim.to_file(os.path.join(
        "..", "dados", "dados_tratados", "unidades_saude_cachoeiro_de_itapemirim.geojson"), driver='GeoJSON')
    print("Unidades de saude de Cachoeiro de Itapemirim criadas.")

    # #unidades de saude de apoio de Cachoeiro de Itapemirim
    # gdf_unidades_saude_apoio = gdf_unidades_saude_cachoeiro_de_itapemirim.loc[
    #     (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Boa Vista', na=False, case=False))
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Santa Angélica', na=False, case=False))
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Floresta', na=False, case=False))
    #     | (gdf_unidades_saude_cachoeiro_de_itapemirim['NOME'].str.contains('US de Roseira', na=False, case=False))]

    # salva o arquivo
    # gdf_unidades_saude_apoio.to_file(os.path.join("..", "dados", "dados_tratados", "unidades_saude_apoio_alegre.geojson"), driver='GeoJSON')
    # print("Unidades de saude de apoio de Cachoeiro de Itapemirim criadas.")
