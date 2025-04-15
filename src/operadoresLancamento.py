from pyautogui import hotkey, press, write, FAILSAFE
from pyperclip import paste
from time import sleep
import pyscreeze
import utils
 
 
# Módulo fornecedor de funções utilitárias para validação, correção, ou inserção de dados
# no momento de lançamento da NF na rotina Documento Entrada.
# Nesse momento é onde confrontamos os dados da NF com os dados passados no pedido criado pelo comprador,
# além de inserirmos dados no processo, como a TES.
 
 
FAILSAFE = True
 
def escrever_valor_unit(valor_unit_convertido, passos=6):
    """
    Função auxiliar à função verificar_valor_item. Ela escreve o valor unitário de um item no sistema SIGA,
    após mover o cursor para a posição correta.
    """
    press(["right"]*passos)
    valor_unit_convertido = utils.formatador(valor_unit_convertido, casas_decimais="{:.6f}")
    sleep(0.5)
    write(valor_unit_convertido, interval=0.5)
    sleep(0.3)
    press(["right"]*3)
    utils.checar_failsafe()
 
 
 
def contar_item_fracionado(quantidade_siga, valor_unit, quantidade_real, actions):
    """
    Função auxiliar à função verificar_valor_item. Serve para lidar com itens fracionados no sistema SIGA.
    Verifica se a quantidade total de um item fracionado no SIGA corresponde à quantidade real da nota fiscal (NF).
    Se a quantidade estiver dividida em múltiplas linhas, a função soma as quantidades e ajusta os valores unitários.
    * Veja o módulo tratamentoItem *.
 
    :param quantidade_siga: Quantidade do item no SIGA.
    :param valor_unit: Valor unitário do item.
    :param quantidade_real: Quantidade real do item na nota fiscal.
 
    :return: Uma tupla contendo uma lista de razões (proporções das quantidades fracionadas) e um booleano
             que indica se o lançamento deve ser cancelado (True se houver discrepância, False caso contrário).
    """
    cancelar_lancamento = False
    razoes = []
    valor_unit = utils.formatador(valor_unit, casas_decimais="{:.6f}")
    cont = 0
    quantidade_total = []
    quantidade_total.append(quantidade_siga)
    press("left", interval=0.5)
    hotkey("ctrl", "c", interval=0.5)
    cod_item = paste()
    utils.checar_failsafe()
    try:
        while sum(quantidade_total) < quantidade_real:
            press("down")
            sleep(0.5)
            hotkey("ctrl", "c", interval=0.8)
            item_dividido = paste()
            cont+=1
            if item_dividido == cod_item:
                press(["right"]*6)
                sleep(0.6)
                hotkey("ctrl", "c", interval=0.8)
                qtd_dividida = paste()
                qtd_dividida = utils.formatador4(qtd_dividida)
                quantidade_total.append(qtd_dividida)
                press("right", interval=0.3)
                write(valor_unit, interval=0.5)
                press(["left"]*8)
                sleep(0.5)
                utils.checar_failsafe()        
            else:
                break
    except TypeError:
        pass
    if len(quantidade_total) > 10:
        press(["up"]*cont, interval=20)
    else:
        press(["up"]*cont, interval=0.6)
    sleep(0.8)
    press(["right"]*7)
    sleep(0.5)
    write(valor_unit, interval=0.5)
    utils.checar_failsafe()
    try:
        if sum(quantidade_total) != quantidade_real:
            cancelar_lancamento = True
            utils.cancelar2(actions)
        else:
            for qtd in quantidade_total:
                razao = qtd / quantidade_real
                razoes.append(razao)
            press(["right"]*3)
        utils.checar_failsafe()
    except TypeError:
        cancelar_lancamento = True
        utils.cancelar2(actions)
        utils.checar_failsafe(actions)
    return razoes, cancelar_lancamento
 
 
 
def verificar_valor_item(lista, indiceX, actions):
    """
    Verifica se o valor do item no SIGA corresponde ao valor do item na nota fiscal (NF).
    Se não corresponder, tenta corrigir o valor unitário.
 
    :param lista: Lista contendo os valores dos itens da NF.
    :param indiceX: Índice do item atual na lista.
 
    :return: Uma tupla contendo um booleano (se o lançamento deve ser cancelado) e uma lista de razões (quant. do item na linha / quantidade total do item na NF)
             para correção caso o item seja fracionado.
             * Veja o módulo tratamentoItem *.
             Aqui também temos uma regra de negócio sendo aplicada: alguns itens
             específicos passam por uma conversão de unidade de medida no pedido. Para que o programa saiba lidar com esses itens,
             eles foram mapeados e inseridos no código afim de aplicar a devida tratativa para cada caso.
    """
    razoes = []
    sleep(0.7)
    cancelar_lancamento = False
    utils.mover_seta(4, "Direita", actions)
    sleep(0.7)
    hotkey("ctrl", "c", interval=0.7)
    utils.checar_failsafe()
    valor_do_item_no_siga = paste()
    valor_do_item_no_siga = utils.formatador4(valor_do_item_no_siga)
    valor_do_item_na_NF = lista[indiceX][0]
    valor_do_item_na_NF = utils.formatador3(valor_do_item_na_NF)
    if valor_do_item_no_siga != valor_do_item_na_NF:
        write(lista[indiceX][0], interval=0.5)
        sleep(1)
        #press("enter", interval=1.5)
        encontrar = utils.encontrar_imagem(r'src\Imagens\ValItemErrado.png')
        utils.checar_failsafe()
        if type(encontrar) == pyscreeze.Box:
            press("enter", interval=1)
            encontrar = utils.encontrar_imagem(r'src\Imagens\ValItemErrado.png')
            utils.checar_failsafe()
            if type(encontrar) == pyscreeze.Box:
                press("enter", interval=1)
            press("esc", interval=0.5)
            press(["left"]*5)
            sleep(0.5)
            hotkey("ctrl", "c", interval=0.5)
            utils.checar_failsafe()
            quantidade_siga = paste()
            quantidade_siga = utils.formatador4(quantidade_siga)
            quantidade_NF = lista[indiceX][1]
            quantidade_NF = utils.formatador3(quantidade_NF)
            valor_unit_NF = lista[indiceX][2]
            valor_unit_NF = utils.formatador3(valor_unit_NF)
            if quantidade_siga == quantidade_NF:
                escrever_valor_unit(valor_unit_NF, passos=1)
                utils.checar_failsafe()
            else:
                press(["left"]*5)
                sleep(0.5)
                hotkey("ctrl", "c", interval=0.5)
                utils.checar_failsafe()
                desc_prod = paste().lower()
                if "abracadeira" in desc_prod:
                    quantidade_convertida = quantidade_NF * 100
                    valor_unit_convertido = valor_unit_NF / 100
                    if quantidade_convertida == quantidade_siga:
                        escrever_valor_unit(valor_unit_convertido)
                        utils.checar_failsafe()
                    else:
                        razoes, cancelar_lancamento = contar_item_fracionado(quantidade_siga, valor_unit_convertido, quantidade_convertida, actions)
                elif "pilha" in desc_prod or "tubo isolante" in desc_prod:
                    quantidade_convertida = quantidade_NF * 2
                    valor_unit_convertido = valor_unit_NF / 2
                    if quantidade_convertida == quantidade_siga:
                        escrever_valor_unit(valor_unit_convertido)
                        utils.checar_failsafe()
                    else:
                        razoes, cancelar_lancamento = contar_item_fracionado(quantidade_siga, valor_unit_convertido, quantidade_convertida, actions)
                elif "gas" in desc_prod:
                    press("left", interval=0.5)
                    hotkey("ctrl", "c", interval=0.5)
                    cod_do_item = paste()
                    press("right", interval=0.3)
                    utils.checar_failsafe()
                    if cod_do_item == "0651000053":
                        razoes, cancelar_lancamento = contar_item_fracionado(quantidade_siga, valor_unit_NF, quantidade_NF, actions)
                    else:
                        valor_unit_convertido = valor_do_item_na_NF / quantidade_siga
                        escrever_valor_unit(valor_unit_convertido)
                        utils.checar_failsafe()
                elif "pedrisco" in desc_prod or "cabo" in desc_prod[:4] or "manta" in desc_prod or "lona" in desc_prod:
                    valor_unit_convertido = valor_do_item_na_NF / quantidade_siga
                    escrever_valor_unit(valor_unit_convertido)
                    utils.checar_failsafe()
                else:
                    razoes, cancelar_lancamento = contar_item_fracionado(quantidade_siga, valor_unit_NF, quantidade_NF, actions)
        else:
            press("left", interval=0.3)
        utils.checar_failsafe()
    return cancelar_lancamento, razoes
 
 
def copiar_natureza():
    """
    Copia a natureza do item no SIGA e a corrige, se necessário.
 
    :return: A natureza.
    """
    press("right", interval=0.7)
    hotkey("ctrl", "c", interval=0.7)
    natureza = paste()
    if natureza == "2020081":
        natureza = "2050006"
        utils.escrever_natureza(natureza)
    elif natureza == "2020060":
        natureza = "2050004"
        utils.escrever_natureza(natureza)
    elif natureza in ["2020082", "2020083"]:
        natureza = "2050008"
        utils.escrever_natureza(natureza)
    utils.checar_failsafe()
    sleep(1)
    return natureza
 
 
def selecionar_caso(natureza):
    """
    Seleciona o caso de lançamento com base na natureza do item.
 
    :param natureza: Natureza do item.
    :return: Código do caso de lançamento.
    """
    codigo = {
    "2020067": 0, "2020085": 0, "2020047": 0, "2020049": 0, "2020055": 0,
    "2020045": 0, "2020006": 0, "2020041": 0, "2020048": 0, "2020042": 0,
    "2020046": 0, "2020030": 0, "2020031": 0, "2020074": 0, "2020019": 0,
    "2020040": 0, "2020056": 0, "2020075": 0, "2010016": 0,
    "2010005": 1, "2020027": 1, "2020036": 1,
    "2050003": 2, "2050004": 2, "2050005": 2, "2050006": 2,
    "2050007": 2, "2050008": 2, "2050009": 2,
    "2050001": 3,
    "2040005": 4,
    "2020029": 5, "2020053": 5,
    "2020018": 6, "2040001": 6, "2040003": 6, "2020101": 6, "2020103": 6,
    "2020034": 6
}
    return codigo.get(natureza, 7)
 
 
def definir_TES(actions, codigo, ctrl_imposto):
    """
    Define o Tipo de Entrada/Saída (TES) com base no código extraído da natureza
    e no indicador da modalidade de impostos presente na variável ctrl_imposto.
 
    :param codigo: Código do caso de lançamento.
    :param ctrl_imposto: Controle de impostos aplicados ao item.
 
    :return: O TES correspondente.
    """
    sleep(0.5)
    press(["left"]*10, interval=0.3)
    sleep(0.5)
    tes = ""
 
    match codigo:
        case 0:
            if ctrl_imposto != "Nenhum imposto":
                tes = "421"
            else:
                tes = "420"
       
        case 1:
            if ctrl_imposto == "Nenhum imposto":
                tes = "402"
            elif ctrl_imposto in ["Apenas ICMS e ICMSST", "Apenas o ICMS", "Apenas o ICMSST"]:
                tes = "405"
            elif ctrl_imposto == "Todos os impostos":
                tes = "407"
            else:
                tes = "403"
       
        case 2:
            if ctrl_imposto not in ["Todos os impostos", "Apenas ICMS e IPI", "Apenas ICMSST e IPI", "Apenas o IPI"]:
                tes = "408"
            else:
                tes = "411"
       
        case 3:
            tes = "423"
       
        case 4:
            if ctrl_imposto not in ["Todos os impostos", "Apenas ICMS e IPI", "Apenas ICMSST e IPI", "Apenas o IPI"]:
                tes = "102"
            else:
                tes = "432"
       
        case 5:
            hotkey("ctrl", "c", interval=0.5)
            tes_padrao = paste()
            if tes_padrao == "406":
                tes = "406"
            else:
                if ctrl_imposto == "Nenhum imposto":
                    tes = "402"
                elif ctrl_imposto == "Todos os impostos":
                    tes = "407"
                elif ctrl_imposto in ["Apenas ICMS e ICMSST", "Apenas o ICMS", "Apenas o ICMSST"]:
                    tes = "405"
                else:
                    tes = "403"
       
        case 6:
            hotkey("ctrl", "c", interval=0.5)
            tes_padrao = paste()
            if tes_padrao == "406":
                tes = "406"
            else:
                press(["left"]*2, interval=0.3)
                sleep(0.7)
                hotkey("ctrl", "c", interval=0.5)
                item_especifico = paste()
                press(["right"]*2, interval=0.3)
                sleep(0.5)
                if item_especifico in ["0207000001", "1312000156", "999920091200", "999949011000", "1303102887", "1302578",
                                       "1303100449", "1303100601", "1303100602", "1303100603", "1312000122", "1312000124",
                                       "1312000125", "1312000126", "1312000144", "1308002", "1312024", "1303100550", "1303100600", 
                                       "1303101290", "1303101291", "1303103835", "1303103836", "1303103837", "1312000141"]:
                    
                    if ctrl_imposto != "Nenhum imposto":
                        tes = "421"
                    else:
                        tes = "420"
                else:
                    if ctrl_imposto == "Nenhum imposto":
                        tes = "402"
                    elif ctrl_imposto in ["Apenas ICMS e ICMSST", "Apenas o ICMS", "Apenas o ICMSST"]:
                        tes = "405"
                    elif ctrl_imposto == "Todos os impostos":
                        tes = "407"
                    else:
                        tes = "403"
               
        case 7:
            cancelar_lancamento = True
            utils.cancelar_lancamento()
            sleep(2)
            utils.voltar_descer(actions)
            sleep(0.3)
            tes = cancelar_lancamento
 
    utils.checar_failsafe()
    return tes
   
 
def zerar_imposto(passos_ida=7, passos_volta=8):
    press(["right"]*passos_ida, interval=0.1)
    sleep(0.8)
    press("enter", interval=1)
    press("backspace", interval=0.3)
    press("enter", interval=1)
    press(["left"]*passos_volta, interval=0.1)
    utils.checar_failsafe()
 
 
def escrever_TES(tes):
    sleep(0.5)
    press("enter", interval=1)
    write(tes, interval=1)
    sleep(2)
    press(["right"]*4, interval=0.2)
    utils.checar_failsafe()
 
 
def inserir_desconto(desc_no_item):
    press(["right"]*3, interval=0.1)
    sleep(0.3)
    press("enter", interval=1)
    desc_no_item = utils.formatador2(desc_no_item)
    write(desc_no_item, interval=0.5)
    sleep(0.3)
    utils.checar_failsafe()
 
 
def inserir_frete(frete_no_item):
    press(["right"]*105)
    sleep(0.6)
    press("enter", interval=1)
    frete_no_item = utils.formatador2(frete_no_item)
    write(frete_no_item, interval=0.5)
    sleep(0.3)
    utils.checar_failsafe()
 
 
def inserir_seguro(seg_no_item):
    sleep(0.3)
    press("enter", interval=1)
    seg_no_item = utils.formatador2(seg_no_item)
    write(seg_no_item, interval=0.5)
    sleep(0.3)
    utils.checar_failsafe()
 
 
def inserir_despesa(desp_no_item):
    sleep(0.3)
    press("enter", interval=1)
    desp_no_item = utils.formatador2(desp_no_item)
    write(desp_no_item, interval=0.5)
    sleep(0.3)
    press(["left"]*112)
    sleep(0.6)
    utils.checar_failsafe()
 
 
def inserir_ICMS(icms_no_item, bc_icms, aliq_icms):
    press(["right"]*7, interval=0.1)
    sleep(0.3)
    press("enter", interval=1)
    bc_icms = utils.formatador2(bc_icms)
    write(bc_icms, interval=0.5)
    sleep(0.3)
    press(["right"]*8)
    sleep(0.3)
    press("enter", interval=1)
    utils.checar_failsafe()
    write(aliq_icms, interval=0.5)
    sleep(0.3)
    press(["left"]*9)
    sleep(0.3)
    press("enter", interval=1)
    icms_no_item = utils.formatador2(icms_no_item)
    write(icms_no_item, interval=0.5)
    sleep(0.3)
    utils.checar_failsafe()
 
 
def inserir_ICMSST(icmsST_no_item, base_icms_ST, aliq_icms_ST, passosST=9):
    press(["right"]*passosST)
    sleep(0.5)
    press("enter", interval=1)
    base_icms_ST = utils.formatador2(base_icms_ST)
    write(base_icms_ST, interval=0.5)
    sleep(0.5)
    press("enter", interval=1)
    utils.checar_failsafe()
    write(aliq_icms_ST, interval=0.5)
    sleep(0.5)
    press("enter", interval=1)
    icmsST_no_item = utils.formatador2(icmsST_no_item)
    write(icmsST_no_item, interval=0.5)
    sleep(0.3)
    press(["left"]*12)
    sleep(0.3)    
    utils.checar_failsafe()
 
 
def inserir_IPI(ipi_no_item, base_ipi, aliq_ipi, passosIPI=12):
    press(["right"]*passosIPI)
    sleep(0.3)
    press("enter", interval=1)
    base_ipi = utils.formatador2(base_ipi)
    write(base_ipi, interval=0.5)
    sleep(0.3)
    press(["right"]*5, interval=0.1)
    sleep(0.3)
    press("enter", interval=0.7)
    utils.checar_failsafe()
    write(aliq_ipi, interval=0.5)
    sleep(0.3)
    press(["left"]*6)
    sleep(0.3)
    press("enter", interval=1)
    ipi_no_item = utils.formatador2(ipi_no_item)
    write(ipi_no_item, interval=0.5)
    sleep(0.3)
    press(["left"]*14)
    sleep(0.3)
    utils.checar_failsafe()
 
 
def corrigir_passos_horizontal(cont, item):
    if len(item) > 1:
        press(["right"]*4, interval=0.1)
        sleep(1)
        if cont == len(item):
            press(["left"]*4)
             
  