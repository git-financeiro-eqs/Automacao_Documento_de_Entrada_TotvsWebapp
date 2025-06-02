from tkinter import messagebox
 
class Mensagens:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
 
        self.info = "Olá! Eu sou a Mariquinha >.<"
        self.texto = """Sou sua parceira robô que irá lançar os caixas no microsiga para você!"""
 
        self.info2 = "Fiscal IO"
        self.texto2 = """Ao lado do bot temos a plataforma Fiscal IO. Nela você baixa todos os XMLs necessários para que eu possa realizar os lançamentos.
 
Vou deixer um breve manual de como baixar os XMLs nessa plataforma.
 
Toda vez que virar o mês, é necessário abrir a plataforma FiscalIO e baixar todos os XMLs do mês passado."""
 
        self.info3 = "Como operar"
        self.texto3 = """Modo de operar:
Escolha uma das modalidades da Mariquinha, seja o lançamento de uma unica RT ou, o lançamento sequencial, basta dar o play e deixar acontecer!
Para lançar apenas uma RT por vez basta inserir o número da RT no campo próprio da Mariquinha e apertar o botão play logo abaixo.
 
Ao acionar a Mariquinha, em qualquer uma de suas modalidades, o navegador será aberto pelo Selenium. A automação abre o microsiga WebApp diretamente, você só precisa inserir as credenciais e selecionar a rotina IntAgillitas no módulo Compras.
Resumindo, a automação abre o siga WebApp, mas, quem coloca as credenciais e seleciona a rotina desejada é você. Então, muita atenção nessa hora pra não acabar escolhendo a rotina errada. Após aberta a rotina, pode soltar o mouse e o teclado que o resto é com a Mariquinha.
 
Para interromper ou finalizar a execução do bot, basta levar o cursor do mouse até o limite do canto superior esquerdo da sua tela e aguardar 10 segundos.
Se a tela do bot estiver preta, mantenha o cursor no canto extremo do monitor e aguarde mais um pouco.
 
Além disso, a Mariquinha também tem a função de rejeitar Caixas! Basta clicar na boca dela e digitar a mensagem de rejeição desejada. Mas, cuidado! Ela só rejeita o caixa se você já o tiver deixado aberto na rotina IntAgillitas. Então, lembre-se, para utilizar essa funcionalidade é preciso já estar com o microsiga WebApp aberto no caixa que se deseja rejeitar.
"""
 
        self.info4 = "Atenção!"
        self.texto4 = """Atenção!
 
Nosso servidor está sempre sobrecarregado, o que pode gerar instabilidade no bot durante sua execução, fazendo-o "crachar" e não conseguir lançar mais nenhum processo. Se acaso perceber algum desses momentos de instabilidade do servidor, verifique se o bot continua execultando seus lançamentos ou se está travado em alguma tela. Se estiver travado, realize o procedimento de interrupção, depois inicialize o bot novamente."""
 
 
    def mostrar_info(self, info, texto):
        messagebox.showinfo(info, texto)
 
    def mostrar_aviso(self, info, texto):
        messagebox.showwarning(info, texto)