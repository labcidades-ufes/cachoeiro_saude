import os

def deploy_app():
    # Comando para realizar o deploy no shinyapps.io
    os.system("rsconnect deploy shiny ./src/main.py")

deploy_app()