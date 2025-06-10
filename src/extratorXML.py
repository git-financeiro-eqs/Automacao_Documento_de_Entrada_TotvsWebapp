from utils import formatador, formatador2, formatador3

class ProcessadorXML:
    """
    Classe responsável por processar dados de XMLs de notas fiscais.
    Extrai informações como valores totais, impostos, e detalhes dos itens.
    """

    def __init__(self, doc, empresa):
        """
        Inicializa a classe ProcessadorXML.

        :param doc: Dicionário contendo os dados do XML da nota fiscal.
        """
        self.doc = doc

        if empresa == "Bratec":
            self.cnpj_dict = {
            '27462720000125': '01', '27462720000397': '03', 
            '27462720000478': '04', '27462720000630': '06'
            }
            
        else:
            self.cnpj_dict = {
                '80464753000197': '02', '80464753000430': '04', '80464753000510': '05', '80464753000782': '07',
                '80464753000863': '08', '80464753000944': '09', '80464753001088': '10', '80464753001169': '11',
                '80464753001240': '12', '80464753001320': '13', '80464753001401': '14', '80464753001592': '15',
                '80464753001673': '16', '80464753001916': '19', '80464753002050': '20', '80464753002130': '21',
                '80464753002211': '22', '80464753002564': '25', '80464753002645': '26', '80464753002807': '28',
                '80464753002998': '29', '80464753003021': '30', '80464753003102': '31', '80464753003293': '32',
                '80464753003374': '33', '80464753003617': '34', '80464753003536': '35', '80464753003455': '36',
                '80464753003706': '37', '80464753003960': '39', '80464753004001': '40', '80464753004184': '41',
                '80464753004265': '42', '80464753004346': '43', '80464753004699': '46', '80464753004770': '47',
                '80464753004850': '48', '80464753004931': '49', '80464753005075': '50', '80464753005156': '51',
                '80464753005407': '54', '80464753005580': '55', '80464753005660': '56', '80464753005741': '57',
                '80464753005822': '58', '80464753005903': '59', '80464753006047': '60', '80464753006209': '62',
                '80464753006390': '63'
            }
            
        self.valores_do_item = []
        self.indices_e_impostos = []
        self.itens = []



    def processar_totais_nota_fiscal(self):
        """
        Processa os totais da nota fiscal, como valor total e filial de entrega.

        :return: Uma tupla contendo o valor total da nota fiscal e o código da filial de entrega.
        """
        try:
            totais_nota_fiscal = self.doc["nfeProc"]["NFe"]["infNFe"]["total"]["ICMSTot"]
        except KeyError:
            try:
                totais_nota_fiscal = self.doc["enviNFe"]["NFe"]["infNFe"]["total"]["ICMSTot"]
            except KeyError:
                totais_nota_fiscal = self.doc["NFe"]["infNFe"]["total"]["ICMSTot"]
 
        valor_total_da_nf = totais_nota_fiscal["vNF"]
        valor_total_da_nf = formatador2(valor_total_da_nf)
        valor_total_da_nf = float(valor_total_da_nf)
 
        try:
            cnpj_filial_de_entrega = self.doc["nfeProc"]["NFe"]["infNFe"]["dest"]["CNPJ"]
        except KeyError:
            try:
                cnpj_filial_de_entrega = self.doc["enviNFe"]["NFe"]["infNFe"]["dest"]["CNPJ"]
            except KeyError:
                cnpj_filial_de_entrega = self.doc["NFe"]["infNFe"]["dest"]["CNPJ"]
                
 
        filial_xml = self.cnpj_dict[cnpj_filial_de_entrega]

        return valor_total_da_nf, filial_xml



    def coletar_dados_XML(self, coletor_xml, impostos_xml):
        """
        Coleta os dados de um item quando a NF refere-se somente a um item, ou, coleta os dados de todos os itens do XML, 
        como valores do produto, quantidade, impostos, desconto, frete ou outras despesas.

        :param coletor_xml: Dicionário contendo os dados do item do XML.
        :param impostos_xml: Dicionário contendo os dados dos impostos do item.

        :return: Lista com os valores coletados do, ou, dos itens. (Em caso de mais de um item, os valores vêm todos juntos no
                 mesmo array, esse array é tratado no método abaixo "trabalhar_dados_XML()" que retorna uma lista bidimensional,
                 onde cada elemento da lista é uma lista com os valores de um item específico).
        """

        valor_prod = coletor_xml["vProd"]
        valor_prod = formatador(valor_prod)
         
        quantidade_comprada = coletor_xml["qCom"]
        quantidade_comprada = formatador(quantidade_comprada, casas_decimais="{:.6f}")
        valor_unitario = coletor_xml["vUnCom"]
        valor_unitario = formatador(valor_unitario, casas_decimais="{:.6f}")

        self.valores_do_item.append(valor_prod)
        self.valores_do_item.append(quantidade_comprada)
        self.valores_do_item.append(valor_unitario)

        try:
            valor_desconto_xml = coletor_xml["vDesc"]
            valor_desconto_xml = formatador3(valor_desconto_xml)
        except KeyError:
            valor_desconto_xml = 0.00

        self.valores_do_item.append(valor_desconto_xml)

        try:
            valor_frete_xml = coletor_xml["vFrete"]
            valor_frete_xml = formatador3(valor_frete_xml)
        except KeyError:
            valor_frete_xml = 0.00

        self.valores_do_item.append(valor_frete_xml)

        try:
            valor_seguro_xml = coletor_xml["vSeg"]
            valor_seguro_xml = formatador3(valor_seguro_xml)
        except KeyError:
            valor_seguro_xml = 0.00

        self.valores_do_item.append(valor_seguro_xml)

        try:
            valor_desp_xml = coletor_xml["vOutro"]
            valor_desp_xml = formatador3(valor_desp_xml)
        except KeyError:
            valor_desp_xml = 0.00

        self.valores_do_item.append(valor_desp_xml)

        try:
            busca_icms_xml = impostos_xml["ICMS"]
            atributos_icms = busca_icms_xml.values()
            atributos_icms = list(atributos_icms)
            descompactar_lista = atributos_icms[0]
            valor_icms = descompactar_lista["vICMS"]
            valor_icms = formatador3(valor_icms)
        except KeyError:
            valor_icms = 0.00

        self.valores_do_item.append(valor_icms)

        if valor_icms != 0.00:
            aliquota_icms = descompactar_lista["pICMS"]
            aliquota_icms = formatador2(aliquota_icms)
            bc_icms = descompactar_lista["vBC"]
            bc_icms = formatador3(bc_icms)
            self.valores_do_item.append((bc_icms, aliquota_icms))

        try:
            busca_icms_xml = impostos_xml["ICMS"]
            atributos_icms = busca_icms_xml.values()
            atributos_icms = list(atributos_icms)
            descompactar_lista = atributos_icms[0]
            valor_icms_st = descompactar_lista["vICMSST"]
            valor_icms_st = formatador3(valor_icms_st)
        except KeyError:
            valor_icms_st = 0.00

        self.valores_do_item.append(valor_icms_st)

        if valor_icms_st != 0.00:
            aliquota_icms_st = descompactar_lista["pICMSST"]
            aliquota_icms_st = formatador2(aliquota_icms_st)
            bc_icms_st = descompactar_lista["vBCST"]
            bc_icms_st = formatador3(bc_icms_st)
            self.valores_do_item.append((bc_icms_st, aliquota_icms_st))

        try:
            busca_ipi_xml = impostos_xml["IPI"]["IPITrib"]
            valor_ipi = busca_ipi_xml["vIPI"]
            valor_ipi = formatador2(valor_ipi)
            valor_ipi = float(valor_ipi)
        except KeyError:
            valor_ipi = 0.00

        self.valores_do_item.append(valor_ipi)

        if valor_ipi != 0.00:
            aliquota_ipi = busca_ipi_xml["pIPI"]
            aliquota_ipi = formatador2(aliquota_ipi)
            bc_ipi = busca_ipi_xml["vBC"]
            bc_ipi = formatador3(bc_ipi)
            self.valores_do_item.append((bc_ipi, aliquota_ipi))

        return self.valores_do_item
    


    def trabalhar_dados_XML(self, valores_do_item):
        """
        Organiza os dados coletados dos itens do XML em listas estruturadas.

        :param valores_do_item: Lista contendo os valores coletados dos itens.

        :return: Duas listas, uma com os dados dos itens e outra com os tipos de impostos aplicados. Essas listas são geradas
                 respeitando um indice em comum, ou seja, o primeiro elemento da lista "itens" terá como tipo
                 de imposto o primeiro elemento da lista "indices_e_impostos".
                 Toda a lógica de funcionamento dessa automação é pautada nessas duas listas.
        """

        controlador = len(valores_do_item)
        cont = 0
        aux = 0
        try:
            while cont <= controlador:
                tem_icms = False
                tem_icms_st = False
                tem_ipi = False
                if valores_do_item[cont+7] != 0.00:
                    cont+=8
                    tem_icms = True
                else:
                    cont+=7
                if valores_do_item[cont+1] != 0.00:
                    cont+=3
                    tem_icms_st = True
                else:
                    cont+=2
                if valores_do_item[cont] != 0.00:
                    cont+=2
                    tem_ipi = True
                else:
                    cont+=1
                self.itens.append(self.valores_do_item[aux:cont])
                aux=cont
                if tem_icms == True and tem_icms_st == True and tem_ipi == True:
                    ctrl_imposto = "Todos os impostos"
                elif tem_icms == True and tem_icms_st == True:
                    ctrl_imposto = "Apenas ICMS e ICMSST"
                elif tem_icms == True and tem_ipi == True:
                    ctrl_imposto = "Apenas ICMS e IPI"
                elif tem_icms_st == True and tem_ipi == True:
                    ctrl_imposto = "Apenas ICMSST e IPI"
                elif tem_ipi == True:
                    ctrl_imposto = "Apenas o IPI"
                elif tem_icms_st == True:
                    ctrl_imposto = "Apenas o ICMSST"
                elif tem_icms == True:
                    ctrl_imposto = "Apenas o ICMS"
                else:
                    ctrl_imposto = "Nenhum imposto"
                self.indices_e_impostos.append(ctrl_imposto)
        except IndexError:
            pass

        return self.itens, self.indices_e_impostos
