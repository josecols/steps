#encoding:utf-8
import cv2, numpy
from video import Video

LUMINOSIDAD = 0.55

class Zapato():
    def __init__(self, rectangulo):
        self.x = rectangulo[0][0]               # Coordenada X del centroide
        self.y = rectangulo[0][1]               # Coordenada Y del centroide
        self.w = rectangulo[1][0]               # Ancho
        self.h = rectangulo[1][1]               # Alto
        self.theta = rectangulo[2][0] % 360     # Rotación del rectángulo
               
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getW(self):
        return self.w
    
    def getH(self):
        return self.h
    
    def getTheta(self):
        return self.theta
    
    def getCentroide(self):
        return (self.x, self.y)
    
    def getMinVertice(self):
        return (self.x + self.w / 2, self.y + self.h / 2)
    
    def getMaxVertice(self):
        return (self.x - self.w / 2, self.y - self.h / 2)
    
    def getXMin(self):
        return self.x - (self.w / 2)
    
    def getXMax(self):
        return self.x + (self.w / 2)
    
    def getYMin(self):
        return self.y * 0.9


class Franja():
    def __init__(self, rectangulo, contorno):
        self.x = rectangulo[0][0]               # Coordenada X del centroide
        self.y = rectangulo[0][1]               # Coordenada Y del centroide
        self.w = rectangulo[1][0]               # Ancho
        self.h = rectangulo[1][1]               # Alto
        self.theta = rectangulo[2][0] % 360     # Rotación del rectángulo
        self.contorno = contorno                # Contorno utilizado para comparar
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getW(self):
        return self.w
    
    def getH(self):
        return self.h
    
    def getTheta(self):
        return self.theta
    
    def getContorno(self):
        return self.contorno
    
    def getXMin(self):
        return self.x - (self.w / 2)
    
    def getXMax(self):
        return self.x + (self.w / 2)
    

class Detector():
    def __init__(self, camara, mostrar, adaptable, fAreaMin, fAreaMax, fColorMin, fColorMax, zColorMin, zColorMax): 
        self.video = Video(camara)                  # Vídeo empleado para la detección
        self.mostrar = mostrar                      # Indica si se debe mostrar el resultado en vídeo
        self.adaptable = adaptable                  # Adapta los algoritmos de detección a los niveles de luz
        self.franjas = []                           # Lista de franjas
        self.zapatos = []                           # Lista de zapatos
        self.fAreaMin = fAreaMin                    # Área mínima de una franja
        self.fAreaMax = fAreaMax                    # Área máxima de una franja
        self.fColorMin = fColorMin                  # Valor mínimo del rango de color de una franja
        self.fColorMax = fColorMax                  # Valor máximo del rango de color de una franja
        self.zColorMin = zColorMin                  # Valor mínimo del rango de color de un zapato
        self.zColorMax = zColorMax                  # Valor máximo del rango de color de una zapato
              
    def detectarFranjas(self):   
        if (self.adaptable):
            self.adaptarLuz("franjas")
             
        self.restablecerFranjas()
        grises = cv2.cvtColor(self.video.getCuadro(), cv2.COLOR_BGR2GRAY)        
        cv2.inRange(grises, self.fColorMin, self.fColorMax, grises)            
        contornos, _ = cv2.findContours(grises, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for _, contorno in enumerate(contornos):
            borde = cv2.minAreaRect(contorno)   
            rectangulo = cv2.cv.BoxPoints(borde)                            
            area = cv2.contourArea(numpy.int0(rectangulo))
            if (self.fAreaMin < area < self.fAreaMax and 680 > rectangulo[0][0] > 80):
                franja = Franja(rectangulo, contorno)
                self.franjas.append(franja)
                if self.mostrar:
                    self.video.dibujarRectangulo(numpy.int0(rectangulo))
                    
        self.franjas.sort(key=lambda xMin : xMin.getXMin())
        
        if self.mostrar:
            self.video.mostrarCuadro()
    
    def detectarZapatos(self):         
        if (self.adaptable):
            self.adaptarLuz("zapato")
        
        self.restablecerZapatos()
        imgHSV = cv2.cvtColor(self.video.getCuadro(), cv2.COLOR_BGR2HSV)
        filtro = cv2.inRange(imgHSV, self.zColorMin, self.zColorMax)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        filtro = cv2.morphologyEx(filtro, cv2.MORPH_OPEN, kernel)                
        contornos, _ = cv2.findContours(filtro, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for _, contorno in enumerate(contornos):
            borde = cv2.minAreaRect(contorno)   
            rectangulo = cv2.cv.BoxPoints(borde)    
            zapato = Zapato(rectangulo)
            if self.mostrar:
                self.video.dibujarRectangulo(numpy.int0(rectangulo))
            self.zapatos.append(zapato)     
            
        if self.mostrar:   
            self.video.mostrarCuadro()
            
    def adaptarLuz(self, tipo):
        luminosidad = self.video.getLuminosidad()
        if (tipo == "franjas"):
            self.fColorMin = int(60 + 2.5 * luminosidad)
            self.fColorMax = 255              
            print(self.fColorMin)       
        elif (tipo == "zapato"):              
            hMin = int(118 - (luminosidad / 100) * 23)
            sMin = int(255 - (luminosidad / 100) * 160)
            vMin = int(45 + (luminosidad / 100) * 110)
            hMax = int(130 - (luminosidad / 100) * 20)
            self.zColorMin = numpy.array([hMin, sMin, vMin], numpy.uint8)
            self.zColorMax = numpy.array([hMax, 255, 255], numpy.uint8)
    
    def getZapatos(self):
        return self.zapatos
    
    def getFranjas(self):
        return self.franjas
    
    def getVideo(self):
        return self.video
    
    def restablecerFranjas(self):
        del self.franjas[0:len(self.franjas)]
        
    def restablecerZapatos(self):
        del self.zapatos[0:len(self.zapatos)]