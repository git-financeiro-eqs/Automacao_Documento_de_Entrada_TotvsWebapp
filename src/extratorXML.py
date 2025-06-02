from utils import formatador, formatador2, formatador3


class ProcessadorXML:
    """
    Classe responsável por processar dados de XMLs de notas fiscais.
    Extrai informações como valores totais, impostos, e detalhes dos itens.
    """

    def __init__(self, doc):
        """
        Inicializa a classe ProcessadorXML.

        :param doc: Dicionário contendo os dados do XML da nota fiscal.
        """
        self.doc = doc
        self.valores_do_item = []
        self.indices_e_impostos = []
        self.itens = []


    def coletar_nome_fantasia(self):
        """
        Coleta o nome fantasia do fornecedor da nota fiscal.
        """
        try:
            nome_fantasia_forn = self.doc["nfeProc"]["NFe"]["infNFe"]["emit"]["xFant"]
        except KeyError:
            try:
                nome_fantasia_forn = self.doc["enviNFe"]["NFe"]["infNFe"]["emit"]["xFant"]
            except KeyError:
                try:
                    nome_fantasia_forn = self.doc["NFe"]["infNFe"]["emit"]["xFant"]
                except KeyError:
                    try:
                        nome_fantasia_forn = self.doc["nfeProc"]["NFe"]["infNFe"]["emit"]["xNome"]
                    except KeyError:
                        try:
                            nome_fantasia_forn = self.doc["enviNFe"]["NFe"]["infNFe"]["emit"]["xNome"]
                        except KeyError:
                            nome_fantasia_forn = self.doc["NFe"]["infNFe"]["emit"]["xNome"]


        nome_fantasia_forn = nome_fantasia_forn[:20]

        return nome_fantasia_forn


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
                if valores_do_item[cont+3] != 0.00:
                    cont+=4
                    tem_icms = True
                else:
                    cont+=3
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

