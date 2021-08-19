
# here put the import lib
import platform

class Settings:
    DEBUG=True 


    SysOS=platform.system()
    if SysOS == "Windows":
        LINUXOS=False 
        DRAWPIC=True
        NWORKER=4 
    else:
        LINUXOS=True 
        DRAWPIC=False 
        NWORKER=31

    POPULATION_SIZE = 31 
    MUTA_RATE = 10     
   
    USE_FORMULA=True
    SQRT_LENTH_SCALE=1.2 


    STOP_GENERATION=1
    SMALLCASE_EXPECTATION=0.84

    ORINGINAL_STRATEGY=False 
    COMPLEX_FIRST_STRATEGY=True 
    COMPLEX_FIRST_AREA_SECOND_STRATEGY=False 
    MIXED_COMPLEX_STRATEGY=False 

    BIN_NORMAL = [[0, 0], [0, 1000], [2000, 1000], [2000, 0]]  
    SQRT_LENTH_SCALE2=2.0  
    SCALE=10.0
    SPACING = 0     
    ROTATIONS = 4   

settings=Settings()