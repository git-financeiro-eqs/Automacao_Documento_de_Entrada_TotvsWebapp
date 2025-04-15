from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
from tigrinho import tigrinho
from time import sleep
from utils import checar_failsafe
import mensagens
import threading


 
def abrir_gui():
    
    def ativar_robozinho():
        """
        Ativa a automação.
        """
        sleep(1)
        window.iconify()
        threading.Thread(target=tigrinho, daemon=True).start()
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
 
    window.iconbitmap(relative_to_assets("robozinho.ico"))
    window.geometry("750x400+390+110")
    window.title("Automação Entrada de DANFE")
    window.configure(bg = "#FFFFFF")


    canvas = Canvas(
        window,
        bg = "#FFFFFF",
        height = 478,
        width = 788,
        bd = 0,
        highlightthickness = 0,
        relief = "solid"
    )

    canvas.place(x = 0, y = 0)
    button_image_1 = PhotoImage(
        file=relative_to_assets("BotaoPlay.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=3,
        highlightthickness=0,
        bd=3,
        command=lambda: ativar_robozinho(),
        relief="solid",
        cursor="hand2"
    )
    button_1.place(
        x=79.0,
        y=235.0,
        width=590,
        height=60
    )

    image_image_7 = PhotoImage(
        file=relative_to_assets("LogoEqs.png"))
    image_7 = canvas.create_image(
        55.0,
        35.0,
        image=image_image_7
    )


    image_image_8 = PhotoImage(
        file=relative_to_assets("EyeOfTheTiger.png"))
    image_8 = canvas.create_image(
        372.0,
        120.0,
        image=image_image_8
    )
    window.resizable(False, False)
    window.mainloop()
