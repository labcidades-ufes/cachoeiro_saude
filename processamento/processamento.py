import os
import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely.geometry import LineString
import math


def obter_centroides():
    # Definir o caminho relativo
    caminho_geojson_population_cachoeiro_de_itapemirim = os.path.join("dados", "dados_tratados", "population_cachoeiro_de_itapemirim.geojson")

    # Carregar os dados
    gdf_population_cachoeiro_de_itapemirim = gpd.read_file(caminho_geojson_population_cachoeiro_de_itapemirim)

    # ajusta o crs
    gdf_population_cachoeiro_de_itapemirim = gdf_population_cachoeiro_de_itapemirim.to_crs(epsg=31984)
    # Calcular os centroides dos hexágonos
    gdf_population_cachoeiro_de_itapemirim['centroid'] = gdf_population_cachoeiro_de_itapemirim.geometry.centroid
    # copia apenas os centroides para o novo geodataframe
    gdf_centroides = gpd.GeoDataFrame(gdf_population_cachoeiro_de_itapemirim[['centroid']].copy(
    ), geometry='centroid')  # Usar 'geometry' para especificar a coluna de geometria

    # Defina explicitamente a coluna 'centroid' como a geometria
    gdf_centroides.set_geometry('centroid', inplace=True)

    # salva o arquivo
    gdf_centroides.to_file(os.path.join("dados", "dados_processados", "population_cachoeiro_de_itapemirim_centroides.geojson"), driver='GeoJSON')
    print("Centroides criados.")


# Função para obter um polígono expandido da área de Cachoeiro de Itapemirim
def obter_dados_viarios_expandido(buffer_size=5000):
    # Definir o caminho relativo
    caminho_municipio = os.path.join("dados", "dados_tratados", "limite_municipio_cachoeiro_de_itapemirim.geojson")

    # Carregar os dados
    municipio_cachoeiro_de_itapemirim = gpd.read_file(caminho_municipio)

    # ajusta o crs
    municipio_cachoeiro_de_itapemirim = municipio_cachoeiro_de_itapemirim.to_crs(epsg=31984)

    # Criar um buffer ao redor do município (em graus)
    municipio_cachoeiro_de_itapemirim_buffered = municipio_cachoeiro_de_itapemirim.buffer(buffer_size)
    municipio_cachoeiro_de_itapemirim_buffered = municipio_cachoeiro_de_itapemirim_buffered.to_crs(epsg=4674)

    # Definir um polígono ao redor de Cachoeiro de Itapemirim
    polygon = municipio_cachoeiro_de_itapemirim_buffered.unary_union

    print("polygon expandido criado com sucesso!")

    # Usar o polígono expandido para obter as vias
    try:
        # G = ox.graph_from_polygon(polygon, network_type='all', simplify=False)
        G = ox.graph_from_polygon(polygon, network_type='all')
        print("Grafo G criado com sucesso!")
    except Exception as e:
        print(f"Erro ao criar o grafo a partir do polígono: {e}")
        # return None, None

    # Converter o grafo para GeoDataFrame
    gdf_viario = ox.graph_to_gdfs(G, nodes=False)

    # salva o geodataframe
    gdf_viario.to_file(os.path.join("dados", "dados_processados", "viario_expandido_cachoeiro_de_itapemirim.geojson"), driver='GeoJSON')
    print("Rede viaria expandida criada.")

    # Salvar o grafo em formato GraphML
    ox.save_graphml(G, filepath=os.path.join("dados", "dados_processados", "grafo_viario_expandido_cachoeiro_de_itapemirim.graphml"))


# Função para calcular e desenhar a rota mais curta
def obter_rotas_centroide_para_saude():
    # Definir o caminho relativo
    caminho_grafo = os.path.join("dados", "dados_processados", "grafo_viario_expandido_cachoeiro_de_itapemirim.graphml")
    caminho_geojson_population_cachoeiro_de_itapemirim_centroides = os.path.join("dados", "dados_processados", "population_cachoeiro_de_itapemirim_centroides.geojson")
    caminho_geojson_unidades_saude_cachoeiro_de_itapemirim = os.path.join("dados", "dados_tratados", "unidades_saude_cachoeiro_de_itapemirim.geojson")

    # Carregar os dados
    grafo_viario = ox.load_graphml(caminho_grafo)
    centroides = gpd.read_file(caminho_geojson_population_cachoeiro_de_itapemirim_centroides)
    unidades_saude = gpd.read_file(caminho_geojson_unidades_saude_cachoeiro_de_itapemirim)

    # ajusta o crs
    grafo_viario = ox.project_graph(grafo_viario, to_crs='EPSG:31984')
    unidades_saude = unidades_saude.to_crs(epsg=31984)
    centroides['geometry'] = centroides['geometry'].to_crs(epsg=31984)

    rotas = []

    print("Calculando rotas.")

    for idx, row in centroides.iterrows():
        centroid = row['geometry']

        # Encontrar a unidade de saúde mais próxima em termos de distância euclidiana
        unidade_saude_mais_proxima = unidades_saude.geometry.distance(centroid).idxmin()
        unidade_saude = unidades_saude.loc[unidade_saude_mais_proxima].geometry

        # Encontrar os nós mais próximos no grafo viário
        nodo_origem = ox.distance.nearest_nodes(grafo_viario, centroid.x, centroid.y)
        nodo_destino = ox.distance.nearest_nodes(grafo_viario, unidade_saude.x, unidade_saude.y)

        # print(f"Nó de origem: {nodo_origem}, Nó de destino: {nodo_destino}")

        if nodo_origem == nodo_destino:
            print(f"Origem e destino são os mesmos para o centroide {idx}. Pulando...")
            continue

        # Calcular a rota mais curta entre os nós usando o peso 'length' (distância em metros)
        try:
            rota = nx.shortest_path(
                grafo_viario, nodo_origem, nodo_destino, weight='length')
            # print(f"Rota calculada: {rota}")
            rota_coords = [(grafo_viario.nodes[node]['x'],
                            grafo_viario.nodes[node]['y']) for node in rota]

            # Armazenar a rota como uma LineString no GeoDataFrame
            linha_rota = LineString(rota_coords)
            rotas.append({'centroide_idx': idx, 'geometry': linha_rota})

        except nx.NetworkXNoPath:
            print(f"Não foi possível calcular a rota para o centroide {idx}.")

        print(f"Rota {idx} de {len(centroides)}.", end='\r')

    # Converter as rotas para um GeoDataFrame
    gdf_rotas = gpd.GeoDataFrame(rotas, crs="EPSG:31984")

    # salva o geodataframe
    gdf_rotas.to_file(os.path.join("dados", "dados_processados", "rotas.geojson"), driver='GeoJSON')
    print("\nRotas para unidades de saúde criadas.")


def obter_gdf_peso_hexagonos():
    # Definir o caminho relativo
    caminho_grafo = os.path.join("dados", "dados_processados", "grafo_viario_expandido_cachoeiro_de_itapemirim.graphml")
    caminho_geojson_population_cachoeiro_de_itapemirim = os.path.join("dados", "dados_tratados", "population_cachoeiro_de_itapemirim.geojson")
    caminho_geojson_population_cachoeiro_de_itapemirim_centroides = os.path.join("dados", "dados_processados", "population_cachoeiro_de_itapemirim_centroides.geojson")
    caminho_geojson_unidades_saude_cachoeiro_de_itapemirim = os.path.join("dados", "dados_tratados", "unidades_saude_cachoeiro_de_itapemirim.geojson")

    # Carregar os dados
    grafo_viario = ox.load_graphml(caminho_grafo)
    gdf_hexagonos = gpd.read_file(caminho_geojson_population_cachoeiro_de_itapemirim)
    centroides = gpd.read_file(caminho_geojson_population_cachoeiro_de_itapemirim_centroides)
    unidades_saude = gpd.read_file(caminho_geojson_unidades_saude_cachoeiro_de_itapemirim)

    gdf_hexagonos['centroid'] = centroides['geometry']

    # ajusta o crs
    grafo_viario = ox.project_graph(grafo_viario, to_crs='EPSG:31984')
    unidades_saude = unidades_saude.to_crs(epsg=31984)
    gdf_hexagonos['centroid'] = gdf_hexagonos['centroid'].to_crs(epsg=31984)

    # Adicionar a nova coluna 'peso' ao GeoDataFrame de hexágonos
    gdf_hexagonos['peso'] = None  # Inicializando a nova coluna
    gdf_hexagonos['distancia'] = None
    gdf_hexagonos['log_population'] = None

    print("Calculando distancia e pesos.")

    for idx, row in gdf_hexagonos.iterrows():
        centroid = row['centroid']
        population = row['population']

        # print(f"centroid.x:{centroid.x},centroid.y{centroid.y}")

        # Encontrar a unidade de saúde mais próxima em termos de distância euclidiana
        unidade_saude_mais_proxima = unidades_saude.geometry.distance(centroid).idxmin()
        unidade_saude = unidades_saude.loc[unidade_saude_mais_proxima].geometry

        # Encontrar os nós mais próximos no grafo viário
        nodo_origem = ox.distance.nearest_nodes(grafo_viario, centroid.x, centroid.y)
        nodo_destino = ox.distance.nearest_nodes(grafo_viario, unidade_saude.x, unidade_saude.y)

        # print(f"Nó de origem: {nodo_origem}, Nó de destino: {nodo_destino}")

        # Calcular a rota mais curta entre os nós usando o peso 'length' (distância em metros)
        try:
            distancia = nx.shortest_path_length(grafo_viario, nodo_origem, nodo_destino, weight='length')

            gdf_hexagonos.at[idx, 'distancia'] = distancia

        except nx.NetworkXNoPath:
            print(f"Não foi possível calcular a rota para o centroide {idx}.")

        log_population = math.log(population)
        gdf_hexagonos.at[idx, 'log_population'] = log_population

        print(f"Distancia {idx} de {len(gdf_hexagonos)}.", end='\r')

    # Selecionar apenas as colunas desejadas para o novo arquivo de hexágonos
    gdf_novo_hexagonos = gdf_hexagonos[['h3', 'geometry', 'population', 'peso', 'distancia', 'log_population']]

    # Ignorar os valores onde a distância é 'None'
    gdf_novo_hexagonos = gdf_novo_hexagonos[gdf_novo_hexagonos['distancia'].notnull()]

    # media da coluna distancia
    media_distancia = gdf_novo_hexagonos['distancia'].mean()
    # desvio padrão da coluna distancia
    std_distancia = gdf_novo_hexagonos['distancia'].std()

    # media do log natural da coluna population
    media_log_population = gdf_novo_hexagonos['log_population'].mean()
    # desvio padrão do log natural da coluna population
    std_log_population = gdf_novo_hexagonos['log_population'].std()

    for idx, row in gdf_novo_hexagonos.iterrows():
        population = row['population']
        distancia = row['distancia']

        # Normalizar população e distância e fazer um shift para acabar com valores negativos
        norm_population = ((math.log(population) - media_log_population) / std_log_population) + 10
        norm_distancia = ((distancia - media_distancia) / std_distancia) + 10

        # Calcular o valor de 'peso' como soma das normalizações
        peso = norm_population * norm_distancia

        # Atribuir o valor de 'peso' à nova coluna
        gdf_novo_hexagonos.at[idx, 'peso'] = peso

        print(f"\nPeso {idx} de {len(gdf_novo_hexagonos)}.", end='\r')

    # ajusta o crs
    gdf_novo_hexagonos = gdf_novo_hexagonos.to_crs(epsg=31984)

    # salva o geodataframe
    gdf_novo_hexagonos.to_parquet(os.path.join("dados", "dados_processados", "peso_hexagonos.parquet"))
    print("\nPesos criados.")
