#encoding:utf-8
import cv2

class Video():
    def __init__(self, camara):
        self.indiceCamara = camara                  # Índice en el arreglo de dispositivos del computador 
        self.camara = cv2.VideoCapture(camara)      # Stream de vídeo de la cámara seleccionada
        self.cuadro = None                          # Último cuadro leído por la cámara
        self.luminosidad = 0                        # Luminosidad del cuadro
        
    def getCuadro(self):
        _, cuadro = self.camara.read()
        self.cuadro = cuadro        
        return cuadro
    
    def setCamara(self, camara):
        self.camara = cv2.VideoCapture(camara)
        
    def mostrarCuadro(self):
        cv2.imshow("Paso Musical" + " - Camara" + str(self.indiceCamara), self.cuadro)
        
    def dibujarRectangulo(self, rectangulo):
        cv2.drawContours(self.cuadro, [rectangulo], 0, (0, 0, 255), 2)
        
    def calcularLuminosidad(self):
        """"La luminosidad es calculada con Y' a través el modelo de color YUV"""
        media = cv2.mean(self.getCuadro())
        self.luminosidad = ((0.299 * media[2] + 0.587 * media[1] + 0.144 * media[0]) * 100) / 262.65
        
    def getLuminosidad(self):        
        while (self.luminosidad < 1):
            self.calcularLuminosidad()
        return self.luminosidad
