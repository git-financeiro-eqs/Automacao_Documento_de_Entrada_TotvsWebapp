import pyautogui as ptg
from time import sleep
from selenium.webdriver.common.keys import Keys
from email.message import EmailMessage
import pyscreeze
import smtplib


# Módulo fornecedor de funções utilitárias para os demais módulos do programa.


FAILSAFE = True

def enviar_email(rt, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica):
    """
    Dispara um E-mail para cada RT que por algum motivo não foi finalizada.
    """
    
    mensagens = []
    
    if len(chave_sefaz) > 0:
        mensagem_chave = f"{len(chave_sefaz)} processo(s) onde o sistema aponta que a chave de acesso não foi encontrada no SEFAZ."
    else:
        mensagem_chave = ""
    mensagens.append(mensagem_chave)

    if len(ncm_problematica) > 0:
        mensagem_ncm = f"{len(ncm_problematica)} processo(s) onde o sistema aponta que a NCM está incorreta."
    else:
        mensagem_ncm = ""
    mensagens.append(mensagem_ncm)

    if len(sem_xml) > 0:
        mensagem_xml_aus = f"{len(sem_xml)} processo(s) que não tenho o XML no meu repositório."
    else:
        mensagem_xml_aus = ""
    mensagens.append(mensagem_xml_aus)

    if len(cond_pag) > 0:
        mensagem_cond_pag = f"{len(cond_pag)} processo(s) com erro na condição de pagamento."
    else:
        mensagem_cond_pag = ""
    mensagens.append(mensagem_cond_pag)

    if len(cnpj_inconclusivo) > 0:
        mensagem_cnpj = f"{len(cnpj_inconclusivo)} processo(s) onde o sistema aponta um erro no CNPJ."
    else:
        mensagem_cnpj = ""
    mensagens.append(mensagem_cnpj)

    if len(chave_inconforme) > 0:
        mensagem_ch_inc = f"{len(chave_inconforme)} processo(s) com uma chave de acesso impossível."
    else:
        mensagem_ch_inc = ""
    mensagens.append(mensagem_ch_inc)

    if len(nf_ja_lancada) > 0:
        mensagem_xml = f"{len(nf_ja_lancada)} processo(s) já lançados segundo a rotina IntAgillitas"
    else:
        mensagem_xml = ""
    mensagens.append(mensagem_xml)

    if len(bloqueado) > 0:
        mensagem_bloq = f"{len(bloqueado)} processo(s) com um item bloqueado."
    else:
        mensagem_bloq = ""
    mensagens.append(mensagem_bloq)

    mensagem = [str(elemento) for elemento in mensagens if elemento != ""]
    string = "\n".join(mensagem)


    corpo = f"""
Olá, colaborador!


Não consegui finalizar a {rt[0]} - {dono_da_rt[0]}                 

Causa:
{string}


Pode me ajudar?

Atenciosamente,
Mariquinha,
    """
    
    carta = EmailMessage()
    carta.set_content(corpo)
    carta['Subject'] = "RT para verificar"
    carta['From'] = "bot.contabil@eqseng.com.br"
    carta['To'] = ["caixa@eqsengenharia.com.br", "jesse.silva@eqsengenharia.com.br"]

    try:
        with smtplib.SMTP_SSL('grid331.mailgrid.com.br', 465) as servidor:
            servidor.login("eqsengenharia@eqsengenharia.com.br", "YXPLlbnL2N")
            servidor.send_message(carta)
    except Exception as e:
        pass
 


def encontrar_imagem(imagem):
    cont = 0
    while True:
        try:
            encontrou = ptg.locateOnScreen(imagem, grayscale=True, confidence = 0.85)
            return encontrou
        except:
            sleep(0.8)
            cont += 1
            if cont == 2:
                break
            pass
            

def encontrar_centro_imagem(imagem):
    cont = 0
    while True:
        try:
            x, y = ptg.locateCenterOnScreen(imagem, grayscale=True, confidence=0.94)     
            return (x, y)
        except:
            sleep(0.8)
            cont += 1
            if cont == 2:
                break
            pass


def encontrar_imagem_precisao(imagem):
    cont = 0
    while True:
        try:
            encontrou = ptg.locateOnScreen(imagem, grayscale=True, confidence=0.96)     
            return encontrou
        except:
            sleep(0.8)
            cont += 1
            if cont == 2:
                break
            pass


def aguardar():
    _ = esperar_aparecer(r'src\Imagens\TelaDeAguarde1.png')
    sleep(0.6)
    aguarde_final = encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde3.png')
    while type(aguarde_final) == tuple:
        aguarde_final = encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde3.png')
    sleep(2)


def aguardar1():
    aguarde = encontrar_imagem(r'src\Imagens\TelaDeAguarde1.png')
    while type(aguarde) == pyscreeze.Box:
        aguarde = encontrar_imagem(r'src\Imagens\TelaDeAguarde1.png')


def aguardar2():
    aguarde1 = encontrar_imagem_precisao(r'src\Imagens\TelaDeAguarde1.png')
    aguarde2 = encontrar_imagem_precisao(r'src\Imagens\TelaDeAguarde2.png')
    return aguarde1, aguarde2



def cancelar_lancamento():
    while True:
        cancelar_lancamento_click = encontrar_centro_imagem(r'src\Imagens\BotaoCancelarLancamento.png')
        try:
            x, y = cancelar_lancamento_click
            ptg.click(x,y, clicks=3, interval=0.1)
            break
        except:
            pass
    aguarde = encontrar_centro_imagem(r'src\Imagens\ReferenciaAguarde.png') 
    while type(aguarde) == tuple:
        aguarde = encontrar_imagem(r'src\Imagens\ReferenciaAguarde.png') 
        sleep(1)


def clicar_em_fechar():
    botao_fechar = encontrar_centro_imagem(imagem=r'src\Imagens\BotaoFechar.png')
    try:
        x, y = botao_fechar
        ptg.click(x, y)
        sleep(0.6)
    except TypeError:
        pass


def lancar_retroativo():
    lancamento_retroativo = encontrar_centro_imagem(r'src\Imagens\ReferenciaLancamentoRetroativo.png')
    if type(lancamento_retroativo) == tuple:
        sleep(0.5)
        ptg.press("enter")
        sleep(1)


def repetir_botao():
    repetir_acao = encontrar_centro_imagem(r'src\Imagens\BotaoLancarNota.png')
    while type(repetir_acao) == tuple:
        ptg.press("enter")
        repetir_acao = encontrar_centro_imagem(r'src\Imagens\BotaoLancarNota.png')


def tratar_processos_pendentes():
    ptg.press("enter")
    sleep(1)
    variavel = encontrar_centro_imagem(r'src\Imagens\BotaoSair2.png')
    x, y = variavel
    ptg.doubleClick(x,y)
    sleep(2.5)
    repetir_botao()


def clicar_2x(imagem):
    variavel = encontrar_centro_imagem(imagem)
    x, y = variavel
    ptg.doubleClick(x,y)
    return x, y


def tratar_etapa_final():
    sleep(1)
    ptg.press('esc', interval=1)
    while True:
        ptg.moveTo(150,100)
        quebrar_loop = encontrar_centro_imagem(r'src\Imagens\ReferenciaFinalPorLancamento.png')
        if type(quebrar_loop) != tuple:
            break
        else:
            ptg.press("esc")


def clicar_botao_sair():
    """
    Não é bem um "clicar" pois o botão não fica visivel na tela para ser clicado. Em vez disso, o botão é acessado
    por meio de teclas de atalho. Essa ação é contingencial, ela só é execultado quando por alguma aleatoriedade
    o siga imputou na RT mais uma etapa para sair do caixa.
    """
    botao_sair = encontrar_centro_imagem(r'src\Imagens\ReferenciaContingencialFinalizarESair.png')
    if type(botao_sair) == tuple:
        ptg.press(["tab"]*6, interval=0.4)
        sleep(0.3)
        ptg.press("enter")
        sleep(2)
    

def esperar_aparecer(imagem):
    encontrar = encontrar_centro_imagem(imagem)
    while type(encontrar) != tuple:
        encontrar = encontrar_centro_imagem(imagem)
    return encontrar


def clicar_finalizar():
    ptg.press("enter")          
    sleep(1)  
    x, y = clicar_2x(r'src\Imagens\BotaoFinalizar.png')
    sleep(1)
    return x, y


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

