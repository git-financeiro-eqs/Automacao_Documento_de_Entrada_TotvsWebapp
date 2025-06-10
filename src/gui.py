from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
from tigrinho import tigrinho
from time import sleep
from utils import checar_failsafe
import mensagens
import threading


 
def abrir_gui():
    
    def ativar_robozinho(empresa):
        """
        Ativa a automação.
        """
        sleep(1)
        window.iconify()
        threading.Thread(target=tigrinho, args=(empresa, ), daemon=True).start()
        checar_failsafe()
        
 
    OUTPUT_PATH = Path(__file__).parent
    ASSETS_PATH = OUTPUT_PATH / Path(r"Imagens\InterfaceGrafica")
 

    def relative_to_assets(path: str) -> Path:
        """
        Retorna o caminho absoluto para um arquivo na pasta de assets.
        """
        return ASSETS_PATH / Path(path)


    window = Tk()

    bot = mensagens.Mensagens(window)
 
    bot.mostrar_info(bot.info, bot.texto)
    bot.mostrar_info(bot.info2, bot.texto2)
    bot.mostrar_info(bot.info4, bot.texto4)
    bot.mostrar_aviso(bot.info5, bot.texto5)
 
    window.deiconify()
 
    window.geometry("700x520+390+75")
    window.title("Automação Entrada de DANFE")
    window.iconbitmap(relative_to_assets("robozinho.ico"))
    window.configure(bg = "#FFFFFF")


    canvas = Canvas(
        window,
        bg = "#FFFFFF",
        height = 520,
        width = 700,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    button_image_1 = PhotoImage(
        file=relative_to_assets("BotaoPlay.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=3,
        highlightthickness=0,
        bd=3,
        command=lambda: ativar_robozinho("Bratec"),
        relief="solid",
        cursor="hand2"
    )
    button_1.place(
        x=112.0,
        y=420.0,
        width=471.0,
        height=51.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("BotaoPlay.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=3,
        highlightthickness=0,
        bd=3,
        command=lambda: ativar_robozinho("EQS"),
        relief="solid",
        cursor="hand2"
    )
    button_2.place(
        x=112.0,
        y=294.0,
        width=471.0,
        height=51.0
    )

    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        371.0,
        259.0,
        image=image_image_1
    )

    image_image_2 = PhotoImage(
        file=relative_to_assets("image_2.png"))
    image_2 = canvas.create_image(
        317.0,
        261.0,
        image=image_image_2
    )

    image_image_3 = PhotoImage(
        file=relative_to_assets("image_3.png"))
    image_3 = canvas.create_image(
        350.0,
        123.0,
        image=image_image_3
    )

    image_image_4 = PhotoImage(
        file=relative_to_assets("image_4.png"))
    image_4 = canvas.create_image(
        347.0,
        391.0,
        image=image_image_4
    )
    window.resizable(False, False)
    window.mainloop()
