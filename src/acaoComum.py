import pyautogui as ptg
from time import sleep
from tkinter import messagebox
from pyperclip import paste, copy
import utils
import atuadorWeb
import operadoresLancamento
import tratamentoItem
import xmltodict
import pyscreeze
import extratorXML


# Este módulo serve pra Fornecer as funções que podem ser usadas tanto pela mariquinhaUnitaria, 
# quanto pela mariquinhaCorrente, que são os dois principais módulos da automação.
# Como eu precisava que a Mariquinha conseguisse lançar muitas RTs de maneira contínua, 
# mas também conseguisse lançar apenas uma RT específica quando necessário, precisei pensar em uma solulução
# que me desse essa flexibilidade. Não tive nenhuma idéia melhor que essa. criei dois módulos, 
# que, embora sejam muito parecidos, não são a mesma coisa, pelo menos não fazem exatamente a mesma coisa.
# Mas devido toda essa semelhança, eu resolvi criar um módulo que contivesse as funções que são comuns a ambos os módulos.


FAILSAFE = True


def inicializar_ERP():
    interagente = atuadorWeb.Interagente()
    driver_microsiga = interagente.abrir_totvs()
    sleep(10)
    driver_microsiga.maximize_window()
    interagente.interagir_pagina_web(driver_microsiga, "#COMP4501", acao="Esperar")
    sleep(3)
    return interagente, driver_microsiga


def proceder_primario():
    """
    Executa o procedimento primário da automação, que inclui:
    - Localizar e clicar na referência da coluna de valor para filtrar da maior para a menor.
    - Verificar o status do processo e, quando identificado que já não há mais
      RTs para lançar, finalizar então o trabalho.
    """
    utils.aguardar1()

    encontrar = utils.encontrar_imagem(r'src\Imagens\ReferenciaColunaValorTelaInicial.png')
    cont = 0
    while type(encontrar) != pyscreeze.Box:
        encontrar = utils.encontrar_imagem(r'src\Imagens\ReferenciaColunaValorTelaInicial.png')
        cont+=1
        if cont == 2:
            ptg.press("enter")
            break 

    sleep(1)

    while True:
        try:
            clique_status = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaColunaValorTelaInicial.png')  
            x, y = clique_status
            break
        except TypeError:
            clique_status = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaStatus.png')  
            x, y = clique_status
            break
        except:
            pass

    ptg.doubleClick(x, y, interval=0.4)
    ptg.click(x, y)
    sleep(1)
    ptg.press("enter", interval=1)
    utils.aguardar1()

    trabalho_acabou = utils.encontrar_imagem_precisao(r'src\Imagens\ReferenciaFinal.png')
    if type(trabalho_acabou) != pyscreeze.Box:
        sleep(1)
        trabalho_acabou = utils.encontrar_imagem_precisao(r'src\Imagens\ReferenciaFinal.png')
        if type(trabalho_acabou) != pyscreeze.Box:
            messagebox.showinfo("Trabalho finalizado", "Trabalho finalizado com sucesso!")
            raise Exception("Trabalho finalizado com sucesso!")



def filtrar_status(funcao="Padrao"):
    """
    Filtra os registros de uma RT para que se efetue o lançamento
    através da coluna status. Além de verificar se já não há mais nenhum
    registro disponível para lançamento.
    """

    estado_do_caixa = ""
    while True:
        try:
            x, y = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaStatus.png')
            break
        except TypeError:
            pass

    ptg.doubleClick(x, y)
    sleep(1.5)
    ptg.click(x, y)
    sleep(1.2)
    ptg.hotkey("ctrl", "c", interval=0.5)
    estado_do_registro = paste()

    if funcao != "Padrao":
        aux_cont = 0
        while True:
            if estado_do_registro == "LANCADO":
                return estado_do_registro
            else:
                ptg.click(x, y)
                sleep(0.5)
                ptg.hotkey("ctrl", "c", interval=0.5)
                estado_do_registro = paste()
                aux_cont += 1
            if aux_cont == 3:
                estado_do_registro = "LIMPO"
                return estado_do_registro

    if estado_do_registro == "LANCADO":
        ptg.click(x, y)
        sleep(1.2)
        ptg.hotkey("ctrl", "c", interval=0.5)
        estado_do_registro = paste()
        if estado_do_registro == "LANCADO":
            estado_do_caixa = "FINALIZADO"

    return estado_do_caixa



def verificar_status():
    """
    Verifica o status do registro atual e retorna o controle correspondente.
    O Controlador é uma string que indica qual ação deve ser tomada a partir do status do registro.
    """

    while True:
        x, y = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaStatusTipoRegistro.png')
        y = y + 20
        ptg.doubleClick(x,y)
        sleep(0.8)
        ptg.hotkey("ctrl", "c", interval=0.5)
        dado_extraido = paste()

        match dado_extraido:
            case "NS-NAO SOLICITADO":
                controlador = "Clicar em Solicitar XML"
            case "NX-CHAVE DANFE NAO DISPONIVEL":
                controlador = "Copie a chave de acesso 1"
            case "DS-DISPONIVEL":
                controlador = "Lançar DANFE"
            case "NA-NAO SE APLICA":
                controlador = "Lançar recibo"
            case "SL-SOLICITADATO- AGUARDANDO SEFAZ":
                controlador = "Clicar em Solicitar XML"
            case "NC-SEM CHAVE INFORMADA":
                controlador = "Copie a chave de acesso 2"
        try:
            return controlador
        except UnboundLocalError:
            pass



def insistir_ate_encontrar(x, y):
    """
    Insiste em encontrar as referências de finalização de caixa ou processo pendente.
    Enquanto nenhum dos dois dados que determinam se a automação deve dar o caixa como finalizado ou
    constatar que não conseguirá lançar mais nenhum registro daquela RT não forem encontrados
    essa função mantém a automação em um loop de busca.
    """
    cont = 0
    finalizar = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaFinalizarCaixa.png')
    ainda_tem_processo_pendente = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCaixaInacabado.png')
    if type(finalizar) != tuple and type(ainda_tem_processo_pendente) != tuple:
        while type(finalizar) != tuple and type(ainda_tem_processo_pendente) != tuple:
            finalizar = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaFinalizarCaixa.png')
            ainda_tem_processo_pendente = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCaixaInacabado.png')
            cont+=1
            if cont == 4:
                ptg.moveTo(150,100)
                ptg.doubleClick(x,y)
                sleep(1)
    return finalizar, ainda_tem_processo_pendente



def importar_xml(caminho, driver_microsiga):
    while True:
        clique = utils.encontrar_centro_imagem(r'src\Imagens\ClicarInputServidor.png')
        if type(clique) == tuple:
            x, y = clique
            break

    sleep(1)
    ptg.click(x,y, clicks=3, interval=0.07)
    copy(caminho)
    ptg.hotkey("ctrl", "v", interval=0.7)

    # script js para clicar no botão salvar

    script = """
    // Função JavaScript para procurar em todos os shadowRoots
    function findButton(root) {
        const buttons = root.querySelectorAll('wa-button[caption="Salvar"]');
        if (buttons.length > 0) return buttons[0];
    
        // Procura recursivamente em shadow DOMs
        const shadows = root.querySelectorAll('*');
        for (let el of shadows) {
            if (el.shadowRoot) {
                const found = findButton(el.shadowRoot);
                if (found) return found;
            }
        }
        return null;
    }

    // Começa a busca do documento principal
    const button = findButton(document);
    if (button) {
        button.click();
        return true;
    }
    return false;
    """

    driver_microsiga.execute_script(script)

    utils.aguardar1()
    


def solicitar_XML():
    """
    Solicita o XML da nota fiscal na rotina e trata possíveis erros como NF cancelada ou duplicidade.

    Returns:
        tuple: Retorna informações sobre a NF cancelada e o XML manual, se aplicável.
    """
    x, y = utils.clicar_2x(r'src\Imagens\BotaoSolicitarXML.png')
    nf_cancelada = ""
    falsa_duplicidade = ""
    sleep(0.3)

    while True:
        aguardando1 = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
        if type(aguardando1) == tuple:
            _aguardando = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
            while type(_aguardando) == tuple:
                _aguardando = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
        nf_cancelada = utils.encontrar_centro_imagem(r'src\Imagens\ErroNFCanceladaPeloFornecedor.png')
        falsa_duplicidade = utils.encontrar_centro_imagem(r'src\Imagens\ErroPossivelDuplicidade.png')
        xml_manual = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaXMLAindaNaoSolicitado3.png')
        xml_manual2 = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaXMLAindaNaoSolicitado.png')
        if type(nf_cancelada) == tuple or type(falsa_duplicidade) == tuple or type(xml_manual) == tuple or type(xml_manual2) == tuple:
            ptg.press("tab", interval=1.5)
            ptg.press("enter", interval=1)
        aguardando2 = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
        if type(aguardando2) == tuple:
            _aguardando = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
            while type(_aguardando) == tuple:
                _aguardando = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')

        if type(aguardando1) != tuple and type(aguardando2) != tuple and type(nf_cancelada) != tuple and type(falsa_duplicidade) != tuple and type(xml_manual) != tuple and type(xml_manual2) != tuple:
            ptg.doubleClick(x,y)
            sleep(0.3)
        else:
            break

    sleep(1)
    if type(falsa_duplicidade) == tuple or type(xml_manual) == tuple or type(xml_manual2) == tuple:
        inserir_xml = ("tupla", "tupla")
    else:
        inserir_xml = None
    return nf_cancelada, inserir_xml



def pular_processo():
    _ = filtrar_status()
    sleep(0.5)
    ptg.press("down", interval=0.7)
    _ = filtrar_status()



def clicar_Lancar():
    """
    Clica no botão lançar nota para as DANFES ou Recibos.
    Além de verificar em um novo momento se já não há mais nenhum
    registro disponível para lançamento.
    """
    sleep(0.5)
    x, y = utils.clicar_2x(r'src\Imagens\BotaoLancarNota.png')
    ptg.doubleClick(x,y)
    sleep(0.3)

    utils.lancar_retroativo()
    aguarde1, aguarde2 = utils.aguardar2()
    if type(aguarde1) == tuple or type(aguarde2) == tuple:
        while True:
            aguarde3, aguarde4 = utils.aguardar2()
            if type(aguarde3) != tuple and type(aguarde4) != tuple:
                utils.lancar_retroativo()
                aguarde3, aguarde4 = utils.aguardar2()
                if type(aguarde3) != tuple and type(aguarde4) != tuple:
                    break
    else:
        utils.lancar_retroativo()
        aguarde1, aguarde2 = utils.aguardar2()
        if type(aguarde1) != tuple and type(aguarde2) != tuple:
            ptg.doubleClick(x,y)
    sleep(2)

    caixa_finalizado = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaRegistroJaLancado2.png')
    nf_ja_lancada = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaNFjaLancada.png')
    nf_ja_lancada2 = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaNFjaLancada2.png')
    if type(caixa_finalizado) == tuple:
        caixa_finalizado = True
    elif type(nf_ja_lancada) == tuple or type(nf_ja_lancada2) == tuple:
        caixa_finalizado = "NF já lançada"
    else:
        caixa_finalizado = False
    return caixa_finalizado



def copiar_chave_acesso():
    """
    Copia a chave de acesso da nota fiscal e verifica se o processo foi feito corretamente.

    Returns:
        tuple: Retorna a chave de acesso e um booleano indicando se o processo foi feito corretamente.
    """
    processo_feito_errado = False
    x, y = utils.clicar_2x(r'src\Imagens\BotaoCopiarChaveDeAcesso.png')
    sleep(2)
    encontrar_chave_de_acesso = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuChaveDeAcesso.png')
    caixa_finalizado = utils.encontrar_imagem(r'src\Imagens\ReferenciaRegistroJaLancado2.png')
    while type(encontrar_chave_de_acesso) != pyscreeze.Box:
        if type(caixa_finalizado) == pyscreeze.Box:
            caixa_finalizado = True
            chave_de_acesso = caixa_finalizado
            return chave_de_acesso, processo_feito_errado
        if type(encontrar_chave_de_acesso) != pyscreeze.Box:
            encontrar_chave_de_acesso = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuChaveDeAcesso.png')
            ptg.doubleClick(x, y)
            caixa_finalizado = utils.encontrar_imagem(r'src\Imagens\ReferenciaRegistroJaLancado2.png')
    sleep(0.5)
    ptg.hotkey("ctrl", "c")
    chave_de_acesso = paste()
    chave_de_acesso = chave_de_acesso.replace(" ", "")
    if len(chave_de_acesso) != 44:
        processo_feito_errado = True
    sleep(0.5)
    ptg.press("esc")
    sleep(2)
    return chave_de_acesso, processo_feito_errado



def rejeitar_caixa(mensagem="Centro de Custo Bloqueado."):
    """
    Rejeita o caixa atual com uma mensagem específica. A mensagem que será passada para o campo
    de rejeição depende do tipo de rejeição, que pode ser "Programado" ou "Independente".
    Programado é quando a função de rejeição foi acionada pela própria lógica da automação.
    O caso onde isso acontece é quando o sistema acusa que o CC de um dos registros está bloqueado.
    Independente é quando a função de rejeição foi acionada manualmente pelo usuário através
    da interface da Mariquinha.
    """

    ptg.click(989, 130)
    abriu = utils.encontrar_centro_imagem(r'src\Imagens\BotaoRejeitarCaixa.png')
    while type(abriu) != tuple:
        ptg.click(989, 130)
        abriu = utils.encontrar_centro_imagem(r'src\Imagens\BotaoRejeitarCaixa.png')

    sleep(0.5)
    while True:
        estado_do_caixa = filtrar_status(funcao="Rejeitar Caixa")
        if estado_do_caixa == "LANCADO":
            x, y = utils.clicar_2x(r'src\Imagens\BotaoCancelar.png')
            tela_de_lancamento = utils.esperar_aparecer(r'src\Imagens\ReferenciaDocumentoEntrada.png')
            ptg.hotkey("ctrl", "s", interval=0.5)
            aguarde1, aguarde2 = utils.aguardar2()
            if type(aguarde1) == tuple or type(aguarde2) == tuple:
                while True:
                    aguarde3, aguarde4 = utils.aguardar2()
                    if type(aguarde3) != tuple and type(aguarde4) != tuple:
                        break
        else:
            break

    x, y = abriu
    ptg.doubleClick(x,y)
    campo_mensagem = utils.encontrar_centro_imagem(r'src\Imagens\CampoObservacaoRejeicao.png')

    while type(campo_mensagem) != tuple:
        sleep(0.6)
        x, y = utils.clicar_2x(r'src\Imagens\BotaoRejeitarCaixa.png')
        sleep(0.7)
        campo_mensagem = utils.encontrar_centro_imagem(r'src\Imagens\CampoObservacaoRejeicao.png')

    ptg.moveTo(150,100)

    copy(mensagem)
    ptg.hotkey("ctrl", "v")
    ptg.press("tab", interval=0.5)
    ptg.press("enter", interval=0.5)
    aguarde = utils.encontrar_imagem(r'src\Imagens\TelaDeAguarde1.png')
    aux_cont = 0
    while type(aguarde) != pyscreeze.Box:
        aguarde = utils.encontrar_imagem(r'src\Imagens\TelaDeAguarde1.png')
        aux_cont+=1
        if aux_cont == 0:
            break
    sleep(2)


def copiar_RT():
    sleep(1)
    clicar_input = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCopiarAutorDoRT.png')
    x, y = clicar_input
    y = y + 25
    ptg.click(x, y, clicks=3, interval=0.3)
    sleep(1.5)
    ptg.hotkey("ctrl", "c", interval=2)
    dono_da_rt = paste()
    ptg.hotkey(["shift", "tab"]*2, interval=0.5)
    ptg.hotkey("ctrl", "c", interval=2)
    rt = paste()
    rt = rt.replace(" ", "")
    return dono_da_rt, rt



def extrair_dados_XML(caminho):
    """
    Extrai os dados de um arquivo XML. Há diferentes possibilidades de árvores XML
    que podemos encontrar. O XML nada mais é do que um conjunto de chaves e valores, e chaves que
    comportam mais chaves. Ele pode ter mais de um item, e, tendo mais de um item,
    a abordagem para extrair seus dados é uma (que segue a linha [const_item], que nada mais é do que acessar item por item
    através de seu indice. Ex: 0, 1, 2...), enquanto quando há apenas um item no XML a abordagem é outra.
    """
    try:
        with open(caminho) as fd:
            doc = xmltodict.parse(fd.read())
    except UnicodeDecodeError:
        with open(caminho, encoding='utf-8') as fd:
            doc = xmltodict.parse(fd.read())
    except:
        with open(caminho, encoding='utf-8') as fd:
            doc = xmltodict.parse(fd.read(), attr_prefix="@", cdata_key="#text")

    processador = extratorXML.ProcessadorXML(doc)
    nome_fantasia_forn = processador.coletar_nome_fantasia()

    const_item = 0
    while True:
        try:
            coletor_xml = doc["nfeProc"]["NFe"]["infNFe"]["det"]["prod"]
            impostos_xml = doc["nfeProc"]["NFe"]["infNFe"]["det"]["imposto"]
            valores_do_item = processador.coletar_dados_XML(coletor_xml, impostos_xml)
            break
        except KeyError:
            try:
                coletor_xml = doc["enviNFe"]["NFe"]["infNFe"]["det"]["prod"]
                impostos_xml = doc["enviNFe"]["NFe"]["infNFe"]["det"]["imposto"]
                valores_do_item = processador.coletar_dados_XML(coletor_xml, impostos_xml)
                break
            except KeyError:
                try:
                    coletor_xml = doc["NFe"]["infNFe"]["det"]["prod"]
                    impostos_xml = doc["NFe"]["infNFe"]["det"]["imposto"]
                    valores_do_item = processador.coletar_dados_XML(coletor_xml, impostos_xml)
                    break
                except TypeError:
                    try:
                        coletor_xml = doc["NFe"]["infNFe"]["det"][const_item]["prod"]
                        impostos_xml = doc["NFe"]["infNFe"]["det"][const_item]["imposto"]
                        valores_do_item = processador.coletar_dados_XML(coletor_xml, impostos_xml)
                        const_item += 1
                    except IndexError:
                        break
            except TypeError:
                try:
                    coletor_xml = doc["enviNFe"]["NFe"]["infNFe"]["det"][const_item]["prod"]
                    impostos_xml = doc["enviNFe"]["NFe"]["infNFe"]["det"][const_item]["imposto"]
                    valores_do_item = processador.coletar_dados_XML(coletor_xml, impostos_xml)
                    const_item += 1
                except IndexError:
                    break
        except TypeError:
            try:
                coletor_xml = doc["nfeProc"]["NFe"]["infNFe"]["det"][const_item]["prod"]
                impostos_xml = doc["nfeProc"]["NFe"]["infNFe"]["det"][const_item]["imposto"]
                valores_do_item = processador.coletar_dados_XML(coletor_xml, impostos_xml)
                const_item += 1
            except IndexError:
                break

    itens, indices_e_impostos = processador.trabalhar_dados_XML(valores_do_item)

    return nome_fantasia_forn, itens, indices_e_impostos



def verificar_cadastro_forn(nome_fantasia_forn, actions):
    """
    Essa função verifica se o Siga forçou a abertura da rotina de cadastro de fornecedor
    para os casos em que o fornecedor não tem uma natureza, um nome fantasia,
    nem um tipo de contribuição definidos no sistema.
    """
    cadastro_fornecedor = utils.encontrar_imagem(r'src\Imagens\ReferenciaTelaCadastroDeFornecedor.png')
    if type(cadastro_fornecedor) == pyscreeze.Box:
        sem_nome_fantasia = utils.encontrar_imagem(r'src\Imagens\ForncedorSemNomeFantasia.png')
        if type(sem_nome_fantasia) == pyscreeze.Box:
            utils.mover_seta(2, "tab", actions)
            copy(nome_fantasia_forn)
            sleep(0.3)
            ptg.hotkey("ctrl", "v", interval=0.7)
            utils.mover_seta(1, "tab", actions)
        ptg.hotkey("alt", "a", interval=1)
        aba_adm = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbaAdm.png')
        while type(aba_adm) != pyscreeze.Box:
            aba_adm = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbaAdm.png')
            ptg.hotkey("alt", "a", interval=1)
        utils.mover_seta(5, "tab", actions)
        sleep(0.8)
        copy("2020087")
        ptg.hotkey("ctrl", "v", interval=0.7)
        utils.mover_seta(1, "tab", actions)
        ptg.hotkey("alt", "f", interval=1)
        aba_fiscal = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbaFiscal.png')
        while type(aba_fiscal) != pyscreeze.Box:
            aba_fiscal = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbaFiscal.png')
            ptg.hotkey("alt", "f", interval=1)
        ptg.hotkey(["shift", "tab"]*3, interval=0.7)
        sleep(0.2)
        ptg.press("space", interval=1)
        ptg.press(["up"]*2, interval=0.7)
        ptg.press("enter", interval=0.5)
        ptg.hotkey("ctrl", "s", interval=0.5)



def inserir_valores_da_NF_no_siga(indices_e_impostos, itens, actions):
    """
    Função que realiza o trabalho de inserir os valores dos itens da nota fiscal no sistema SIGA
    com base no que o indicador ctrl_imposto, que indica quanto dos três impostos
    essenciais cada item daquela NF tem, determina.
    """
    cancelar_lancamento = False

    for i, ctrl_imposto in enumerate(indices_e_impostos):

        verificador, item_fracionado = operadoresLancamento.verificar_valor_do_item(itens, i, actions)
        if verificador == True:

            # Circunstância indesejada:
            # Caso o valor do item não corresponda de nenhuma maneira ao total do item na NF,
            # a +TI deve ser contatada imediatamente, pois, a rotina IntAgillitas foi configurada por eles,
            # para puxar exatamente o mesmo valor do item que consta no xml. Então,
            # se o valor não corresponder diretamente, nem estiver fracionado, a +TI deve
            # ser acionada.

            return cancelar_lancamento
        
        tratamento_item = tratamentoItem.TratadorItem(item_fracionado, itens, i, ctrl_imposto)
        item = tratamento_item.tratar_item()
        cont = 0

        match ctrl_imposto:
            case "Nenhum imposto":
                ptg.press(["left"]*4)    
                                    
            case "Apenas o ICMS":
                for lista in item:
                    icms_no_item, bc_icms, aliq_icms, icmsST_no_item, ipi_no_item = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, bc_icms, aliq_icms)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    ptg.press(["left"]*9)
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)                           
                                        
            case "Apenas o ICMSST":
                for lista in item:
                    icms_no_item, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    operadoresLancamento.zerar_imposto()
                    cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, passosST=9)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)                           
                                        
            case "Apenas o IPI":
                for lista in item:
                    icms_no_item, icmsST_no_item, ipi_no_item, base_ipi, aliq_ipi = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    operadoresLancamento.zerar_imposto()
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)                           
                                        
            case "Apenas ICMSST e IPI":
                for lista in item:
                    icms_no_item, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item, base_ipi, aliq_ipi = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    operadoresLancamento.zerar_imposto()
                    cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, passosST=9)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, passosIPI=0)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)                           
                                        
            case "Apenas ICMS e IPI":
                for lista in item:
                    icms_no_item, base_icms, aliq_icms, icmsST_no_item, ipi_no_item, base_ipi, aliq_ipi = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, base_icms, aliq_icms)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, passosIPI=3)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)                           
                                        
            case "Apenas ICMS e ICMSST":
                for lista in item:
                    icms_no_item, base_icms, aliq_icms, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, base_icms, aliq_icms)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, passosST=0)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)
                                        
            case "Todos os impostos":
                for lista in item:
                    icms_no_item, base_icms, aliq_icms, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item, base_ipi, aliq_ipi = lista
                    cancelar_lancamento = operadoresLancamento.definir_TES(ctrl_imposto)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, base_icms, aliq_icms)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, passosST=0)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, passosIPI=12)
                    if cancelar_lancamento:
                        return cancelar_lancamento
                    sleep(0.5)
                    if len(item) > 1:
                        ptg.press("down", interval=0.5)
                    cont+=1
                    operadoresLancamento.corrigir_passos_horizontal(cont, item)
                if len(item) > 1:
                    ptg.press("up", interval=0.5)
                           

        if len(indices_e_impostos) > 1:
            ptg.press("down")

        sleep(2)



def finalizar_lancamento():
    """
    Realiza a tarefa de finalizar o lançamento de cada registro de uma RT.
    """
    ptg.hotkey("ctrl", "s", interval=2.2)

    erro_cnpj = utils.encontrar_centro_imagem(r'src\Imagens\ErroCNPJ.png')
    if type(erro_cnpj) == tuple:
        ptg.press("enter", interval=0.5)
        erro_cnpj = utils.encontrar_centro_imagem(r'src\Imagens\ErroCNPJ.png')
        if type(erro_cnpj) == tuple:
            utils.clicar_em_fechar()
            sleep(0.5)
        campo_sped = utils.encontrar_centro_imagem(r'src\Imagens\CampoSPED.png')
        x, y = campo_sped
        sleep(1)
        ptg.click(x,y)
        sleep(1)
        ptg.write("NF", interval=0.3)
        ptg.press("tab")
        ptg.hotkey("ctrl", "s", interval=1)

    
    campo_sped = utils.encontrar_centro_imagem(r'src\Imagens\CampoSPED.png')
    if type(campo_sped) == tuple:
        while type(campo_sped) == tuple:
            ptg.hotkey("ctrl", "s", interval=1.5)
            campo_sped = utils.encontrar_centro_imagem(r'src\Imagens\CampoSPED.png')
        

    while True:
        sem_tela_final = utils.encontrar_imagem_precisao(r'src\Imagens\ReferenciaSemTelaFinal.png')
        repentina_etapa_final = utils.encontrar_imagem_precisao(r'src\Imagens\ReferenciaFinalPorLancamento.png')
        aguarde = utils.encontrar_imagem_precisao(r'src\Imagens\TelaDeAguarde2.png')
        if type(aguarde) == pyscreeze.Box:
            sleep(0.5)
            continue
        if type(repentina_etapa_final) == pyscreeze.Box:
            utils.tratar_etapa_final()
            break
        elif type(sem_tela_final) == pyscreeze.Box:
            break

    repentina_etapa_final = utils.encontrar_imagem_precisao(r'src\Imagens\ReferenciaFinalPorLancamento.png')
    if type(repentina_etapa_final) == pyscreeze.Box:
        utils.tratar_etapa_final()
        
