import threading
import queue
import utils
import time
import pyautogui as ptg
from typing import Optional, Set


class ContingenciaMonitor:
    def __init__(self):
        self.encerrar = threading.Event()
        self.fila = queue.Queue()
        self.erros_ativos: Set[str] = set()
        self.thread_monitoramento: Optional[threading.Thread] = None
        self.lock = threading.Lock()


    def encontrar_erro_geral(self) -> Optional[tuple]:
        """Tenta encontrar qualquer um dos erros inesperados de forma sequencial"""
        imagens = [
            r'src\Imagens\ErroInesperado.png',
            r'src\Imagens\ErroInesperado2.png',
            r'src\Imagens\ErroInesperado3.png'
        ]
        
        for imagem in imagens:
            if self.encerrar.is_set():
                return None
                
            try:
                coordenadas = utils.encontrar_centro_imagem(imagem)
                if coordenadas:
                    return coordenadas
            except ptg.FailSafeException:
                raise
            except Exception:
                continue
        
        return None
    

    def monitorar(self):
        """Loop principal de monitoramento com tratamento de recursos"""
        try:
            while not self.encerrar.is_set():
                try:
                    if 'ValItemErrado' in self.erros_ativos:
                        val_item = utils.encontrar_centro_imagem(r'src\Imagens\ValItemErrado.png')
                        if val_item:
                            with self.lock:
                                self.fila.put("ValItemErrado")
                    
                    erro_geral = self.encontrar_erro_geral()
                    if erro_geral:
                        with self.lock:
                            self.fila.put("ErroGeral")
                    
                    time.sleep(0.5)
                    
                except ptg.FailSafeException:
                    with self.lock:
                        self.fila.put("FailSafeAcionado")
                    break
                except Exception as e:
                    print(f"[Monitor] Erro: {str(e)}")
                    time.sleep(1)
                    
        finally:
            self.limpar_recursos()


    def limpar_recursos(self):
        """Garante a liberação de recursos"""
        with self.lock:
            while not self.fila.empty():
                try:
                    self.fila.get_nowait()
                except queue.Empty:
                    pass


    def iniciar(self, erros=None):
        """Inicia uma nova thread de monitoramento"""
        if self.thread_monitoramento and self.thread_monitoramento.is_alive():
            self.parar()
            
        self.erros_ativos = set(erros or [])
        self.encerrar.clear()
        self.thread_monitoramento = threading.Thread(
            target=self.monitorar,
            daemon=True,
            name="ThreadMonitoramento"
        )
        self.thread_monitoramento.start()



    def parar(self):
        """Versão à prova de falhas para encerramento"""
        if not hasattr(self, 'thread_monitoramento') or not self.thread_monitoramento:
            return

        self.encerrar.set()

        if (threading.current_thread() != self.thread_monitoramento and 
            self.thread_monitoramento.is_alive()):
            
            self.thread_monitoramento.join(timeout=1.0)

        self.limpar_recursos()
        self.thread_monitoramento = None
        print(threading.enumerate())



    def obter_erro(self, timeout=None):
        """Obtém o próximo erro da fila com thread-safe"""
        try:
            with self.lock:
                return self.fila.get(timeout=timeout)
        except queue.Empty:
            return None
        

    def __enter__(self):
        return self
    
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.parar()


    def __del__(self):
        """Destruidor seguro - versão simplificada"""
        if hasattr(self, 'encerrar') and not self.encerrar.is_set():
            self.parar()