# **Automação de Lançamento de DANFEs no ERP TOTVS Microsiga**  
<br/>

## 📌 **Descrição do Projeto**  
Este projeto tem como objetivo **automatizar o processo de lançamento de DANFEs (Documento Auxiliar de Nota Fiscal Eletrônica) no ERP TOTVS Microsiga**. A automação **extrai dados do XML** de cada nota fiscal e insere, valida, ou corrige esses dados no sistema, garantindo que todas as **regras de negócio** sejam atendidas. É um bot, um robô que controla o mouse e o teclado enquanto monitora
o que está sendo imprimido na tela para, com base em sua programação, realizar as tarefas e ações definidas que cada etapa do processo exige.  

### Fluxo de Trabalho:   
✅ Busca o XML correspondente no repositório local.  
✅ Extrai os dados do XML, como valores dos itens, impostos e filial de entrega.  
✅ Abre o processo de lançamento no Microsiga e insere os dados extraídos.  
✅ Verifica e corrige discrepâncias entre os valores do pedido interno e da NF.  
✅ Finaliza o lançamento e inicia o próximo processo.  
<br/>

## 🖥 **Tecnologias Utilizadas**  
- **Python** – Linguagem principal da automação.  
- **Selenium** – Abertura do Microsiga.  
- **Pyautogui** – Interação com a interface gráfica do ERP.  
- **Pyperclip** – Manipulação da área de transferência para inserção e validação dos dados.  
- **xmltodict** – Extração de dados estruturados dos arquivos XML.  
<br/>

## ⚙️ **Pré-requisitos**  
Antes de rodar o projeto, certifique-se de ter instalado:  
- **Python 3.x**    
- **ERP TOTVS Microsiga** instalado e acessível  
<br/>

## 📥 **Instalação**  

1. **Clone este repositório**  
   ```sh
   https://github.com/git-financeiro-eqs/Automacao_Documento_de_Entrada_TotvsWebapp.git
   ```
   
2. **Crie um ambiente virtual (opcional, mas recomendado)**  
   ```sh
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
   
3. **Instale as dependências**  
   ```sh
   pip install -r requirements.txt
   ```
<br/>   

## 🚀 **Como Executar**  
  
1. Coloque os **arquivos XML** das notas na pasta configurada como **repositório**.
   
   2.1. Configure o repositório de XMLs:  
        - Crie uma pasta para armazenar os XMLs das notas fiscais.  
        - Atualize o caminho da pasta no código, se necessário.  
        - Se acaso não tiver tempo para inserir os XMLs na pasta, a rotina Processo Pagamento permite que você extraia
          esses arquivos diretamente nela. O bot está programado para, em caso de não encontrar o XML na pasta repositório,
          buscar o arquivo pela função de extração do próprio SIGA.
   
3. **Execute o script principal**:  
   ```sh
   python main.py
   ```
4. Acione o botão **Play** e acompanhe o processo na interface do Microsiga. Efetue o login e abra a rotina Processo Pagamento.
<br/>

## **Observações**  
   
2. A automção envia o numero da NF impedida de lançamento por E-mail para o grupo Entrada de Documentos.

3. *Para um melhor entendimento do funcionamento do Bot, deixei um vídeo na pasta *docs* dele em ação.
