Para instalar as bibliotecas a partir da pasta raiz
pip install -r requirements.txt

Importante: os arquivos main.py e app.py devem ser rodados a partir da pasta src, ou dará erro para achar
os arquivos

Para rodar o aplicativo para fazer o download, tratamento e processamento dos dados a partir da pasta src
python main.py

Quando o aplicativo rodar, será perguntado no terminal se quer fazer o download dos arquivos, tratar os dados,
processar os dados. responda com 'sim' ou 'nao'.

Para rodar o app shiny localmente a partir da pasta src
python app.py

Após fazer o git pull a primeira vez, é necessário fazer o download, tratar os dados e processar os dados para
conseguir rodar o app. Nas proximas vezes, não é necessário, apenas rodarando o app localmente.

Essa versão do código esta com o número de nós da malha viária reduzido, o que faz com que as rotas calculadas
fiquem com linhas mais retas e não sigam inteiramente as vias, mas os pontos inicial e final continuam
corretos.
Para alterar isso comente a linha numero 55 (G = ox.graph_from_polygon(polygon, network_type='all'))
e descomente a linha 54 (#G = ox.graph_from_polygon(polygon, network_type='all', simplify=False)).