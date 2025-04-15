from tkinter import messagebox

class Mensagens:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        self.info = " Bem-vindo ao Bot.Contabil!"
        self.texto = """A seguir, você verá a nossa interface de controle da automação. Nela temos:
 
Botão "Play": Esse botão é o que ativa o Bot, ele só precisa ser acionado 1x, e quando acionado, efetue o login no Microsiga, abra a rotina Processo Pagamento e então tire as mãos do mouse e do teclado e deixe a mágica acontecer.

"""

        self.info2 = "Fiscal IO"
        self.texto2 = """Ao lado do bot temos a plataforma Fiscal IO. Nela você baixa todos os XMLs necessários para que o bot realize os lançamentos.

Vou deixer um breve manual de como baixar os XMLs nessa plataforma."""

        self.info4 = "Como operar"
        self.texto4 = """Modo de operar:
 
Acione a automação no "botão Play" e aguarde o bot abrir a tela de login do Microsiga. 
No Microsiga, logue no usuário bot.contabil (Usuário: ******** Senha: *********);
Em seguida, vá para a rotina "Processo Pagamento" no módulo Compras; faça o filtro que desejar, mas, atente-se para o tipo de nota fiscal que será lançada, o bot só realiza os lançamentos de mercadoria!
 
Para interromper ou finalizar a execução do bot, basta levar o cursor do mouse até o limite do canto superior esquerdo da sua tela e aguardar 10 segundos ou fechar a janela do Microsiga.

"""

        self.info5 = "Atenção!"
        self.texto5 = """Atenção!

Como mencionado anteriormente, nosso servidor está sempre sobrecarregado, o que pode gerar instabilidade no bot durante sua execução, fazendo-o "crachar" e não conseguir lançar mais nenhum processo. Se acaso perceber algum desses momentos de instabilidade do servidor, verifique se o bot continua execultando seus lançamentos ou se está travado em alguma tela. Se estiver travado, realize o procedimento de interrupção, depois inicialize o usuario novamente e então reacione o robô. Devido alguns momentos de instabilidade serem imperceptiveis, aconcelho que verifique o monitor do bot no mínimo 1x a cada duas horas."""


    def mostrar_info(self, info, texto):
        messagebox.showinfo(info, texto)

    def mostrar_aviso(self, info, texto):
        messagebox.showwarning(info, texto)

    def mostrar_erro(self, texto):
        messagebox.showerror("Cuidado!", texto)
