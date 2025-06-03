# Arquitetura do Sistema  
Este documento descreve a arquitetura do sistema de automação para processamento de notas fiscais (NFs) e lançamento de dados no sistema SIGA. O programa é composto por vários módulos que trabalham em conjunto para extrair, processar e validar os dados das NFs, além de realizar o lançamento no sistema interno.
<br/>

## Visão Geral  
O sistema é dividido em módulos que desempenham funções específicas, desde a extração de dados de XMLs até a interação com o sistema SIGA para o lançamento das informações. A automação é orquestrada pelo módulo tigrinho, que coordena as ações da automação.
<br/>
<br/>
<br/>


# Módulos do Sistema

<table>
  <thead>
    <tr>
      <th>Módulo</th>
      <th>Descrição</th>
      <th>Principais Responsabilidades</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>extratorXML.py</strong></td>
      <td>Extrai e processa os dados dos XMLs das notas fiscais.</td>
      <td>
        <ul>
          <li>Extrai informações como valores totais, impostos e detalhes dos itens.</li>
          <li>Processa os totais da nota fiscal (valor total, filial de entrega, etc.).</li>
          <li>Coleta e organiza os dados dos itens e impostos presentes no XML.</li>
        </ul>
        <strong>Classes:</strong> <code>ProcessadorXML</code> (realiza a extração e processamento dos dados).
      </td>
    </tr>
    <tr>
      <td><strong>gui.py</strong></td>
      <td>Fornece uma interface gráfica para o usuário interagir com o sistema.</td>
      <td>
        <ul>
          <li>Permite ao usuário iniciar a automação.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>atuadorWeb</strong></td>
      <td>Módulo responsável pela interação com páginas web utilizando Selenium, através da classe Interagente.</td>
      <td>
        <ul>
          <li>Controlar o navegador via Selenium.</li>
          <li>Interagir com elementos da página.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>main.py</strong></td>
      <td>Inicializa o programa e abre a interface gráfica.</td>
      <td>
        <ul>
          <li>Executa o módulo <code>gui</code> para iniciar a automação.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>mensagens.py</strong></td>
      <td>Contém mensagens de apresentação e instruções para o usuário.</td>
      <td>
        <ul>
          <li>Exibe um manual breve sobre como o operador deve acionar o programa.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>operadoresLancamento.py</strong></td>
      <td>Contém funções utilitárias para a conferência e validação dos valores da NF com os valores do pedido no SIGA.</td>
      <td>
        <ul>
          <li>Verifica e corrige valores unitários e quantidades dos itens.</li>
          <li>Define o Tipo de Entrada/Saída (TES) com base na natureza do item e nos impostos aplicados.</li>
          <li>Insere descontos, fretes, seguros e despesas no sistema.</li>
          <li>Lida com impostos como ICMS, ICMS-ST e IPI.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>tigrinho.py</strong></td>
      <td>Orquestra o fluxo da automação, coordenando as suas ações junto aos demais módulos.</td>
      <td>
        <ul>
          <li>Interage com o sistema SIGA e com o portal compras para abrir processos e exportar XMLs.</li>
          <li>Extrai e processa os dados dos XMLs usando a classe <code>ProcessadorXML</code>.</li>
          <li>Realiza o tratamento de itens fracionados usando a classe <code>TratadorItem</code>.</li>
          <li>Valida e lança os dados no sistema SIGA.</li>
          <li>Lida com erros e exceções durante o processo.</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td><strong>tratamentoItem.py</strong></td>
      <td>Trata itens que foram fracionados no pedido, aplicando razão e proporção aos valores.</td>
      <td>
        <ul>
          <li>Aplica tratamento proporcional para itens que foram divididos em várias linhas no pedido.</li>
          <li>Garante que os valores dos itens fracionados sejam corretamente lançados no sistema.</li>
        </ul>
        <strong>Classes:</strong> <code>TratadorItem</code> (realiza o tratamento lógico dos itens fracionados).
      </td>
    </tr>
    <tr>
      <td><strong>utils.py</strong></td>
      <td>Fornece funções utilitárias para todos os módulos do sistema.</td>
      <td>
        <ul>
          <li>Funções para formatação de valores.</li>
          <li>Funções para interação com a interface gráfica do SIGA (clicar, copiar, colar, etc.).</li>
          <li>Funções para tratamento de erros e exceções.</li>
          <li>Funções para envio de e-mails em caso de falhas.</li>
          <li>Funções para manipulação de listas e links.</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>
<br/>

## Regras de negócio

A Automação deve verificar se a filial de entrega posta no pedido corresponde a filial de entrega extraída da NF. Caso não corresponda, o processo deve ser pulado e os logs de erro devem ser disparados;

As naturezas de ativo 2020081, 2020060, 2020082, 2020083 são naturezas usadas em notas fiscais de serviço. Em casos onde o comprador utilizou essas naturezas erroneamente, a automação deve substitui-las pelas naturezas 2050006, 2050004, 2050008, como está posto no código, na função operadoresLancamento.copiar_natureza();

O título (duplicata) gerado pelo SIGA para o financeiro pagar precisa de uma natureza da mesma forma que os itens do pedido. Há casos (quando na NF há destacado mais de um item e no pedido o comprador o cria destinando naturezas diferentes para esses itens) em que a natureza que o siga puxa para o título não corresponde a natureza do item de maior valor, ou, não corresponde a natureza dos itens que, somados, detêm a maior parcela de natureza do pedido. Nesses casos, a automação deve identificar a natureza majoritária do processo e inseri-la no campo correspondente à natureza da duplicata.
<br/>
<br/>

## Observações  

A Biblioteca Pyautogui é uma maneira diferente de execultar a técnica da raspagem de tela. Para o Pyautogui execultar essa técnica, é preciso tirar um print do elemento que se deseja procurar, salvá-lo em algum diretório, e passar o caminho desse arquivo para o método locateOnScreen. As imagens dos elementos que foram mapeadas para essa automação estão na pasta Imagens.
<br/>
<br/>

## Considerações Finais  
A arquitetura do sistema foi projetada para ser modular, permitindo que cada parte do processo seja executada de forma independente. Isso facilita a manutenção e a expansão do sistema, além de garantir que cada módulo tenha uma responsabilidade clara e bem definida.
