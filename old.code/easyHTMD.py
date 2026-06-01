#########-#########-#########-#########-#########-#########-#########-#########-#########-#########
# program: easyHTMD - A in house program to perform High-Throughput MD for protein/protein-ligand/
#          systems
# author:  Ropón-Palacios G.
# e-mail:  groponp@gmail.com
# data   : Fri 8, Sep at 22:39  
# 
# Change logs 
#  text :: code line :: data :: programmer 
#########-#########-#########-#########-#########-#########-#########-#########-#########-######### 


import sys 
import os 

class IO:
    def __init__(self) -> None:
        pass

    def message(string, tm):
        if tm == "INFO":
            print("[INFO    ] {}".format(string))
        elif tm == "WARNING":
            print("[WARNING ] {}".format(string))
        else: 
            print("[ERROR   ] {}".format(string))


class Solution:
    def __init__(self, iPDB, oGRO, water_model, ff):
        self.iPDB = iPDB
        self.oGRO = oGRO 
        self.water_model = water_model
        self.ff = ff 

    def pdb2gmx(self):
        IO.message("Running pdb2gmx", tm="INFO")
        os.system("gmx")



class Complex:
    def __init__(self) -> None:
        pass

