from selenium import webdriver  
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
 
 
 
class Interagente:
    """
    Classe para interagir com páginas web usando Selenium WebDriver.
    Permite navegar em páginas, preencher campos, esperar por elementos, e outras interações.
    """
 
    def __init__(self):
        pass
 
 
    def abrir_totvs(self):
        servico = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument(r"user-data-dir=C:\Users\Usuário\AppData\Local\Google\Chrome\User Data\Profile 4")
        options.add_argument("--disable-cache")  
        driver_microsiga = webdriver.Chrome(service=servico)
        driver_microsiga.get("https://totvs.eqsengenharia.com.br:8880/webapp/?E=servicos&P=sigamdi")
        return driver_microsiga
 
 
    def interagir_pagina_web(self, driver, elhtml, acao, limitar_retorno=False, limitar_espera=False):
        """
        Realiza ações em um elemento da página web, como clicar, ou esperar o próprio elemento.
 
        Parâmetros:
            xpath (str): O XPath do elemento a ser encontrado.
            acao (str): A ação a ser executada. Pode ser "Clicar" ou "Esperar".
            limitar_retorno (bool, opcional): Limita o número de tentativas de encontrar o elemento.
            
        """
      
        aux = 0
        while True:
            try: 
                elemento = driver.find_element(By.CSS_SELECTOR, elhtml)
                match acao:
                    case "Clicar":
                        elemento.click()
                    case "Esperar":
                        pass
                break
            except Exception as e:
                sleep(1)
                if limitar_retorno == True:
                    aux+=7
                if limitar_espera == True:
                    aux+=1
                if aux == 21:
                    break
