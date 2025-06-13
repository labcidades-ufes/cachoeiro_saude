# app.py
from exibicao.exibicao import obter_app_ui, server
from shiny import App

# Cria a instância do app e a exporta com o nome 'app'
app = App(obter_app_ui(), server)

if __name__ == "__main__":
    app.run()

