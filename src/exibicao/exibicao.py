import folium
import os
import folium
from folium import Popup
import geopandas as gpd
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from shiny import App, ui, render


# Criar o mapa usando Folium
def criar_mapa():
    # Localização inicial no mapa (Cachoeiro do Itapemirim, ES)
    localizacao_inicial = [-20.8481, -41.1121]
    zoom_inicial = 10

    # Definir o caminho relativo
    caminho_municipio = os.path.join("..", "dados", "dados_tratados", "limite_municipio_cachoeiro_de_itapemirim.geojson")
    caminho_geojson_unidades_saude_cachoeiro_de_itapemirim = os.path.join("..", "dados", "dados_tratados", "unidades_saude_cachoeiro_de_itapemirim.geojson")
    #caminho_geojson_unidades_saude_alegre_apoio = os.path.join("..", "dados", "dados_tratados", "unidades_saude_apoio_alegre.geojson")
    caminho_geojson_population_cachoeiro_de_itapemirim = os.path.join("..", "dados", "dados_tratados", "population_cachoeiro_de_itapemirim.geojson")
    caminho_geojson_population_cachoeiro_de_itapemirim_centroides = os.path.join("..", "dados", "dados_processados", "population_cachoeiro_de_itapemirim_centroides.geojson")
    caminho_geojson_viario_expandido = os.path.join("..", "dados", "dados_processados", "viario_expandido_cachoeiro_de_itapemirim.geojson")
    caminho_geojson_rotas = os.path.join("..", "dados", "dados_processados", "rotas.geojson")
    caminho_geojson_peso_hexagonos = os.path.join("..", "dados", "dados_processados", "peso_hexagonos.parquet")

    # Carregar os dados
    gdf_municipio_cachoeiro_de_itapemirim = gpd.read_file(caminho_municipio)
    gdf_unidades_saude_cachoeiro_de_itapemirim = gpd.read_file(caminho_geojson_unidades_saude_cachoeiro_de_itapemirim)
    #gdf_unidades_saude_apoio = gpd.read_file(caminho_geojson_unidades_saude_alegre_apoio)
    gdf_population_cachoeiro_de_itapemirim = gpd.read_file(caminho_geojson_population_cachoeiro_de_itapemirim)
    gdf_population_cachoeiro_de_itapemirim_centroides = gpd.read_file(caminho_geojson_population_cachoeiro_de_itapemirim_centroides)
    gdf_viario_expandido = gpd.read_file(caminho_geojson_viario_expandido)
    gdf_rotas = gpd.read_file(caminho_geojson_rotas)
    gdf_peso_hexagonos = gpd.read_parquet(caminho_geojson_peso_hexagonos)

    #ajusta o crs
    gdf_municipio_cachoeiro_de_itapemirim = gdf_municipio_cachoeiro_de_itapemirim.to_crs(epsg=4674)
    gdf_unidades_saude_cachoeiro_de_itapemirim = gdf_unidades_saude_cachoeiro_de_itapemirim.to_crs(epsg=4674)
    #gdf_unidades_saude_apoio = gdf_unidades_saude_apoio.to_crs(epsg=4674)
    gdf_population_cachoeiro_de_itapemirim = gdf_population_cachoeiro_de_itapemirim.to_crs(epsg=4674)
    gdf_population_cachoeiro_de_itapemirim_centroides = gdf_population_cachoeiro_de_itapemirim_centroides.to_crs(epsg=4674)
    gdf_viario_expandido = gdf_viario_expandido.to_crs(epsg=4674)
    gdf_rotas = gdf_rotas.to_crs(epsg=4674)
    gdf_peso_hexagonos = gdf_peso_hexagonos.to_crs(epsg=4674)

    mapa = folium.Map(location=localizacao_inicial, zoom_start=zoom_inicial)
    
    # Adicionar a camada municipio_cachoeiro_de_itapemirim
    folium.GeoJson(
        gdf_municipio_cachoeiro_de_itapemirim.geometry,
        name='Limites da cidade de Cachoeiro de Itapemirim',
        style_function=lambda x: {'color': 'green'}
    ).add_to(mapa)
    
    # Adicionar as unidades de saúde
    if not gdf_unidades_saude_cachoeiro_de_itapemirim.empty:
        for idx, row in gdf_unidades_saude_cachoeiro_de_itapemirim.iterrows():
            if row.geometry.geom_type == 'Point':  # Verificar se a geometria é um ponto
                folium.Marker(location=[row.geometry.y, row.geometry.x], 
                              popup=Popup(f'Unidade de Saúde: {row["NOME"]}'), 
                              icon=folium.Icon(color='green')).add_to(mapa)
                

    # # Adicionar as unidades de saúde de apoio
    # if not gdf_unidades_saude_apoio.empty:
    #     for idx, row in gdf_unidades_saude_apoio.iterrows():
    #         if row.geometry.geom_type == 'Point':  # Verificar se a geometria é um ponto
    #             folium.Marker(location=[row.geometry.y, row.geometry.x], 
    #                           popup=Popup(f'Unidade de Saúde: {row["NOME"]}'), 
    #                           icon=folium.Icon(color='blue')).add_to(mapa)
                
    # Verificar se há dados viários expandidos (vias) para exibir
    if not gdf_viario_expandido.empty:
        # Adicionar a camada de vias
        folium.GeoJson(
            gdf_viario_expandido.geometry,
            name='Sistema Viário Expandido Cachoeiro de Itapemirim',
            style_function=lambda x: {'color': 'blue'},
            show=False
        ).add_to(mapa)
    else:
        print("Nenhuma rodovia expandida para exibir em Cachoeiro de Itapemirim.")

    # Verificar se há dados de população para exibir
    if not gdf_population_cachoeiro_de_itapemirim.empty:
        # Adicionar a camada filtrada de população em Cachoeiro de Itapemirim
        folium.GeoJson(
            gdf_population_cachoeiro_de_itapemirim.geometry,
            name='População Cachoeiro de Itapemirim',
            style_function=lambda x: {'color': 'red'},
            show=False
        ).add_to(mapa)

    else:
        print("Nenhum dado de hexágonos para exibir em Cachoeiro de Itapemirim.")

    # Criar uma camada separada para os centroides
    centroid_layer = folium.FeatureGroup(name='Centroides', show=False)
    
    # Adicionar os centroides ao mapa como pontos vermelhos
    for idx, row in gdf_population_cachoeiro_de_itapemirim_centroides.iterrows():
        centroid = row['geometry']
        folium.CircleMarker(
            location=[centroid.y, centroid.x],
            radius=2,  # Ajuste o tamanho do ponto aqui
            color='red',  # Cor do ponto
            fill=True,
            fill_color='red',  # Preenchimento do ponto
            fill_opacity=1,  # Opacidade do preenchimento
            popup=Popup(f'Centroide do Hexágono: {idx}')
        ).add_to(centroid_layer)  # Adicionar à camada de centroides

    # Adicionar a camada de centroides ao mapa
    centroid_layer.add_to(mapa)


    #função para definir o range de cor para a camada de pesos
    def get_color(gdf_peso_hexagonos, peso):
        # Normaliza o peso entre 0 e 1
        norm = mcolors.Normalize(vmin=gdf_peso_hexagonos['peso'].min(), vmax=gdf_peso_hexagonos['peso'].max())
        # Converte a normalização em uma cor da paleta de cores (vermelho)
        rgba = cm.Reds(norm(peso))  # Usando a paleta Reds
        return f'rgba({int(rgba[0]*255)}, {int(rgba[1]*255)}, {int(rgba[2]*255)}, {rgba[3]})'

    # Verificar se há dados no GeoDataFrame pesos
    if not gdf_peso_hexagonos.empty:
        # Adicionar a nova camada de hexágonos ao mapa
        folium.GeoJson(
            gdf_peso_hexagonos,
            name='Peso dos Hexágonos',
            style_function=lambda feature: {
                'fillColor': get_color(gdf_peso_hexagonos, feature['properties']['peso']),
                'color': 'black',  # Cor da borda
                'weight': 1,
                'fillOpacity': 0.6  # Opacidade do preenchimento
            },
            popup=folium.GeoJsonPopup(fields=['h3', 'peso', 'population'])  # Exibir h3 e peso no popup
        ).add_to(mapa)
    else:
        print("Nenhum dado de hexágonos para exibir.")



    # Criar uma camada para as rotas
    rotas_layer = folium.FeatureGroup(name='Rotas Calculadas', show=False)

    # Desenhar as rotas no FeatureGroup
    if not gdf_rotas.empty:
        # Adicionar a camada de vias
        folium.GeoJson(
            gdf_rotas.geometry,
            name='Sistema Viário Expandido Cachoeiro de Itapemirim',
            style_function=lambda x: {'color': 'blue'}
        ).add_to(rotas_layer)

    # Adicionar o FeatureGroup ao mapa
    rotas_layer.add_to(mapa)

    
    folium.LayerControl().add_to(mapa)
    
    return mapa
    


#App
def obter_app_ui():
    # Definir a interface do Shiny
    app_ui = ui.page_fluid(

        # Definir estilo global para o body para remover margens e paddings
        ui.tags.style("""
            body {
                margin: 0;
                padding: 0;
            }
            .container-fluid {
                padding: 0 !important;
            }
            .row {
                margin: 0 !important;
                padding: 0 !important;
            }
        """),

        # Cabeçalho estilizado (com logotipo e texto à direita)
        ui.tags.div(
            ui.tags.h1(
                ui.tags.span("Escritório", style="color: #7C019B; margin: 0; display: inline-block; float: left;"),
                ui.tags.span(
                    ui.tags.span("de Dados", style="color: #7C019B; margin: 0 8px 0 0; display: inline-block;"),
                    ui.tags.span("| Cachoeiro de Itapemirim", style="color: #FEAA01; ; margin: 0; display: inline-block;")                
                ),
                style="float: left; margin-left: 50px; display: flex; flex-direction: column; align-items: flex-start; font-size: 1.5em;"
            ),
            ui.tags.h2("Visualização geolocalizada de acesso às Unidades Básicas de Saúde",
                style="color: #93319B; margin: 0 50px 0 0; padding: 0; float: right; font-size: 1.5em;"),
            style="height: 15vh; width: 100vw; padding: 10px; font-size: 3vh; display: flex; justify-content: space-between; align-items: center; background-color: white; font-family: 'Arial', sans-serif; font-weight: bold;"
        ),

        # Corpo do aplicativo (mapa, gráficos, etc.)
        ui.tags.div(
            ui.output_ui("mapa_output"),
            style="height: 80vh; width: 100vw; border: none; background-color: #f0f0f0; overflow: hidden; margin: 0; padding: 0;"
        ),

        # Rodapé estilizado
        ui.tags.div(
            ui.tags.p(
                "LabCidades Projetos Inteligentes - Universidade Federal do Espírito Santo (UFES), Goiabeiras, Vitória - ES, 29075-053",
                style="color: white; font-size: 0.9em; text-align: center; margin: 0; padding: 0;"
            ),
            style="height: 5vh; width: 100vw; background-color: #6D6E70; display: flex; justify-content: center; align-items: center; position: fixed; bottom: 0; margin: 0;"
        )
    )
    return app_ui

# Definir o servidor
def server(input, output, session):
    @output
    @render.ui
    def mapa_output():
        mapa = criar_mapa()
        mapa_html = mapa._repr_html_()
        return ui.HTML(mapa_html)
    
def roda_app():
    # Criar o app
    app = App(obter_app_ui(), server)

    # Rodar o app
    app.run()