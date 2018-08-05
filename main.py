#encoding:utf-8
import pickle, cv2, threading, pyaudio, wave
from detector import Detector
from calibrar import AREA_MAX, AREA_MIN, AZUL_MAX, AZUL_MIN, BLANCO_MAX, BLANCO_MIN

NOTAS = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C1']
  
class Reproductor(threading.Thread):
    """Esta clase debe heredar de Thread para que la reproducción del sonido sea asíncrona.
    Esta implementación permite que en un futuro STEPS soporte múltiples usuarios simultáneos"""  
    def __init__(self, tecla):  
        threading.Thread.__init__(self)    
        self.tecla = tecla
           
    def run(self):  
        segmento = 1024
        archivo = wave.open('audio/%s.wav' % self.tecla, 'rb')
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=audio.get_format_from_width(archivo.getsampwidth()),
            channels=archivo.getnchannels(),
            rate=archivo.getframerate(),
            output=True)
        data = archivo.readframes(segmento)
        
        while data != '':
            stream.write(data)
            data = archivo.readframes(segmento)
        
        stream.close()
        audio.terminate()

class Piano:
    def __init__(self):
        self.fYMin = open("limite.txt", "r")
        self.fFranjas = open("franjas.obj", "rb") 
        self.yMin = self.fYMin.read()
        self.franjas = pickle.load(self.fFranjas)
        self.franjas = self.franjas[:8]
        self.camara1 = Detector(1, True, False, AREA_MIN, AREA_MAX, BLANCO_MIN, BLANCO_MAX, AZUL_MIN, AZUL_MAX)    # Cámara del suelo
        self.camara2 = Detector(0, True, False, AREA_MIN, AREA_MAX, BLANCO_MIN, BLANCO_MAX, AZUL_MIN, AZUL_MAX)    # Cámara de la cabina
        self.presionada = False
        
    def teclaPresionada(self, zapato):
        for i, franja in enumerate(self.franjas):
            if (cv2.pointPolygonTest(franja.getContorno(), zapato.getCentroide(), True) >= 0):
                return i
        return None
                    
    def iniciar(self):    
        self.camara1.restablecerZapatos()
        self.camara2.restablecerZapatos() 
        
        while (len(self.camara1.getZapatos()) == 0):
            self.camara1.detectarZapatos() 
            self.camara2.detectarZapatos()                                  
        zapato = self.camara1.getZapatos()[0]        
        
        if (zapato.getYMin() >= float(self.yMin)):
            if (self.presionada == False):
                self.presionada = True                
                while (len(self.camara2.getZapatos()) == 0):
                    self.camara2.detectarZapatos()                                     
                zapato = self.camara2.getZapatos()[0]                
                tecla = self.teclaPresionada(zapato)
                if (tecla != None):
                    print("Hay alguien en la tecla %d" % tecla)
                    self.sonar(tecla)
                else:
                    print("Hay alguien tocando el piso pero no una tecla")
        else:
            self.presionada = False
            
        
    def detener(self):
        self.fYMin.close()
        self.fFranjas.close()
        
    def sonar(self, tecla):    
        reproductor = Reproductor(NOTAS[tecla])
        reproductor.start()


if __name__ == "__main__":
    piano = Piano()
    while (True):
        piano.iniciar()
        if (cv2.waitKey(27) != -1):
            piano.detener()                  
            break        
