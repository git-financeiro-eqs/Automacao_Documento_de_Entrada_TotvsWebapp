from selenium import webdriver  
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        driver_microsiga.get("https://totvs.eqsengenharia.com.br:8880/webapp/")
        driver_microsiga.maximize_window()
        return driver_microsiga
 
 
    def interagir_pagina_web(self, driver, elhtml, acao, texto="", limitar_espera=False, limitar_retorno=False):
        """
        Realiza ações em um elemento da página web, como clicar, escrever ou retornar o próprio elemento.
 
        Parâmetros:
            xpath (str): O XPath do elemento a ser encontrado.
            acao (str): A ação a ser executada. Pode ser "Clicar", "Escrever", "Retornar elemento" ou "Esperar".
            texto (str, opcional): Texto a ser inserido caso a ação seja "Escrever".
            limitar_espera (bool, opcional): Limita o tempo de espera para encontrar o elemento.
            limitar_retorno (bool, opcional): Limita o número de tentativas de encontrar o elemento.
 
        Retorna:
            WebElement ou None: Retorna o elemento se a ação for "Retornar elemento", caso contrário retorna None.
        """
 
        aux = 0
        while True:
            try:
                elemento = driver.find_element(By.CSS_SELECTOR, elhtml)
                match acao:
                    case "Clicar":
                        elemento.click()
                    case "Escrever":
                        elemento.clear()
                        sleep(0.8)
                        elemento.send_keys(texto)
                    case "Retornar elemento":
                        return elemento
                    case "Esperar":
                        pass
                break
            except Exception as e:
                sleep(1)
                if limitar_espera == True:
                    aux+=1
                if limitar_retorno == True:
                    aux+=7.5
                if aux == 15:
                    break
 
 
 
    def migrar_ao_frame(self, driver, acao, indice=0):
        match acao:
            case "ir":
                driver.switch_to.frame(indice)
            case "voltar":
                driver.switch_to.default_content()
            case "Aceitar alerta":
                try:
                    WebDriverWait(driver, 15).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    alert.accept()
                    return True
                except:
                    return False
 
   