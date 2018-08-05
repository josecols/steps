#encoding:utf-8
import cv2, numpy, sys, pickle
from detector import Detector

AREA_MIN = 1000
AREA_MAX = 10000
AZUL_MIN = numpy.array([100, 150, 110], numpy.uint8)
AZUL_MAX = numpy.array([130, 255, 255], numpy.uint8)
BLANCO_MIN = cv2.mean((200, 200, 200))
BLANCO_MAX = cv2.mean((255, 255, 255))

class Calibrador():
    def __init__(self, camara):                
        self.detector = Detector(camara, True, False, AREA_MIN, AREA_MAX, BLANCO_MIN, BLANCO_MAX, AZUL_MIN, AZUL_MAX)        
    
    def calibrar(self, tipo):                    
        if (tipo == "franjas"):
            self.franjas = open("franjas.obj", "wb")
            self.detector.detectarFranjas()
        elif (tipo == "zapato"):
            self.yMin = open("limite.txt", "w")
            self.detector.detectarZapatos()
        else:
            print("No se reconoce el parámetro: '%s'" % tipo)
            sys.exit(0)
    
    def guardar(self, tipo):
        if (tipo == "franjas"):
            pickle.dump(self.detector.getFranjas(), self.franjas)
            self.franjas.close() 
        elif (tipo == "zapato"):
            self.yMin.write("%d" % self.detector.getZapatos()[0].getYMin())         
            self.yMin.close()
            
if __name__ == "__main__":
    if (len(sys.argv) > 2):
        calibrador = Calibrador(int(sys.argv[2]))
    else:
        calibrador = Calibrador(0)
    while True:           
        calibrador.calibrar(sys.argv[1])        
        if (cv2.waitKey(27) != -1):      
            calibrador.guardar(sys.argv[1])
            break
        

