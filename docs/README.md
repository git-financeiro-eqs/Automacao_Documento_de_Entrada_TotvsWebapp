# Bot em execução
<br/>
<br/>



https://github.com/user-attachments/assets/3ce7503c-85be-4b42-ac98-60ba1ccaf73a


<br/>

- Primeira parte da execução do Bot após o usuário já ter sido inicializado no Chrome driver Selenium. Nesse trecho do processo de lançamento de uma NF, o Bot está clicando no botão _Ver Documentos_ para abrir o processo no portal. Ao abrir o processo no portal, ele coleta a URL do processo e abre a mesma página no Chrome driver Selenium. Através desse acesso virtual à pagina do processo, por meio da biblioteca Selenium, é possível mapear todos os elementos html presentes na página, o que permite a ele extrair a chave de acesso da NF que está sendo lançada, e, com a chave de acesso, procurar o arquivo xml na pasta repositório de XMLs. Caso o arquivo XML ainda não esteja na pasta, o Microsiga permite que ele faça a extração do XML diretamente na rotina Processo Pagamento, como ocorreu no vídeo, onde foi passado o caminho do diretório xmlFiscalio (pasta repositório) para receber o arquivo xml do processo. Então o Bot lê o arquivo e extrai os dados conforme está no módulo _extratorXML_. Depois clica em _Dados da Nota_ para iniciar o lançamento. Após inserir a TES 408 por padrão, a primeira conferência que ele faz é a da Filial de entrega, que precisa corresponder ao CNPJ do destinatário presente na NF. Caso não corresponda, o lançamento é cancelado e aquela chave de acesso é incorporada a uma lista de processos a serem ignorados pela automação. Quem deve efetuar a correção desses processos é um operador do setor financeiro.
<br/>
<br/>


https://github.com/user-attachments/assets/f332c8bb-f2ba-4ab7-a348-d9a708f4e57b

<br/>

- Segunda parte. Nesse momento o bot está aguardando que surja a tela de lançamento. Nessa tela ele começa a validação e inserção dos valores. Primeiro ele verifica se o valor total do item no processo corresponde ao valor total do item na NF. Essa ordenação de itens é pautada pelo xml. O primeiro item do xml, na grande maioria dos casos corresponde ao primeiro item do processo. Quando não corresponde, o bot cancela o lançamento e vai para o próximo, mas a grande maioria segue a mesma ordem. Quando o valor do item no processo não bate com o da NF, a primeira solução é tentar inserir o valor correto diretamente no campo (às vezes a diferença é de centavos), se acaso essa primeira solução não for aceita pelo sistema (o que não é o caso do vídeo), o bot verifica a quantidade do item no Microsiga e, se estiver de acordo com o xml, ele corrige o valor unitário no Siga para conforme está no xml. Caso a quantidade também não coincida, então ele tem duas alternativas que serão melhor explicadas no próximo trecho. Para o caso desse vídeo, os dois primeiros itens tiveram seus valores corrigidos diretamente no campo Valor Total. Após corrigido o valor, o bot verifica a natureza e parte para a inserção da TES. A TES é definida com base na natureza e nos impostos destacados para aquele item, além de um caso especifico definido pelo setor Fiscal, que são os casos dos itens que já vêm com a TES 406 por padrão - essa TES precisa ser mantida, e o bot a mantém -. Depois de inserida a TES, o bot insere os valores de _Desconto, Despesas Acessórias, Frete e Seguro_. Caso o item não tenha nenhum desses valores, o bot ainda assim insere o valor 0,00 nos campos afim de corrigir qualquer equivoco por parte do comprador no momento da criação do pedido. Depois, são inseridos os valores dos impostos, e então passa para o próximo item a ser verificado.
<br/>
<br/>


https://github.com/user-attachments/assets/9f8d9136-fcc8-4314-9978-4962943f393d

<br/>

- Terceira parte. Aqui nós temos um exemplo de caso onde a primeira correção de valor total feita pelo Bot não foi aceita pelo sistema. Nesse caso ele partiu para conferir a quantidade do item e isso também não correspondeu à NF. Então, uma daquelas duas alternativas citadas no trecho anterior acontece. O Bot parte para conferir o código do item, primeiro, para validar se o item é de um tipo que sofre conversão de unidade de medida, como gás e pilhas por exemplo, caso seja um item do tipo, o tratamento será um específico, presente no módulo _operadoresLancamento_, nas funções _verificar_valor_item()_ e _contar_item_fracionado()_. Caso o item não seja detectado como do tipo que sofre conversão, o bot tenta verificar se é um item que está fracionado (*Vide explicação presente no código), que consiste em checar se o item abaixo é o mesmo item que ele está lançando no momento. Caso seja o mesmo item, ele verifica a quantidade e, se essa quantidade somada a anterior bater com o total da NF, ele confirma que é um item fracionado e aplica o tratamento para o caso, que é determinar uma razão entre a quantidade do item presente em cada linha pela quantidade total na NF - _razão = quantidade na linha / quantidade total_ -. Coletada a razão para cada linha, podendo o item ser divido em quantas linhas for necessário, o bot aplica o roteiro presente no módulo _tratamentoItem_, conforme ilustra muito bem esse terceiro vídeo. Caso a somatória não bata com o total da NF, o lançamento é cancelado e o bot pula para a próxima. Essa é a segunda alternativa.
<br/>
<br/>


https://github.com/user-attachments/assets/2b4ccd9f-1a2f-4d4f-a4b1-87b9962e9771

<br/>

- Quarta e ultima parte. Nesse ultimo trecho, após ter sido feito o processo de validação dos itens, o bot irá para a aba duplicatas afim de verificar o valor das parcelas. Ele verifica a primeira e, caso não corresponda ao valor total da NF (pagamento a vista) ele desce para procurar outra parcela. Em caso de haver outra parcela, ele a soma ao valor da primeira e verifica novamente se bate com o total da NF. Se não bater ele repete a ação. Caso ele chegue na ultima parcela e ainda assim a somatória de todas as outras não corresponderem ao total, ele faz a correção. A ultima parcela é na grande maioria das vezes a única que pode estar errada, então é ela que é corrigida com a diferença entre o Siga e a NF. Essa dinâmica vale tanto pra diferenças maiores que zero quanto menores, e também vale para pagamentos a vista, onde há somente uma parcela.
Depois de corrigido o valor das parcelas, então é feita a validação da natureza da duplicata. Como explicado no código, um pedido com mais de um item pode ter mais de uma natureza. Tendo mais de uma natureza, a natureza majoritária precisa ser a mesma natureza vinculada a duplicata. O Bot realiza essa conferencia no momento em que verifica a porcentagem que cada natureza tem sobre o todo da nota fiscal. Caso o valor seja 0,00, então significa que no pedido teve apenas uma natureza, sendo assim, não é necessário fazer a correção. Caso contrario, o bot coleta uma a uma das porcentagens e separa a majoritária, depois ele torna a procura-la e, encontrando a maior, ele coleta a natureza no campo ao lado e vai até o primeiro campo de natureza presente na aba duplicatas para inseri-la ali, independente se a informação já estiver correta, ele sempre realiza esse procedimento.
Então todo o processo de lançamento está feito, bastando apenas finaliza-lo, e é isso que acontece no restante do vídeo.



