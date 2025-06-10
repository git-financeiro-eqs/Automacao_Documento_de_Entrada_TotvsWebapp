import pyautogui as ptg
from time import sleep
import pyperclip as area_trans
from selenium.webdriver.common.keys import Keys
from email.message import EmailMessage
import smtplib
 
 
# Módulo fornecedor de funções utilitárias para os demais módulos do programa.
 
 
ptg.FAILSAFE = True
 
def checar_failsafe():
    """
    Em determinado momento de desenvolvimento desse script, o método FAILSAFE importado diretamente da lib Pyautogui parou de funcionar.
    Para contornar a situação, eu fiz essa função que força o robô a parar, exatamente como funciona no método ptg.FAILSAFE.
    """
    z, f = ptg.position()
    if z == 0 and f == 0:
        raise ptg.FailSafeException
   
 
def mover_seta(passos, direcao, actions):
    """
    Controle de teclado através da Lib Slenium. Em alguns momentos é mais confiável do que o Pyautogui.
    """
    match direcao:
        case "Direita":
            direcao = Keys.ARROW_RIGHT
        case "Esquerda":
            direcao = Keys.ARROW_LEFT
        case "Cima":
            direcao = Keys.ARROW_UP
        case "Baixo":
            direcao = Keys.ARROW_DOWN
        case "tab":
            direcao = Keys.TAB
 
    for _ in range(passos):
        sleep(0.5)
        actions.send_keys(direcao).perform()
 
 
def verificar_chave_de_acesso(actions, processos_ja_vistos):
    """
    Ação de de recolher a chave de acesso da NF no microsiga para que se possa fazer o seu lançamento.
    Ainda conta com uma verificação para que não se repitam as chaves de acesso já testadas em lançamento.	
    """
    
    while True:
        sleep(0.4)
 
        ptg.hotkey("ctrl", "c", interval=0.4)
       
        chave_de_acesso = area_trans.paste()
        if len(chave_de_acesso) == 44:
            break
        
        mudar_a_selecao = encontrar_centro_imagem(imagem=r'src\Imagens\ClicarMudarSelecao.png')
        try:
            x, y = mudar_a_selecao
            y = y + 17
            ptg.click(x,y, interval=0.4)
        except TypeError:
            ptg.click(300,300)

 
    while True:
        try:  
            verificador = processos_ja_vistos.index(chave_de_acesso)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            sleep(0.3)
            ptg.hotkey("ctrl", "c", interval=0.4)
            chave_de_acesso = area_trans.paste()
        except:
            break
 
    return chave_de_acesso
   
 
 
def encontrar_imagem(imagem):
    cont = 0
    while True:
        try:
            encontrou = ptg.locateOnScreen(imagem, grayscale=True, confidence = 0.8)
            checar_failsafe()
            return encontrou
        except:
            sleep(0.8)
            cont += 1
            if cont == 3:
                break
            checar_failsafe()
            pass
           
 
def encontrar_centro_imagem(imagem):
    cont = 0
    while True:
        try:
            x, y = ptg.locateCenterOnScreen(imagem, grayscale=True, confidence=0.92)
            checar_failsafe()      
            return (x, y)
        except:
            sleep(0.8)
            cont += 1
            if cont == 3:
                break
            checar_failsafe()
            pass



def encontrar_imagem_especifica(imagem):
    cont = 0
    while True:
        try:
            x, y = ptg.locateCenterOnScreen(imagem, grayscale=True, confidence=0.80)
            checar_failsafe()      
            return (x, y)
        except:
            sleep(0.8)
            cont += 1
            if cont == 3:
                break
            checar_failsafe()
            pass


def clicar_em_fechar():
    botao_fechar = encontrar_centro_imagem(imagem=r'src\Imagens\BotaoFechar.png')
    try:
        x, y = botao_fechar
        ptg.click(x, y)
        sleep(0.6)
    except TypeError:
        pass
 
 
def formatador(variavel, casas_decimais="{:.2f}"):
    variavel = float(variavel)
    variavel = casas_decimais.format(variavel)
    variavel = variavel.replace(".", ",")
    return variavel
 
 
def formatador2(variavel):
    variavel = float(variavel)
    variavel = "{:.2f}".format(variavel)
    return variavel
 
 
def formatador3(variavel):
    variavel = variavel.replace(",", ".")
    variavel = float(variavel)
    return variavel
 
 
def formatador4(variavel):
    variavel = variavel.replace(".", "")
    variavel = formatador3(variavel)
    return variavel
 
 
def descer_copiar():
    ptg.press("down", interval=0.1)
    ptg.hotkey("ctrl", "c", interval=0.1)
    checar_failsafe()
 
 
def voltar_descer(actions):
    mudar_a_selecao = encontrar_centro_imagem(imagem=r'src\Imagens\ClicarMudarSelecao.png')
    x, y = mudar_a_selecao
    y = y + 17
    ptg.click(x,y, interval=0.4)
    mover_seta(1, "Baixo", actions)
    checar_failsafe()
 
 
def cancelar_lancamento():
    checar_failsafe()
    while True:
        cancelar_lancamento_click = encontrar_centro_imagem(r'src\Imagens\BotaoCancelarLancamento.png')
        try:
            x, y = cancelar_lancamento_click
            ptg.click(x,y, clicks=3, interval=0.1)
            checar_failsafe()
            break
        except:
            pass
    aguarde = encontrar_centro_imagem(r'src\Imagens\ReferenciaAguarde.png')
    while type(aguarde) == tuple:
        aguarde = encontrar_centro_imagem(r'src\Imagens\ReferenciaAguarde.png')
        sleep(1)
    checar_failsafe()
 

def controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos):
    mensagem_pe = "Processo com valor incorreto."
    checar_failsafe()
    controle_repeticao.append(chave_de_acesso)
    if controle_repeticao.count(chave_de_acesso) == 2:
        controle_repeticao = [x for x in controle_repeticao if x != chave_de_acesso]
        enviar_email(numero_da_nf, mensagem_pe, empresa)
        pass
    else:
        processos_ja_vistos.remove(chave_de_acesso)


def cancelar1(actions):
    sleep(0.8)
    voltar_descer(actions)
    sleep(0.5)
    checar_failsafe()
 
 
def cancelar2(actions):
    sleep(0.5)
    cancelar_lancamento()
    voltar_descer(actions)
    sleep(0.3)
    checar_failsafe()
 
 
def cancelar3(actions):
    sleep(0.5)
    cancelar_lancamento()
    sleep(2)
    ptg.press("esc", interval=1)
    ptg.press("enter")
    cancelar1(actions)
    checar_failsafe()
 
 
def escrever_natureza(natureza):
    ptg.press("enter", interval=0.5)
    ptg.write(natureza, interval=0.25)
    ptg.press("enter", interval=0.5)
    ptg.press("left", interval=0.7)
    checar_failsafe()
 
 
def clicar_valor_parcela():
    valor_parcela = encontrar_centro_imagem(r'src\Imagens\ClicarParcela.png')
    while type(valor_parcela) != tuple:
        ptg.moveTo(180, 200)
        aba_duplicatas = encontrar_centro_imagem(r'src\Imagens\BotaoAbaDuplicatas.png')
        x, y =  aba_duplicatas
        checar_failsafe()
        ptg.click(x,y, clicks=4, interval=0.2)
        valor_parcela = encontrar_centro_imagem(r'src\Imagens\ClicarParcela.png')
        sleep(0.4)
    x, y = valor_parcela
    ptg.click(x,y, clicks=4, interval=0.2)
    checar_failsafe()
 
 
def clicar_natureza_duplicata():
    natureza_duplicata_clique = encontrar_centro_imagem(r'src\Imagens\ClicarNaturezaDuplicata.png')
    x, y = natureza_duplicata_clique
    ptg.click(x,y, clicks=4, interval=0.2)
    checar_failsafe()
 
 
def enviar_email(numero_da_nf, variavel, empresa):
    corpo = f"""
        Olá, colaborador!
 
 
        Não consegui lançar a NF abaixo, pode me ajudar?
 
        {numero_da_nf}, compra da {empresa}.
       
        Situação: {variavel}
 
 
        Atenciosamente,
        Bot.Contabil
        """
    
    mensagem = EmailMessage()
    mensagem.set_content(corpo)
    mensagem['Subject'] = "DANFE PARA LANÇAR"
    mensagem['From'] = "bot.contabil@eqseng.com.br"
    mensagem['To'] = "entrada.doc@eqsengenharia.com.br"
 
    try:
        with smtplib.SMTP_SSL('mail.eqseng.com.br', 465) as servidor:
            servidor.login("bot.contabil@eqseng.com.br", "EQSeng852@")
            servidor.send_message(mensagem)
    except Exception as e:
        pass
 
 
def tratar_xml_ilegivel(numero_da_nf, mensagem_xi, empresa, aux=False):
    if aux == True:
        ptg.press(["tab"]*3, interval=0.1)
    else:
        ptg.hotkey(["shift","tab"]*3, interval=0.1)
    ptg.press("down")
    sleep(0.5)
    enviar_email(numero_da_nf, mensagem_xi, empresa)
    checar_failsafe()
 
 
def tratar_lista(lista1, lista2):
    lista_unica = lista1 + lista2
    lista_unica = list(set(lista_unica))
    return lista_unica
 
   
     