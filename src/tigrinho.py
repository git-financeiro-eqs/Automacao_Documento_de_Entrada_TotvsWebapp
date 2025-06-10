from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from pyperclip import paste, copy    
from time import sleep
import atuadorWeb
import utils
import extratorXML
import tratamentoItem
import operadoresLancamento
import pyautogui as ptg
import xmltodict  
import pyscreeze
 
 

ptg.FAILSAFE = True
mensagem_sb = "Processo sem boleto."
mensagem_pb = "Processo Bloqueado."
mensagem_pe = "Processo com algum erro impeditivo de lançamento."
mensagem_xi = "Processo com um XML que não consigo ler."
 
 
def tigrinho(empresa):
    """
    Função para inicialização da automação no Totvs Webapp.
    """
    
    controle_repeticao = []
    processos_ja_vistos = []

    interagente = atuadorWeb.Interagente()

    driver_microsiga = interagente.abrir_totvs()
    sleep(15)
    driver_microsiga.maximize_window()

    interagente.interagir_pagina_web(driver_microsiga, "#COMP6020", acao="Esperar")


    actions = ActionChains(driver_microsiga)
   
   
    def robozinho():
        """
        Função principal. Nela está o fluxo da tarefa que esse programa realiza.
        É uma função recursiva devido a necessidade de reinicialização do processo
        que alguma circunstância indesejada pode provocar.
        """

        chave_de_acesso = utils.verificar_chave_de_acesso(actions, processos_ja_vistos)

        numero_da_nf = chave_de_acesso[25:34]

        processos_ja_vistos.append(chave_de_acesso)

        aux = False
        while True:
            caminho = "C:\\Users\\User\\OneDrive - EQS Engenharia Ltda\\Área de Trabalho\\Mariquinha\\xmlFiscalio\\" + chave_de_acesso + ".xml"
            try:
                with open(caminho) as fd:
                    doc = xmltodict.parse(fd.read())
                    break
            except UnicodeDecodeError:
                with open(caminho, encoding='utf-8') as fd:
                    doc = xmltodict.parse(fd.read())
                    break
            except FileNotFoundError:
                interagente.interagir_pagina_web(driver_microsiga, "#COMP6026", acao="Clicar")

                abriu = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaApareceuTela.png')
                while type(abriu) != tuple:
                    abriu = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaApareceuTela.png')
                    interagente.interagir_pagina_web(driver_microsiga, "#COMP6026", acao="Clicar", limitar_retorno=True)

                sleep(1.5)
                copy("C:\\Users\\User\\OneDrive - EQS Engenharia Ltda\\Área de Trabalho\\Mariquinha\\xmlFiscalio\\")
                ptg.hotkey("ctrl", "v", interval=0.6)

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

                interagente.interagir_pagina_web(driver_microsiga, "#COMP9012", acao="Clicar")
                sleep(1.5)
                interagente.interagir_pagina_web(driver_microsiga, "#COMP9012", acao="Esperar")
                interagente.interagir_pagina_web(driver_microsiga, "#COMP9012", acao="Clicar")

            except:
                try:
                    with open(caminho, encoding='utf-8') as fd:
                        doc = xmltodict.parse(fd.read(), attr_prefix="@", cdata_key="#text")
                        break
                except xmltodict.expat.ExpatError as e:
                    if aux == True:
                        utils.tratar_xml_ilegivel(numero_da_nf, mensagem_xi, empresa, aux)
                   
                        # Circunstância indesejada:
                        # XML ilegível
                   
                        return robozinho()
                    else:
                        utils.tratar_xml_ilegivel(numero_da_nf, mensagem_xi, empresa)
                        return robozinho()
       
        # <DETALHES DO TRECHO/>
           

        # <DETALHES DO TRECHO>

        # O Código abaixo pode parecer um tanto confuso, mas ele é dessa maneira devido as muitas possibilidades de árvores XML
        # que podemos encontrar. O XML nada mais é do que um conjunto de chaves e valores, e chaves que
        # comportam mais chaves. Ele pode ter mais de um item, e tendo mais de um item,
        # a abordagem para extrair seus dados é uma (que segue a linha [const_item], que nada mais é do que acessar item por item
        # através de seu indice. Ex: 0, 1, 2...), enquanto quando há apenas um item no XML a abordagem é outra.

        # O XML da NF é transformado em um objeto, um dicionario Python, e como todo objeto, os valores são acessados através da chave.
   
        processador = extratorXML.ProcessadorXML(doc, empresa)
        valor_total_da_nf, filial_xml = processador.processar_totais_nota_fiscal()

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

        # <DETALHES DO TRECHO/>

        sleep(1)
        while True:
            utils.checar_failsafe()
            sleep(0.5)
            ptg.moveTo(150, 100)
            interagente.interagir_pagina_web(driver_microsiga, "#COMP6018", acao="Clicar")
            sleep(0.8)
            aparece_enter = utils.encontrar_imagem(r'src\Imagens\NCMIgnorar.png')
            if type(aparece_enter) == pyscreeze.Box:
                sleep(0.5)
                ptg.press("enter")
                utils.checar_failsafe()
            sleep(1)
            abriu_a_tela = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaAbriuDadosDaNota.png')
            if type(abriu_a_tela) == tuple:
                sleep(1.5)
                copy("408")
                ptg.hotkey("ctrl", "v", interval=0.5)
                break
        while True:
            ptg.press("tab", interval=0.7)
            ptg.hotkey("ctrl", "c", interval=0.5)
            filial_pedido = paste()
            if filial_pedido == filial_xml:
                utils.checar_failsafe()
                interagente.interagir_pagina_web(driver_microsiga, "#COMP7511", acao="Clicar")
                sleep(1)
                clicar_confirmar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoConfirmar.png')
                if type(clicar_confirmar) == tuple:
                    cont = 0
                    while cont < 5:
                        ptg.moveTo(150, 100)
                        interagente.interagir_pagina_web(driver_microsiga, "#COMP7511", acao="Clicar", limitar_retorno=True)
                        cont+=1
                break
            else:
                try:
                    utils.checar_failsafe()
                    interagente.interagir_pagina_web(driver_microsiga, "#COMP7512", acao="Clicar")
                    sleep(1)
                    clicar_cancelar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoCancelarDadosNF.png')
                    if type(clicar_cancelar) == tuple:
                        while type(clicar_cancelar) == tuple:
                            ptg.moveTo(150, 100)
                            interagente.interagir_pagina_web(driver_microsiga, "#COMP7512", acao="Clicar", limitar_retorno=True)
                            clicar_cancelar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoCancelarDadosNF.png')  
                    utils.cancelar1(actions)
                    utils.enviar_email(numero_da_nf, mensagem_pe, empresa)
               
                    # Circunstância indesejada:
                    # Filial do pedido não corresponde a filial de XML
               
                    return robozinho()
                except TypeError:
                    sleep(0.5)
                    interagente.interagir_pagina_web(driver_microsiga, "#COMP6017", acao="Clicar")
                    sleep(0.8)
                    aparece_enter = utils.encontrar_imagem(r'src\Imagens\NCMIgnorar.png')
                    if type(aparece_enter) == pyscreeze.Box:
                        sleep(0.5)
                        ptg.press("enter")
                        utils.checar_failsafe()

        try:
            sleep(0.5)
            utils.checar_failsafe()
            aparece_enter = utils.encontrar_imagem(r'src\Imagens\AtencaoEstoque.png')
            if type(aparece_enter) == pyscreeze.Box:
                sleep(0.3)
                ptg.press("enter")
            aparece_enter2 = utils.encontrar_imagem(r'src\Imagens\TES102.png')
            if type(aparece_enter2) == pyscreeze.Box:
                sleep(0.2)
                ptg.press("enter", interval=0.5)
                ptg.press(["tab"]*2, interval=0.5)
                sleep(0.2)
                ptg.write("102", interval=0.2)
                ptg.press(["tab"]*2, interval=0.5)
                sleep(0.2)
                ptg.press("enter")
                utils.checar_failsafe()
        finally:
            pass

   
        tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuOProcesso.png')
        cont = 0
        while type(tela_de_lancamento) != pyscreeze.Box:
            cont +=1
            tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuOProcesso.png')
            lancamento_retroativo = utils.encontrar_imagem(r'src\Imagens\LancamentoRetroativo.png')
            nota_ja_lancada = utils.encontrar_imagem(r'src\Imagens\ProcessoJaLancado.png')
            utils.checar_failsafe()
            if type(lancamento_retroativo) == pyscreeze.Box or type(nota_ja_lancada) == pyscreeze.Box:
                sleep(1)
                ptg.press("enter", interval=1)
                cont = 0

            tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuOProcesso.png')
            erro_esquisito = utils.encontrar_imagem(r'src\Imagens\ErroEsquisito2.png')
            if type(erro_esquisito) == pyscreeze.Box:
                sleep(1)
                utils.checar_failsafe()
                ptg.press("enter")
                utils.cancelar1(actions)

                # Circunstância indesejada:
                # Erro sistêmico na abertura do processo para lançamento.
           
                return robozinho()
       
            tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuOProcesso.png')
            erro_generico = utils.encontrar_imagem(r'src\Imagens\ErroGenerico.png')
            if type(erro_generico) == pyscreeze.Box:
                sleep(1)
                ptg.press("enter", interval=3)
                ptg.press("esc", interval=3)
                ptg.press("enter", interval=3)    
                utils.cancelar1(actions)
                utils.checar_failsafe()
                utils.enviar_email(numero_da_nf, mensagem_pb, empresa)
                return robozinho()
       
            tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaAbriuOProcesso.png')
            fornecedor_bloqueado = utils.encontrar_imagem(r'src\Imagens\FornecedorBloqueado.png')
            chave_nao_encontrada = utils.encontrar_imagem(r'src\Imagens\chaveNaoEncontradaNoSefaz.png')
            nf_cancelada = utils.encontrar_imagem(r'src\Imagens\NFCancelada.png')
            natureza_bloq = utils.encontrar_imagem(r'src\Imagens\NaturezaBloq.png')
            if type(chave_nao_encontrada) == pyscreeze.Box or type(natureza_bloq) == pyscreeze.Box or type(nf_cancelada) == pyscreeze.Box or type(fornecedor_bloqueado) == pyscreeze.Box:
                sleep(1)
                ptg.press("enter")
                utils.cancelar3(actions)
                utils.enviar_email(numero_da_nf, mensagem_pb, empresa)
                return robozinho()
            if cont == 15:
                ptg.press("enter")
                cont = 0

        sleep(0.5)
        if empresa == "EQS":
            utils.mover_seta(10, "tab", actions)
        else:
            utils.mover_seta(9, "tab", actions)
        sleep(1)
        utils.mover_seta(8, "Direita", actions)


        cancelar_lancamento = False
       
        for i, ctrl_imposto in enumerate(indices_e_impostos):

            verificador, item_fracionado = operadoresLancamento.verificar_valor_item(itens, i, actions)
            if verificador == True:
                utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
           
                # Circunstância indesejada:
                # Valor total do item não confere nem é passível de correção
           
                return robozinho()
           
            tratamento_item = tratamentoItem.TratadorItem(item_fracionado, itens, i, ctrl_imposto)
            item = tratamento_item.tratar_item()
            cont = 0

            match ctrl_imposto:
                case "Nenhum imposto":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, icmsST_no_item, ipi_no_item = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                       
                            # Circunstância indesejada:
                            # Natureza não mapeada pela automação
                       
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        if tes in ["102", "405", "433", "408", "436"]:
                            operadoresLancamento.zerar_imposto()
                        elif tes in ["406", "439", "421", "423", "438"]:
                            operadoresLancamento.zerar_imposto()
                            operadoresLancamento.zerar_imposto(passos_ida=12, passos_volta=13)
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)    
                                   
                case "Apenas o ICMS":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, bc_icms, aliq_icms, icmsST_no_item, ipi_no_item = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, bc_icms, aliq_icms, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        ptg.press(["left"]*9)
                        if tes in ["406", "439", "421", "423", "438"]:
                            operadoresLancamento.zerar_imposto(passos_ida=12, passos_volta=13)
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)
                                       
                case "Apenas o ICMSST":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        if tes in ["102", "405", "433", "408", "436"]:
                            operadoresLancamento.zerar_imposto()
                        elif tes in ["406", "439", "421", "423", "438"]:
                            operadoresLancamento.zerar_imposto()
                            operadoresLancamento.zerar_imposto(passos_ida=12, passos_volta=13)
                        cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, aliq_icms_ST, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)
                                       
                case "Apenas o IPI":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, icmsST_no_item, ipi_no_item, base_ipi, aliq_ipi = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        if tes in ["406", "439", "421", "438", "423", "102", "403", "434", "411", "437"]:
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
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item, base_ipi, aliq_ipi = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        if tes in ["406", "439", "421", "438", "423", "102", "411", "437"]:
                            operadoresLancamento.zerar_imposto()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, aliq_icms_ST, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, actions, passosIPI=0)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)
                                       
                case "Apenas ICMS e IPI":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, base_icms, aliq_icms, icmsST_no_item, ipi_no_item, base_ipi, aliq_ipi = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, base_icms, aliq_icms, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, actions, passosIPI=3)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)
                                   
                case "Apenas ICMS e ICMSST":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, base_icms, aliq_icms, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, base_icms, aliq_icms, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, aliq_icms_ST, actions, passosST=0)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)
                                       
                case "Todos os impostos":
                    for lista in item:
                        desc_no_item, frete_no_item, seg_no_item, desp_no_item, icms_no_item, base_icms, aliq_icms, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item, base_ipi, aliq_ipi = lista
                        natureza = operadoresLancamento.copiar_natureza()
                        codigo = operadoresLancamento.selecionar_caso(natureza)
                        tes = operadoresLancamento.definir_TES(actions, codigo, ctrl_imposto, empresa)
                        if tes == True:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.escrever_TES(tes, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_desconto(desc_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_frete(frete_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_seguro(seg_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_despesa(desp_no_item, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMS(icms_no_item, base_icms, aliq_icms, actions)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_ICMSST(icmsST_no_item, base_icms_ST, aliq_icms_ST, actions, passosST=0)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        cancelar_lancamento = operadoresLancamento.inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, actions, passosIPI=12)
                        if cancelar_lancamento:
                            utils.controlar_repeticao(controle_repeticao, chave_de_acesso, numero_da_nf, empresa, processos_ja_vistos)
                            return robozinho()
                        sleep(0.5)
                        if len(item) > 1:
                            ptg.press("down", interval=0.5)
                        cont+=1
                        operadoresLancamento.corrigir_passos_horizontal(cont, item)
                    if len(item) > 1:
                        ptg.press("up", interval=0.5)
                                       
            sleep(0.5)
            if len(indices_e_impostos) > 1:
                utils.mover_seta(1, "Baixo", actions)
            sleep(1.5)

        ptg.press("up", interval=0.5)
   
        aba_duplicatas = utils.encontrar_centro_imagem(r'src\Imagens\BotaoAbaDuplicatas.png')
        x, y =  aba_duplicatas
        ptg.click(x,y, clicks=4, interval=0.25)
        utils.checar_failsafe()
        sleep(1)
        lista_parc = []
        try:
            utils.clicar_valor_parcela()
            sleep(0.5)
            ptg.hotkey("ctrl", "c", interval=0.5)
            valor_parcela = paste()
            valor_parcela = utils.formatador4(valor_parcela)
        except:
            utils.clicar_valor_parcela()
            sleep(0.5)
            ptg.hotkey("ctrl", "c", interval=0.5)
            valor_parcela = paste()
            valor_parcela = utils.formatador4(valor_parcela)
        utils.checar_failsafe()

        # <DETALHES DO TRECHO>

        # Esse trecho faz a validação do valor das parcelas, aplicando correção caso necessário.
        # Ele verifica se o valor da primeira parcela corresponde ao valor total da NF,
        # em caso de correspondência ele dá sequência no roteiro de lançamento acionando a função utils.clicar_natureza_duplicata(),
        # caso contrário, ele tenta seguir um primeiro aparelho lógico para tratamento do caso.
        # Esse primeiro aparelho consiste em verificar se o valor da parcela copiada é maior ou menor que o valor total da NF,
        # e aplica um pequeno roteiro para cada caso. - Entenda que há muitas possibilidades de erro de informação no Microsiga
        # nesta etapa. O sistema tende a puxar a informação do pedido, mas às vezes este dado está errado,
        # ao mesmo tempo em que ele tenta puxar a informação do momento do lançamento. Sendo franco, é bem confuso a forma como
        # o sistema trata essa informação, por isso eu desenvolvi a sequencia lógica abaixo, para tratar essas incertezas -
        # Perceba que a todo momento está sendo verificado se o "ErroParcela" surge na tela. Dependendo do momento em que ele aparece,
        # ele servirá como um gatilho para executar o segundo aparelho lógico. Esse segundo aparelho consiste em buscar no Siga
        # a quantidade de parcelas para aquele processo, e então fazer a divisão por igual do valor total da NF. Esse aparelho é pouco
        # acionado, a maioria dos casos conseguem ser tratado pelo primeiro, mas, quando primeiro caso não resolve tem essa segunda
        # possibilidade. E se nenhum dos dois resolver ele cancela o lançamento e trata o caso como um "Processo Errado".

        if valor_parcela < valor_total_da_nf:
            lista_parc.append(valor_parcela)
            while round(sum(lista_parc),2) < valor_total_da_nf:
                utils.descer_copiar()
                erro_parcela = utils.encontrar_imagem(r'src\Imagens\ErroParcela.png')
                if type(erro_parcela) == pyscreeze.Box:
                    ptg.press("enter", interval=0.7)
                    ptg.press("enter", interval=0.7)
                    lista_parc = lista_parc[:-1]
                    valor_parc = valor_total_da_nf - round(sum(lista_parc),2)
                    valor_parc = utils.formatador2(valor_parc)
                    ptg.write(valor_parc, interval=0.03)
                    ptg.press("left")
                    lista_parc.append(float(valor_parc))
                else:
                    valor_parcela = paste()
                    valor_parcela = utils.formatador4(valor_parcela)
                    lista_parc.append(valor_parcela)
            somatoria = utils.formatador2(sum(lista_parc))
            somatoria = float(somatoria)
            parcela_errada = lista_parc[-1]
            if somatoria != valor_total_da_nf:
                if lista_parc[-1] == lista_parc[-2]:
                    parcela_errada = lista_parc.pop()
                    somatoria = utils.formatador2(sum(lista_parc))
                    somatoria = float(somatoria)
                diferenca_NF_siga = valor_total_da_nf - somatoria
                ultima_parcela = parcela_errada + diferenca_NF_siga
                ultima_parcela = "{:.2f}".format(ultima_parcela)
                ptg.press("enter", interval=1)
                ptg.write(ultima_parcela, interval=0.2)
                utils.checar_failsafe()
            sleep(1)

        elif valor_parcela > valor_total_da_nf:
            valor_total_da_nf = utils.formatador2(valor_total_da_nf)
            ptg.press("enter", interval=0.7)
            ptg.write(valor_total_da_nf)
            sleep(1)

        utils.clicar_natureza_duplicata()
        sleep(1)

        erro_parcela = utils.encontrar_imagem(r'src\Imagens\ErroParcela.png')
        if type(erro_parcela) == pyscreeze.Box:
            ptg.press("enter")
            utils.clicar_valor_parcela()
            utils.checar_failsafe()
            ptg.press(["left"]*2)
            sleep(0.3)
            ptg.hotkey("ctrl", "c", interval=0.1)
            primeira_parc = paste()
            ordem_parc = []
            ordem_parc.append(primeira_parc)

            if primeira_parc == '001':
                utils.descer_copiar()
                proxima_parcela = paste()
                ordem_parc.append(proxima_parcela)
                utils.checar_failsafe()
                if ordem_parc[-2] != ordem_parc[-1]:
                    while ordem_parc[-2] != ordem_parc[-1]:
                        utils.descer_copiar()
                        proxima_parcela = paste()
                        ordem_parc.append(proxima_parcela)
                    ordem_parc.pop()
                    valor_parcela = valor_total_da_nf / len(ordem_parc)
                    try:
                        valor_parcela = "{:.2f}".format(valor_parcela)
                    except ValueError:
                        utils.cancelar_lancamento()
                        processos_ja_vistos.remove(chave_de_acesso)
                        return robozinho()
                    utils.clicar_valor_parcela()
                    for vezes in range(len(ordem_parc)):
                        ptg.write(valor_parcela, interval=0.08)
                        ptg.press("left")
                        ptg.press("down", interval=0.8)
                    try:
                        valor_parcela = utils.formatador3(valor_parcela)
                    except ValueError:
                        utils.cancelar_lancamento()
                        processos_ja_vistos.remove(chave_de_acesso)
                        return robozinho()
                    valor_atingido = valor_parcela * len(ordem_parc)
                    utils.checar_failsafe()
                    sleep(2)
                    if valor_atingido != valor_total_da_nf:
                        diferenca_NF_siga = valor_atingido - valor_total_da_nf
                        valor_ultima_parcela = valor_parcela - diferenca_NF_siga
                        try:
                            valor_ultima_parcela = "{:.2f}".format(valor_ultima_parcela)
                        except ValueError:
                            utils.cancelar_lancamento()
                            processos_ja_vistos.remove(chave_de_acesso)
                            return robozinho()
                        ptg.write(valor_ultima_parcela, interval=0.08)
                        sleep(2)

        # <DETALHES DO TRECHO/>

            utils.clicar_natureza_duplicata()
            sleep(0.6)

            erro_parcela = utils.encontrar_imagem(r'src\Imagens\ErroParcela.png')
            if type(erro_parcela) == pyscreeze.Box:
                ptg.press("enter")
                utils.cancelar2(actions)
                utils.enviar_email(numero_da_nf, mensagem_pe, empresa)
                utils.checar_failsafe()
           
                # Circunstância indesejada:
                # Não foi possível corrigir o valor dos títulos
                # com a lógica estabelecida nessa automação
           
                return robozinho()
       
        ptg.hotkey("ctrl", "c", interval=0.3)

        natureza_perc = paste()
        if natureza_perc != "0,00":
            lista_perc = []
            aux = 0
            while round(sum(lista_perc),2) < 100.0:
                try:
                    natureza_perc = utils.formatador3(natureza_perc)
                except ValueError:
                    utils.cancelar_lancamento()
                    processos_ja_vistos.remove(chave_de_acesso)
                    return robozinho()
                lista_perc.append(natureza_perc)
                utils.descer_copiar()
                natureza_perc = paste()
                aux+=1
            maior_perc = max(lista_perc)
            for _ in range(aux):
                ptg.press("up", interval=0.3)
            ptg.press("right", interval=0.3)
            ptg.hotkey("ctrl", "c", interval=0.3)
            perc_majoritario = paste()
            utils.checar_failsafe()
            try:
                perc_majoritario = utils.formatador3(perc_majoritario)
            except ValueError:
                utils.cancelar_lancamento()
                processos_ja_vistos.remove(chave_de_acesso)
                return robozinho()
            while perc_majoritario != maior_perc:
                utils.descer_copiar()
                perc_majoritario = paste()
                try:
                    perc_majoritario = utils.formatador3(perc_majoritario)
                except ValueError:
                    utils.cancelar_lancamento()
                    processos_ja_vistos.remove(chave_de_acesso)
                    return robozinho()
            ptg.press("left",interval=0.3)
            ptg.hotkey("ctrl", "c", interval=0.3)
            natureza_duplicata = paste()
            ptg.hotkey(["shift", "tab"]*5, interval=0.2)
            ptg.write(natureza_duplicata, interval=0.2)
            ptg.press("tab", interval=1)
            utils.checar_failsafe()

        ptg.hotkey("ctrl", "s")
        sleep(2)
        utils.checar_failsafe()
        cont = 0
        while True:
            salvar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoSalvarLancamento.png')
            if type(salvar) == tuple:
                interagente.interagir_pagina_web(driver_microsiga, "#COMP9260", acao="Clicar", limitar_retorno=True)
                x, y = salvar
                ptg.click(x, y, interval=0.3)
                cont += 1
                sleep(1)
                if cont == 2:
                    break
            else:
                break

        erro_de_serie = utils.encontrar_imagem(r'src\Imagens\ErroDeSerie.png')
        erro_de_modelo = utils.encontrar_imagem(r'src\Imagens\ErroDeModulo.png')
        if type(erro_de_serie) == pyscreeze.Box or type(erro_de_modelo) == pyscreeze.Box:
            ptg.press("enter", interval=0.2)
            espec_doc = utils.encontrar_centro_imagem(r'src\Imagens\CampoESPEC.png')
            x, y = espec_doc
            sleep(0.5)
            ptg.click(x,y, clicks=2)
            ptg.write("NF", interval=0.1)
            ptg.press("enter", interval=0.5)
            utils.checar_failsafe()
            ptg.hotkey("ctrl", "s")
        erro_esquisito = utils.encontrar_imagem(r'src\Imagens\ErroEsquisito.png')
        if type(erro_esquisito) == pyscreeze.Box:
            ptg.press("esc")
            quit()
        erro_quantidade = utils.encontrar_imagem(r'src\Imagens\ErroDeQuantidade.png')
        if type(erro_quantidade) == pyscreeze.Box:
            ptg.press("enter")
            utils.cancelar_lancamento()
            mudar_a_selecao = utils.encontrar_centro_imagem(imagem=r'src\Imagens\ClicarMudarSelecao.png')
            x, y = mudar_a_selecao
            ptg.doubleClick(x, y)
            sleep(0.3)
            utils.enviar_email(numero_da_nf, mensagem_pe, empresa)
       
            # Circunstância indesejada:
            # Erro de quantidade no estoque da empresa
            # (Esse erro só pode ser ajustado pelos colaboradores do almoxarifado)
       
            return robozinho()


        while True:
            penultima_tela = utils.encontrar_centro_imagem(r'src\Imagens\PenultimoClique.png')
            if type(penultima_tela) == tuple:
                ptg.press("esc", interval=3)  
                penultima_tela = utils.encontrar_centro_imagem(r'src\Imagens\PenultimoClique.png')
                if type(penultima_tela) != tuple:
                    break     

        while True:
            ultima_tela = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaFinalizarLancamento.png')
            if type(ultima_tela) == tuple:
                ptg.press("tab", interval=1)
                ptg.press("enter", interval=1.5)  
                break
        
        while type(ultima_tela) == tuple:
            ultima_tela = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaFinalizarLancamento.png')
            if type(ultima_tela) == tuple:
                ptg.press("enter", interval=2.5)
            else:
                break

        
        utils.checar_failsafe()
                   
        aguarde = utils.encontrar_imagem_especifica(r'src\Imagens\ReferenciaAguarde.png')
        while type(aguarde) == pyscreeze.Box:
            sleep(0.5)
            aguarde = utils.encontrar_imagem_especifica(r'src\Imagens\ReferenciaAguarde.png')
                         

        mudar_a_selecao = utils.encontrar_centro_imagem(imagem=r'src\Imagens\ClicarMudarSelecao.png')
        try:
            x, y = mudar_a_selecao
            y = y + 17
            ptg.click(x,y, interval=0.4)
        except TypeError:
            ptg.click(300,300)

        sleep(1.5)

    while True:
        robozinho()
