from selenium.webdriver.common.action_chains import ActionChains
import pyautogui as ptg
from time import sleep
from pathlib import Path
import utils
import pyscreeze
import acaoComum


# Um dos dois módulos principais da automação. Este módulo é responsável por realizar o lançamento
# sequencial de RTs, por isso do nome "Corrente".
# Essa automação, que a primeira vista pode parecer confusa, tem um modo de funcionamento simples:
# Primeiro ela filtra a tela inicial para encontrar os processos pendentes, em seguida ela abre para lançar
# a RT de maior valor dentre as pendentes. Ao abrir a RT, ela filtrará os registros daquela RT seguindo a coluna
# "Status", buscando sempre os registros pendentes e pulando os lançados. Ao encontrar um registro pendente, ela
# verifica qual é o tipo de ação que deve ser tomada, tomando como referencia a informação presente na coluna "Status XML".
# É daí que a variável "controlador" é extraída. Com base nessa informação, a automação decide se deve
# lançar a NF, lançar o recibo, solicitar o XML, ou copiar a chave de acesso. Em cada uma dessas ações há muitos
# desdobramentos possíveis, por isso o script é tão extenso.


FAILSAFE = True
doc = ''

def inicializar_processo():

    interagente, driver_microsiga = acaoComum.inicializar_ERP()


    actions = ActionChains(driver_microsiga)

    def robozinho():
        """
        Função que realiza os primeiros passos da automação. Na tela inicial do IntAgillitas, 
        ela seleciona o filtro de pendentes para puxar somente as RTs que ainda não foram lançadas,
        depois ela clica na coluna valor para filtrar do maior para o menor. E então ela clica na primeira RT
        para realizar o lançamento, e chama a função "operar_lancamento", essa sim é responsável pelo lançamento do caixa.
        Função recursiva. A automação fica em loop até que não haja mais RTs pendentes para lançamento.
        """

        pular_processo = []                     
        controle_de_repeticao = []
        dono_da_rt = []
        chave_inconforme = []
        sem_xml = []
        rt_contador = []
        nf_ja_lancada = []
        cond_pag = []
        bloqueado = []
        cnpj_inconclusivo = []
        chave_sefaz =[]
        ncm_problematica = []


        sleep(0.5)
        while True:
            try:
                primeiro_clique = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCliqueInicial.png')
                x, y = primeiro_clique
            except TypeError:
                try:
                    primeiro_clique = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCliqueInicial2.png')
                    x, y = primeiro_clique
                except TypeError:
                    try:
                        primeiro_clique = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCliqueInicialSelecionado.png')
                        x, y = primeiro_clique
                    except TypeError:
                        sleep(0.5)
                        pass
            if type(primeiro_clique) == tuple:
                sleep(8)
                ptg.click(x, y, clicks=3, interval=0.2)
                break


        controle_acao = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaParaAcao.png')
        if type(controle_acao) != tuple:
            sleep(0.5)
            ptg.hotkey(["shift", "tab"]*4, interval=0.5)
            sleep(1)
            ptg.press("p", interval=1)
            botao_localizar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoLocalizar.png')
            x, y = botao_localizar
            ptg.click(x, y)
            

        acaoComum.proceder_primario()

        ptg.moveTo(150,100)
        _ = utils.esperar_aparecer(r'src\Imagens\ReferenciaStatusPendenteTelaInicial.png')

        sleep(0.5)

        _ = acaoComum.filtrar_status()
            
        def operar_lancamento(pular_processo):
            """
            Função que realiza o lançamento da RT que está aberta na tela. Seu modo de funcionamento é simples,
            dentre os muitos registros que aquela RT pode ter, ela verifica o status do registro imediato
            e toma uma ação baseada nesse status. São quatro possibilidades de ação, mas, primeiro, para que se entenda
            melhor, é preciso saber que cada RT pode ter dois tipos de registro: Recibo e Danfe. 
            Dentro de uma RT pode ter muitos recibos e muitas danfes, mas todas são apenas desses dois tipos. 
            Os recibos tem apenas um status, que é "NA-NÃO SE APLICA". Quando esse status é identificado pela automação
            através do valor armazenado na variável "controlador" extraído pela função "verificar_status", ela realiza o
            processo de lançamento para esse tipo de registro. Já as danfes tem cinco status possíveis: "NS-NÃO SOLITADO",
            "SL-SOLICITADATO-AGUARDANDO SEFAZ", esses dois primeiros indicam que a automação deve clicar no botão "Solicitar XML"
            para que o sistema SIGA faça a busca e a leitura do XML no SEFAZ; e então tem o status "NX-CHAVE DANFE NÃO DISPONÍVEL",
            esse status significa que, apesar do SIGA conseguir acessar a chave de acesso fornecida pela integração do Presteconta,
            de alguma forma ele não consegue vincular aquela chave a nenhum XML, seja porque a chave foi inserida erroneamente
            no Presteconta, ou, por qualquer outro motivo que desconheço. Então, a automação copia a chave de acesso através
            do botão "Corrigir Danfe" e, com a chave, a automação tenta buscar o seu XML no repositório de XMLs (a pasta xmlFiscalio)
            para inseri-lo manualmente no sistema através do botão "Solicitar XML" também.
            Caso a automação não encontre o XML, ou identifique que a chave não atende ao requisito de possuir 44 caracteres, ela
            adiciona o processo à lista de processos que devem ser pulados e que precisam ser mencionados no E-mail
            que será enviado para o setor Gestão de Caixas, informando que a RT não foi lançada por esse e/ou outros motivos.
            Tem também o status "NC-SEM CHAVE INFORMADA", que significa que a chave de acesso não foi inserida no Presteconta,
            e, finalmente, o status "DS-DISPONIVEL", que significa que o resgistro do tipo Danfe enfim está disponível para lançamento.
            Nesse ultimo caso, como é de se esperar, a automação clica no botão "Lancar Nota" e realiza o processo de lançamento.
            
            Essa automação conta com muitos recursos de controle. Por exemplo as variáveis pular_processo e controle_de_repeticao
            que servem para evitar que a automação tente lançar o mesmo registro que ela já tentou e já constatou que 
            por algum motivo não será possível lança-lo, ou então evitar que ela fique presa em um loop infinito tentando
            lançar um registro que já foi testado seu lançamento.
            """
            estado_do_caixa = False
            global doc

            controlador = acaoComum.verificar_status()

            if controlador == "Lançar recibo":
                estado_do_caixa = acaoComum.clicar_Lancar()
                cc_bloqueado = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaCCBloqueado.png')
                erro_cc = utils.encontrar_centro_imagem(r'src\Imagens\CCNaoSintetico.png')
                aguarde = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde2.png')
                while type(aguarde) == tuple:
                    aguarde = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde2.png')
                if type(cc_bloqueado) == tuple or type(erro_cc) == tuple:
                    ptg.press("enter", interval=0.5)
                    if type(erro_cc) == tuple:
                        acaoComum.rejeitar_caixa(mensagem="Centro de Custo não é sintético.")
                    else:
                        acaoComum.rejeitar_caixa()

                    # Circuntância indesejada:
                    # Se o CC estiver bloqueado, a automação não poderá prosseguir com o lançamento da RT.

                    return robozinho()
                
                repentina_etapa_final = utils.encontrar_imagem(r'src\Imagens\ReferenciaFinalPorLancamento.png')

                if type(repentina_etapa_final) == pyscreeze.Box:
                    utils.tratar_etapa_final()

                if estado_do_caixa == "NF já lançada":
                    controle_de_repeticao.append(chave_de_acesso)
                    pular_processo.append(chave_de_acesso)
                    clique_negar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoNao.png')
                    x, y = clique_negar
                    ptg.doubleClick(x, y, interval=0.7)
                    if not rt_contador:
                        autor_da_rt, rt = acaoComum.copiar_RT()
                        dono_da_rt.append(autor_da_rt)
                        rt_contador.append(rt)
                    nf_ja_lancada.append(rt_contador[0])
                    acaoComum.pular_processo()
                    return operar_lancamento(pular_processo)
                
                elif estado_do_caixa == True:
                    x, y = utils.clicar_finalizar()
                    finalizar, ainda_tem_processo_pendente = acaoComum.insistir_ate_encontrar(x, y)

                    if type(ainda_tem_processo_pendente) == tuple:
                        utils.tratar_processos_pendentes()
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        
                        # O registro imediato para lançamento é um recibo, mas, por algum motivo, não deu para lançar todos
                        # os registros dessa RT, ao mesmo tempo, não há mais nenhum registro que a automação consiga lançar.
                        # Nesse caso, ela sai da RT, deixa ela com status de lançada parcialmente, e usa da recursividade para
                        # iniciar o próximo processo.
                        
                        return robozinho()
                    
                    if type(finalizar) == tuple:
                        ptg.press("enter")
                    utils.aguardar()
                    utils.clicar_botao_sair()
                    if rt_contador:
                        utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                    return robozinho()
                
                else:
                    estado_do_caixa = acaoComum.filtrar_status()

                    if estado_do_caixa == "FINALIZADO":
                        x, y = utils.clicar_finalizar()
                        finalizar, ainda_tem_processo_pendente = acaoComum.insistir_ate_encontrar(x, y)

                        if type(ainda_tem_processo_pendente) == tuple:
                            utils.tratar_processos_pendentes()
                            if rt_contador:
                                utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                            return robozinho()
                        
                        if type(finalizar) == tuple:
                            ptg.press("enter")
                        utils.aguardar()
                        utils.clicar_botao_sair()
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        return robozinho()
                    
                    controle_de_repeticao.clear()
                    return operar_lancamento(pular_processo)
                

            elif controlador == "Clicar em Solicitar XML":
                status_nf, inserir_xml = acaoComum.solicitar_XML()

                if type(status_nf) == tuple:
                    try:
                        numero_nf = chave_de_acesso[25:34]
                    except UnboundLocalError:
                        chave_de_acesso, processo_feito_errado = acaoComum.copiar_chave_acesso()
                        numero_nf = chave_de_acesso[25:34]
                    acaoComum.rejeitar_caixa(mensagem = f"NF {numero_nf} foi cancelada pelo fornecedor.")
                    
                    # Circunstância indesejada:
                    # Se a NF foi cancelada pelo fornecedor, a automação não poderá prosseguir com o lançamento da RT.
                    # É necessário rejeitar o caixa para que o setor Gestão de Caixas avalie o caso.

                    return robozinho()
                
                if type(inserir_xml) == tuple:
                    chave_de_acesso, processo_feito_errado = acaoComum.copiar_chave_acesso()
                    x, y = utils.clicar_2x(r'src\Imagens\BotaoSolicitarXML.png')

                    while True:
                        aguardando = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
                        falsa_duplicidade = utils.encontrar_centro_imagem(r'src\Imagens\ErroPossivelDuplicidade.png')
                        xml_manual = utils.encontrar_centro_imagem(r'src\Imagens\ReferenciaXMLAindaNaoSolicitado3.png')
                        if type(aguardando) == tuple:
                            while type(aguardando) == tuple:
                                aguardando = utils.encontrar_centro_imagem(r'src\Imagens\TelaDeAguarde1.png')
                        elif type(falsa_duplicidade) == tuple or type(xml_manual) == tuple:
                            try:
                                verificador = pular_processo.index(chave_de_acesso)
                                try:
                                    verificador = controle_de_repeticao.index(chave_de_acesso)
                                    utils.mover_seta(7, "tab", actions)
                                    sleep(1)
                                    ptg.press("enter", interval=1)
                                    utils.repetir_botao()
                                    clique_status = utils.esperar_aparecer(r'src\Imagens\ReferenciaStatus.png')  
                                    x, y = clique_status
                                    ptg.click(x, y)
                                    sleep(0.7)
                                    ptg.press("down")
                                    ptg.click(x, y)
                                    if rt_contador:
                                        utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                                    
                                    # Esses casos de "try - except" são onde a automação tenta verificar se o registro imediato
                                    # já foi testado para lançamento. Se já tiver sido testado, a automação também precisa pular o processo,
                                    # além de ter um controle de repetição, para evitar ficar presa testando o mesmo registro infinitamente.
                                    # Isso pode acontecer quando a RT que está sendo lançada possui apenas um registro, ou, 
                                    # o ultimo registro pendente de lançamento é justamente um registro que apresenta algum erro
                                    # impeditivo.
                                    
                                    return robozinho()
                                
                                except ValueError:
                                    ptg.press("right", interval=0.05)
                                    ptg.press("enter")
                                    acaoComum.pular_processo()
                                    
                                    # Para o caso do segundo "try" capturar uma exceção no trecho "verificador = controle_de_repeticao.index(chave_de_acesso)"
                                    # a automação precisa pular o registro e adiciona-lo à lista de controle de repetição, justamente para evitar o que 
                                    # foi explicado no comentário anterior. Essa dinâmica se repete em outros trechos do código.

                                    controle_de_repeticao.append(chave_de_acesso)
                                    return operar_lancamento(pular_processo)
                                
                            except ValueError:
                                # Aqui está o fluxo natural do script. Quando o registro não precisa ser pulado, mas sim lançado.
                                caminho = "C:\\Users\\User\\OneDrive - EQS Engenharia Ltda\\Área de Trabalho\\Mariquinha\\xmlFiscalio\\" + chave_de_acesso + ".xml"
                                path = Path(caminho)

                                if not path.exists():
                                    ptg.press("right", interval=0.05)
                                    ptg.press("enter")
                                    pular_processo.append(chave_de_acesso)
                                    controle_de_repeticao.append(chave_de_acesso)
                                    if not rt_contador:
                                        autor_da_rt, rt = acaoComum.copiar_RT()
                                        dono_da_rt.append(autor_da_rt)
                                        rt_contador.append(rt)
                                    acaoComum.pular_processo()
                                    sem_xml.append(rt_contador[0])

                                    # Circunstância indesejada:
                                    # Quando não temos o xml da NF salvo na pasta repositório "xmlFiscalio".

                                    return operar_lancamento(pular_processo)
                                
                            ptg.press("enter", interval=0.5)
                            
                            acaoComum.importar_xml(caminho, driver_microsiga)

                            erro_de_xml = utils.encontrar_imagem(r'src\Imagens\ErroNaImportacaoDoXML.png')
                            if type(erro_de_xml) == pyscreeze.Box:
                                ptg.press("enter")
                                pular_processo.append(chave_de_acesso)
                                controle_de_repeticao.append(chave_de_acesso)
                                if not rt_contador:
                                    autor_da_rt, rt = acaoComum.copiar_RT()
                                    dono_da_rt.append(autor_da_rt)
                                    rt_contador.append(rt)
                                acaoComum.pular_processo()
                                sem_xml.append(rt_contador[0])
                                return operar_lancamento(pular_processo)
                            
                            estado_do_caixa = acaoComum.filtrar_status()
                            return operar_lancamento(pular_processo)
                        
                        else:
                            ptg.doubleClick(x,y)
                            break

                estado_do_caixa = acaoComum.filtrar_status()
                return operar_lancamento(pular_processo)
            

            elif controlador == "Copie a chave de acesso 1" or controlador == "Copie a chave de acesso 2":
                chave_de_acesso, processo_feito_errado = acaoComum.copiar_chave_acesso()

                if processo_feito_errado == True or controlador == "Copie a chave de acesso 2":
                    try:
                        verificador = controle_de_repeticao.index(chave_de_acesso)
                    except ValueError:
                        controle_de_repeticao.append(chave_de_acesso)
                        
                        # Circunstância indesejada:
                        # Quando a chave de acesso é desconforme.
                        
                        if not rt_contador:
                            autor_da_rt, rt = acaoComum.copiar_RT()
                            dono_da_rt.append(autor_da_rt)
                            rt_contador.append(rt)
                        try:
                            verificador = pular_processo.index(chave_de_acesso)
                        except ValueError:
                            chave_inconforme.append(rt_contador[0])
                        pular_processo.append(chave_de_acesso)
                        acaoComum.pular_processo()
                        return operar_lancamento(pular_processo)
                
                try:
                    verificador = pular_processo.index(chave_de_acesso)
                    try:
                        verificador = controle_de_repeticao.index(chave_de_acesso)
                        utils.mover_seta(7, "tab", actions)
                        sleep(1)
                        ptg.press("enter", interval=1)
                        utils.repetir_botao()
                        clique_status = utils.esperar_aparecer(r'src\Imagens\ReferenciaStatus.png')  
                        x, y = clique_status
                        ptg.click(x, y)
                        sleep(0.7)
                        ptg.press("down")
                        ptg.click(x, y)
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        return robozinho()
                    
                    except ValueError:
                        acaoComum.pular_processo()
                        controle_de_repeticao.append(chave_de_acesso)
                        return operar_lancamento(pular_processo)
                    
                except ValueError:
                    caminho = "C:\\Users\\User\\OneDrive - EQS Engenharia Ltda\\Área de Trabalho\\Mariquinha\\xmlFiscalio\\" + chave_de_acesso + ".xml"
                    path = Path(caminho)

                    if not path.exists():
                        pular_processo.append(chave_de_acesso)
                        controle_de_repeticao.append(chave_de_acesso)
                        if not rt_contador:
                            autor_da_rt, rt = acaoComum.copiar_RT()
                            dono_da_rt.append(autor_da_rt)
                            rt_contador.append(rt)
                        acaoComum.pular_processo()
                        sem_xml.append(rt_contador[0])
                        return operar_lancamento(pular_processo)
                    
                    x, y = utils.clicar_2x(r'src\Imagens\BotaoSolicitarXML.png')

                    while True:
                        solicitar_xml = utils.encontrar_imagem(r'src\Imagens\ReferenciaXMLAindaNaoSolicitado.png')
                        solicitar_xml2 = utils.encontrar_imagem(r'src\Imagens\ReferenciaXMLAindaNaoSolicitado2.png')
                        if type(solicitar_xml) == pyscreeze.Box or type(solicitar_xml2) == pyscreeze.Box:
                            break

                    ptg.press("enter", interval=0.5)

                    acaoComum.importar_xml(caminho, driver_microsiga)

                    erro_de_xml = utils.encontrar_imagem(r'src\Imagens\ErroNaImportacaoDoXML.png')
                    if type(erro_de_xml) == pyscreeze.Box:
                        ptg.press("enter")
                        pular_processo.append(chave_de_acesso)
                        controle_de_repeticao.append(chave_de_acesso)
                        if not rt_contador:
                            autor_da_rt, rt = acaoComum.copiar_RT()
                            dono_da_rt.append(autor_da_rt)
                            rt_contador.append(rt)
                        acaoComum.pular_processo()
                        sem_xml.append(rt_contador[0])
                        return operar_lancamento(pular_processo)
                    
                    estado_do_caixa = acaoComum.filtrar_status()
                    return operar_lancamento(pular_processo)
                
            else:
                # controlador == "Lançar DANFE":
                chave_de_acesso, processo_feito_errado = acaoComum.copiar_chave_acesso()
                estado_do_caixa = chave_de_acesso

                if estado_do_caixa == True:
                    x, y = utils.clicar_finalizar()
                    finalizar, ainda_tem_processo_pendente = acaoComum.insistir_ate_encontrar(x, y)

                    if type(ainda_tem_processo_pendente) == tuple:
                        utils.tratar_processos_pendentes()
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        return robozinho()
                    
                    if type(finalizar) == tuple:
                        ptg.press("enter")
                    utils.aguardar()
                    utils.clicar_botao_sair()
                    if rt_contador:
                        utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                    return robozinho()
                
                try:
                    verificador = pular_processo.index(chave_de_acesso)
                    try:
                        verificador = controle_de_repeticao.index(chave_de_acesso)
                        utils.mover_seta(7, "tab", actions)
                        sleep(2)
                        ptg.press("enter", interval=1)
                        utils.repetir_botao()
                        clique_status = utils.esperar_aparecer(r'src\Imagens\ReferenciaStatus.png')  
                        x, y = clique_status
                        ptg.click(x, y)
                        sleep(0.7)
                        ptg.press("down", interval=0.4)
                        ptg.click(x, y)
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        return robozinho()
                    
                    except ValueError:
                        acaoComum.pular_processo()
                        controle_de_repeticao.append(chave_de_acesso)
                        return operar_lancamento(pular_processo)
                    
                except ValueError:
                    caminho = "C:\\Users\\User\\OneDrive - EQS Engenharia Ltda\\Área de Trabalho\\Mariquinha\\xmlFiscalio\\" + chave_de_acesso + ".xml"
                    path = Path(caminho)
                    
                    if not path.exists():
                        pular_processo.append(chave_de_acesso)
                        controle_de_repeticao.append(chave_de_acesso)
                        if not rt_contador:
                            autor_da_rt, rt = acaoComum.copiar_RT()
                            dono_da_rt.append(autor_da_rt)
                            rt_contador.append(rt)
                        acaoComum.pular_processo()
                        sem_xml.append(rt_contador[0])
                        return operar_lancamento(pular_processo)
                    
                estado_do_caixa = acaoComum.clicar_Lancar()
                if estado_do_caixa == "NF já lançada":
                    controle_de_repeticao.append(chave_de_acesso)
                    pular_processo.append(chave_de_acesso)
                    clique_negar = utils.encontrar_centro_imagem(r'src\Imagens\BotaoNao.png')
                    x, y = clique_negar
                    ptg.doubleClick(x, y, interval=0.7)
                    if not rt_contador:
                        autor_da_rt, rt = acaoComum.copiar_RT()
                        dono_da_rt.append(autor_da_rt)
                        rt_contador.append(rt)
                    nf_ja_lancada.append(rt_contador[0])
                    acaoComum.pular_processo()
                    return operar_lancamento(pular_processo)
                    
                elif estado_do_caixa == True:
                    x, y = utils.clicar_finalizar()
                    finalizar, ainda_tem_processo_pendente = acaoComum.insistir_ate_encontrar(x, y)

                    if type(ainda_tem_processo_pendente) == tuple:
                        utils.tratar_processos_pendentes()
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        return robozinho()
                    
                    if type(finalizar) == tuple:
                        ptg.press("enter", interval=0.4)
                    utils.aguardar()
                    utils.clicar_botao_sair()
                    if rt_contador:
                        utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                    return robozinho()
                
                else:
                    nome_fantasia_forn, itens, indices_e_impostos = acaoComum.extrair_dados_XML(caminho)

                    tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaDocumentoEntrada.png')
                    while type(tela_de_lancamento) != pyscreeze.Box:

                        acaoComum.verificar_cadastro_forn(nome_fantasia_forn, actions)

                        tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaDocumentoEntrada.png')
                        utils.lancar_retroativo()

                        tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaDocumentoEntrada.png')
                        tela_bloqueio = utils.encontrar_imagem(r'src\Imagens\ReferenciaBloqueioGenerico.png')
                        if type(tela_bloqueio) == pyscreeze.Box:
                            pular_processo.append(chave_de_acesso)
                            controle_de_repeticao.append(chave_de_acesso)
                            ptg.press("enter", interval=1)
                            utils.aguardar1()
                            cc_bloqueado = utils.encontrar_imagem(r'src\Imagens\ReferenciaCCBloqueado.png')
                            erro_cc = utils.encontrar_centro_imagem(r'src\Imagens\CCNaoSintetico.png')
                            if type(cc_bloqueado) == tuple or type(erro_cc) == tuple:
                                ptg.press("enter", interval=0.5)
                                if type(erro_cc) == tuple:
                                    acaoComum.rejeitar_caixa(mensagem="Centro de Custo não é sintético.")
                                else:
                                    acaoComum.rejeitar_caixa()
                                return robozinho()
                            prod_bloq = utils.encontrar_centro_imagem(r'src\Imagens\ErroProdutoBloqueado.png')
                            erro_condicao_pag = utils.encontrar_centro_imagem(r'src\Imagens\ErroCondicaoDePagamento.png')
                            if type(prod_bloq) == tuple or type(erro_condicao_pag) == tuple:
                                ptg.press("enter", interval=0.5)
                                if not rt_contador:
                                    autor_da_rt, rt = acaoComum.copiar_RT()
                                    dono_da_rt.append(autor_da_rt)
                                    rt_contador.append(rt)
                            if type(erro_condicao_pag) == tuple:
                                cond_pag.append(rt_contador[0])
                                
                                # Circunstância indesejada:
                                # Quando o SIGA acusa erro na condição de pagamento do registro que está sendo lançado.

                            elif type(prod_bloq) == tuple:
                                bloqueado.append(rt_contador[0])
                                
                                # Circunstância indesejada:
                                # Quando o SIGA acusa que o código de um dos produtos está bloqueado.

                            acaoComum.pular_processo()
                            return operar_lancamento(pular_processo)

                        erro_cnpj = utils.encontrar_centro_imagem(r'src\Imagens\ErroEsquisito.png')
                        if type(erro_cnpj) == tuple:
                            ptg.press("enter", interval=1)
                            utils.aguardar1()

                        tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaDocumentoEntrada.png')
                        erro_sefaz = utils.encontrar_imagem(r'src\Imagens\ErroNFNaoEncontradaNoSefaz.png')
                        chave_divergente = utils.encontrar_imagem(r'src\Imagens\ChaveNaoConfereNF.png')
                        if type(erro_sefaz) == pyscreeze.Box or type(chave_divergente) == pyscreeze.Box:
                            pular_processo.append(chave_de_acesso)
                            controle_de_repeticao.append(chave_de_acesso)
                            ptg.press("enter", interval=0.5)
                            _ = utils.esperar_aparecer(r'src\Imagens\ReferenciaBloqueioGenerico.png')
                            ptg.press("enter", interval=1)
                            utils.aguardar1()
                            erro_condicao_pag = utils.encontrar_centro_imagem(r'src\Imagens\ErroCondicaoDePagamento.png')
                            if type(erro_condicao_pag) == tuple:
                                ptg.press("enter", interval=0.5)
                            erro_generico = utils.encontrar_centro_imagem(r'src\Imagens\ErroGenerico.png')   
                            if type(erro_generico) == tuple:
                                ptg.press("enter", interval=0.5)
                            if not rt_contador:
                                autor_da_rt, rt = acaoComum.copiar_RT()
                                dono_da_rt.append(autor_da_rt)
                                rt_contador.append(rt)
                            acaoComum.pular_processo()
                            if type(erro_cnpj) == tuple:
                                cnpj_inconclusivo.append(rt_contador[0])
                                
                                # Circunstância indesejada:
                                # Quando o SIGA acusa erro de CNPJ em branco.
                            
                            elif type(erro_condicao_pag) == tuple:
                                cond_pag.append(rt_contador[0])
                            else:
                                chave_sefaz.append(rt_contador[0])
                                
                                # Circunstância indesejada:
                                # Quando o SIGA acusa erro chave de acesso vinculada ao processo não confere com a NFE
                                # que está sendo digitada.
                            
                            return operar_lancamento(pular_processo)

                        tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaDocumentoEntrada.png')
                        erro_ncm = utils.encontrar_centro_imagem(r'src\Imagens\ErroNCM.png')
                        if type(erro_ncm) == tuple:
                            pular_processo.append(chave_de_acesso)
                            controle_de_repeticao.append(chave_de_acesso)
                            ptg.press("esc", interval=0.7)
                            if not rt_contador:
                                autor_da_rt, rt = acaoComum.copiar_RT()
                                dono_da_rt.append(autor_da_rt)
                                rt_contador.append(rt)
                            acaoComum.pular_processo()
                            ncm_problematica.append(rt_contador[0])

                            # Circunstância indesejada:
                            # Quando o SIGA acusa erro no NCM de um dos produtos do registro que está sendo lançado.

                            return operar_lancamento(pular_processo)
                        
                        tela_de_lancamento = utils.encontrar_imagem(r'src\Imagens\ReferenciaDocumentoEntrada.png')
                        

                    sleep(0.5)
                    utils.mover_seta(10, "tab", actions)
                    sleep(1)
                    utils.mover_seta(8, "Direita", actions)

                    cancelar_lancamento = False
                    cancelar_lancamento = acaoComum.inserir_valores_da_NF_no_siga(indices_e_impostos, itens, actions)
                    if cancelar_lancamento:
                        try:
                            pular_processo.remove(chave_de_acesso)
                            controle_de_repeticao.remove(chave_de_acesso)
                        except ValueError:
                            pass
                        return operar_lancamento(pular_processo)
                    
                    ptg.press("up", interval=0.5)

                    acaoComum.finalizar_lancamento()

                
                    estado_do_caixa = acaoComum.filtrar_status()

                    if estado_do_caixa == "FINALIZADO":
                        x, y = utils.clicar_finalizar()
                        finalizar, ainda_tem_processo_pendente = acaoComum.insistir_ate_encontrar(x, y)

                        if type(ainda_tem_processo_pendente) == tuple:
                            utils.tratar_processos_pendentes()
                            if rt_contador:
                                utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                            return robozinho()
                        
                        if type(finalizar) == tuple:
                            ptg.press("enter")
                        utils.aguardar()
                        utils.clicar_botao_sair()
                        if rt_contador:
                            utils.enviar_email(rt_contador, dono_da_rt, sem_xml, chave_inconforme, nf_ja_lancada, cond_pag, bloqueado, cnpj_inconclusivo, chave_sefaz, ncm_problematica)
                        return robozinho()
        
                    controle_de_repeticao.clear()
                    return operar_lancamento(pular_processo)

        operar_lancamento(pular_processo)
        sleep(1)


    while True:
        robozinho()
        sleep(1)