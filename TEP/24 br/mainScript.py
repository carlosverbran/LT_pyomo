# -*- coding: utf-8 -*-
from pyomo.environ import *
from pyomo.opt import SolverFactory
import sys
import time
from TEP import model



#---------------------------------------------------------------
#CREACIÓN DEL CASO
#---------------------------------------------------------------
start_time = time.time()
sys.argv = ['caseGenerator_TEP.py', 'ILT-br24.xlsx'] # por ahora se define manualmente el archivo del caso
execfile('caseGenerator_TEP.py')
elapsed_time = '%2.2f' % float(time.time()-start_time)
print 'Tiempo de escritura de caso',elapsed_time,'s'

#---------------------------------------------------------------
#SOLUCION DEL PROBLEMA
#---------------------------------------------------------------
#Se define el optimizador y sus opciones
opt = SolverFactory('gurobi')
opt.options['logfile'] = 'solver.log'
opt.options['optimalitytol']  = 1e-9
opt.options['FeasibilityTol']  = 1e-9
#Se le da una entrada al modelo
#---------------------------------------------------------------
start_time = time.time()
instance = model.create_instance('case.dat')
#Se crea arhivo lp
instance.write('problema.lp', io_options={'symbolic_solver_labels':True})
elapsed_time = '%2.2f' % float(time.time()-start_time)
print 'Tiempo de escritura del problema',elapsed_time,'s'
#---------------------------------------------------------------
#Se resuelve el problema
start_time = time.time()
print "----------------------------------------------------------------\n"
results = opt.solve(instance, tee=True) #tee=True si se quiere ver la solución del solver. De todas formas se encuentra en log
elapsed_time = '%2.2f' % float(time.time()-start_time)
print 'Tiempo de solucion del problema',elapsed_time,'s'
#---------------------------------------------------------------
#Se cargan los resultados a la instancia
instance.solutions.load_from(results)
#Se muestra un resumen de los resultados
#instance.display()
#Se muestra el valor de la función objetivo
#print value(instance.objFunction)

print "----------------------------------------------------------------\n"
print "Branch \t\t From \t To \t y \t t \t Value"
for t in instance.ETA:
    for line in instance.LINE:
        for y in instance.circY:
            value = instance.x_inv[line,y,t].value
            if value!=0:
                fromB = instance.frombus[line]
                toB = instance.tobus[line]
                print "%s \t %s \t %s \t %.1f \t %.1f \t %.1f"%(line,fromB,toB,y,t,value)

raw_input('END OF LINE')
