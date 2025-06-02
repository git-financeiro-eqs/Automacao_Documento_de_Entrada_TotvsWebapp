class TratadorItem:
    """
    Essa classe serve unica e exclusivamente para fornecer o tratamento lógico necessário aos itens que 
    foram fracionados para atender alguma necessidade no pedido, como divisão por centro de custo por exemplo.
    Em uma NF, o item vem em sua totalidade, conforme foi comprado, por exemplo: 50 teclados de computador.
    Contudo, muitas vezes o comprador que efetuou a compra necessita distribuir esses 50 teclados entre os setores diversos
    da empresa, fazendo assim com que seja necessário a divisão dos itens por centro de custo no pedido interno.
    Quando ocorre essa divisão o pedido lança o item de maneira fracionada, gerando duas linhas para um item.
    Nesses casos, o programa precisa saber lidar com essa possibilidade e realizar um tratamente proporcional para aquele item que,
    na NF está inteiro, mas, no pedido, onde antes cada linha deveria representar um item inteiro, 
    passa a representar uma fração de um mesmo item.

    Nessa classe ocorre o tratamento lógico para esses casos, aplicando razão e proporção quando identificado um caso de item
    fracionado.

    """

    def __init__(self, item_fracionado, itens, i, ctrl_imposto):
        self.item_fracionado = item_fracionado
        self.itens = itens
        self.i = i
        self.ctrl_imposto = ctrl_imposto
        self.item = []
 


    def tratar_item(self):
        match self.ctrl_imposto:
            case "Nenhum imposto":
                pass

            case "Apenas o ICMS":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, base_e_aliq_icms, icmsST_no_item, ipi_no_item = self.itens[self.i]
                base_icms, aliq_icms = base_e_aliq_icms
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        icms = icms_no_item * razao
                        bc_icms = base_icms * razao
                        self.item.append([icms, bc_icms, aliq_icms, icmsST_no_item, ipi_no_item])
                else:
                    self.item.append([icms_no_item, base_icms, aliq_icms, icmsST_no_item, ipi_no_item])
        
            case "Apenas o ICMSST":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, icmsST_no_item, base_e_aliq_ST, ipi_no_item = self.itens[self.i]
                base_icms_ST, aliq_icms_ST = base_e_aliq_ST
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        icmsST = icmsST_no_item * razao
                        bc_icms_ST = base_icms_ST * razao
                        self.item.append([icmsST, bc_icms_ST, aliq_icms_ST, ipi_no_item])
                else:
                    self.item.append([icms_no_item, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item])
        
            case "Apenas o IPI":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, icmsST_no_item, ipi_no_item, base_e_aliq_ipi = self.itens[self.i]
                base_ipi, aliq_ipi = base_e_aliq_ipi
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        ipi = ipi_no_item * razao
                        bc_ipi = base_ipi * razao
                        self.item.append([icms_no_item, icmsST_no_item, ipi, bc_ipi, aliq_ipi])
                else:
                    self.item.append([icms_no_item, icmsST_no_item, ipi_no_item, base_ipi, aliq_ipi])
        
            case "Apenas ICMSST e IPI":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, icmsST_no_item, base_e_aliq_ST, ipi_no_item, base_e_aliq_ipi = self.itens[self.i]
                base_icms_ST, aliq_icms_ST = base_e_aliq_ST
                base_ipi, aliq_ipi = base_e_aliq_ipi
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        icmsST = icmsST_no_item * razao
                        bc_icms_ST = base_icms_ST * razao
                        ipi = ipi_no_item * razao
                        bc_ipi = base_ipi * razao
                        self.item.append([icms_no_item, icmsST, bc_icms_ST, aliq_icms_ST, ipi, bc_ipi, aliq_ipi])
                else:
                    self.item.append([icms_no_item, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item, base_ipi, aliq_ipi])
        
            case "Apenas ICMS e IPI":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, base_e_aliq_icms, icmsST_no_item, ipi_no_item, base_e_aliq_ipi = self.itens[self.i]
                base_icms, aliq_icms = base_e_aliq_icms
                base_ipi, aliq_ipi = base_e_aliq_ipi
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        icms = icms_no_item * razao
                        bc_icms = base_icms * razao
                        ipi = ipi_no_item * razao
                        bc_ipi = base_ipi * razao
                        self.item.append([icms, bc_icms, aliq_icms, icmsST_no_item, ipi, bc_ipi, aliq_ipi])
                else:
                    self.item.append([icms_no_item, base_icms, aliq_icms, icmsST_no_item, ipi_no_item, base_ipi, aliq_ipi])
        
            case "Apenas ICMS e ICMSST":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, base_e_aliq_icms, icmsST_no_item, base_e_aliq_ST, ipi_no_item = self.itens[self.i]
                base_icms, aliq_icms = base_e_aliq_icms
                base_icms_ST, aliq_icms_ST = base_e_aliq_ST
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        icms = icms_no_item * razao
                        bc_icms = base_icms * razao
                        icmsST = icmsST_no_item * razao
                        bc_icms_ST = base_icms_ST * razao
                        self.item.append([icms, bc_icms, aliq_icms, icmsST, bc_icms_ST, aliq_icms_ST, ipi_no_item])
                else:
                    self.item.append([icms_no_item, base_icms, aliq_icms, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item])
        
            case "Todos os impostos":
                valor_do_item, quant_do_item, vl_unit_item, icms_no_item, base_e_aliq_icms, icmsST_no_item, base_e_aliq_ST, ipi_no_item, base_e_aliq_ipi = self.itens[self.i]
                base_icms, aliq_icms = base_e_aliq_icms
                base_icms_ST, aliq_icms_ST = base_e_aliq_ST
                base_ipi, aliq_ipi = base_e_aliq_ipi
                if self.item_fracionado != []:
                    for razao in self.item_fracionado:
                        icms = icms_no_item * razao
                        bc_icms = base_icms * razao
                        icmsST = icmsST_no_item * razao
                        bc_icms_ST = base_icms_ST * razao
                        ipi = ipi_no_item * razao
                        bc_ipi = base_ipi * razao
                        self.item.append([icms, bc_icms, aliq_icms, icmsST, bc_icms_ST, aliq_icms_ST, ipi, bc_ipi, aliq_ipi])
                else:
                    self.item.append([icms_no_item, base_icms, aliq_icms, icmsST_no_item, base_icms_ST, aliq_icms_ST, ipi_no_item, base_ipi, aliq_ipi])
        
        
        return self.item