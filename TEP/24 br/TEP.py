# -*- coding: utf-8 -*-
from pyomo.environ import *
from pyomo.core import *
from math import pi

model = AbstractModel()

###########################################################################
# SETS
###########################################################################

model.CENT = Set(ordered=True) #Centrales del sistema
model.LINE = Set(ordered=True) #Líneas del sistema
model.BUS = Set(ordered=True) #Barras del sistema
model.ETA = Set(ordered=True) #Etapas de simulación

###########################################################################
# PARAMETERS
###########################################################################

model.frombus   = Param(model.LINE)
model.tobus     = Param(model.LINE)
model.x         = Param(model.LINE)
model.fmax      = Param(model.LINE)
model.n         = Param(model.LINE)
model.nmax      = Param(model.LINE)
model.cost      = Param(model.LINE)

model.location  = Param(model.CENT)

model.year      = Param(model.ETA)

model.demand    = Param(model.ETA, model.BUS)
model.generation= Param(model.ETA, model.CENT)

model.bslack    = Param()
model.Sbase     = Param()

###########################################################################
# SUPER SETS
###########################################################################

def busFrom_init(model, bus): #Líneas con barra de origen i
    retval = []
    for line in model.LINE:
        if model.frombus[line] == bus:
            retval.append(line)
    return retval
model.busFrom = Set(model.BUS, initialize = busFrom_init)

def busTo_init(model, bus): #Líneas con barra de destino i
    retval = []
    for line in model.LINE:
        if model.tobus[line] == bus:
            retval.append(line)
    return retval
model.busTo = Set(model.BUS, initialize = busTo_init)

def busGen_init(model, bus): #Centrales con ubicación en i
    retval = []
    for gen in model.CENT:
        if model.location[gen] == bus:
            retval.append(gen)
    return retval
model.busGen = Set(model.BUS, initialize = busGen_init)

#Hay que explorar otra forma de definir este set por cada tramo
model.circY = RangeSet(1,5)

###########################################################################
# VARIABLES
###########################################################################

# Potencia generada por cada central
def Pgen_bound(model,gen,t):
    return (0, model.generation[t,gen])
model.Pgen=Var(model.CENT, model.ETA, bounds=Pgen_bound, within = NonNegativeReals)

# Ángulos de fase de cada barra
def Theta_bound(model,bus,t):
    return (-2*pi, 2*pi)
model.theta=Var(model.BUS, model.ETA, bounds = Theta_bound)

# Flujos por las líneas, caso base
def f0_bound(model,line,t):
    return (-model.n[line]*model.fmax[line]/model.Sbase, model.n[line]*model.fmax[line]/model.Sbase)
model.f0 = Var(model.LINE, model.ETA, bounds = f0_bound)

# Flujos por las líneas, etapas
model.f = Var(model.LINE, model.circY, model.ETA)

# Decisiones de inversión
model.x_inv = Var(model.LINE, model.circY, model.ETA, within = Binary)

###########################################################################
# CONSTRAINTS
###########################################################################

# Balance nodal
def nodalBal_rule(model,bus,t):
    return sum(model.Pgen[gen,t] for gen in model.busGen[bus])+model.Sbase*(\
           sum(model.f0[i,t]+sum(model.f[i,y,t] for y in model.circY) for i in model.busTo[bus])-\
           sum(model.f0[i,t]+sum(model.f[i,y,t] for y in model.circY) for i in model.busFrom[bus]))-\
           model.demand[t,bus]==0
model.nodalBal = Constraint(model.BUS, model.ETA, rule=nodalBal_rule)

# Flujos caso base
def flow0_rule(model,line,t):
    return model.f0[line,t]*model.x[line] == -model.n[line]*(\
        model.theta[model.frombus[line],t]-\
        model.theta[model.tobus[line],t])
model.flow0 = Constraint(model.LINE, model.ETA, rule=flow0_rule)

# Disyuntivo
def dis1_rule(model,line,y,t):
    value = -2*1.57*(1-model.x_inv[line,y,t])
    value2 = model.f[line,y,t]*model.x[line]+\
             (model.theta[model.frombus[line],t]-\
              model.theta[model.tobus[line],t])
    return value<=value2
model.dis1 = Constraint(model.LINE, model.circY, model.ETA, rule=dis1_rule)

def dis2_rule(model,line,y,t):
    value = 2*1.57*(1-model.x_inv[line,y,t])
    value2 = model.f[line,y,t]*model.x[line]+\
             (model.theta[model.frombus[line],t]-\
              model.theta[model.tobus[line],t])
    return value2<=value
model.dis2 = Constraint(model.LINE, model.circY, model.ETA, rule=dis2_rule)

# Límite de flujos
def limFlow1_rule(model,line,y,t):
    return -model.fmax[line]*model.x_inv[line,y,t]/model.Sbase<=model.f[line,y,t]
model.limFlow1 = Constraint(model.LINE, model.circY, model.ETA, rule=limFlow1_rule)

def limFlow2_rule(model,line,y,t):
    return model.fmax[line]*model.x_inv[line,y,t]/model.Sbase>=model.f[line,y,t]
model.limFlow2 = Constraint(model.LINE, model.circY, model.ETA, rule=limFlow2_rule)

# Consecuencia inversiones (circuitos)
def consecInv_rule(model,line,y,t):
    if y>1:
        return model.x_inv[line,y,t]<=model.x_inv[line,y-1,t]
    else:
        return Constraint.Skip
model.consecInv = Constraint(model.LINE, model.circY, model.ETA, rule=consecInv_rule)

# Temporalidad inversiones
def tempInv_rule(model,line,y,t):
    if t>1:
        return model.x_inv[line,y,t-1]<=model.x_inv[line,y,t]
    else:
        return Constraint.Skip
model.tempInv = Constraint(model.LINE, model.circY, model.ETA, rule=tempInv_rule)

# Máximo de inversiones
def maxInv_rule(model,line,t):
    return sum(model.x_inv[line,y,t] for y in model.circY)<=model.nmax[line]
model.maxInv = Constraint(model.LINE, model.ETA, rule=maxInv_rule)

# Barra slack
def slackBus_rule(model,t):
    return model.theta[model.bslack,t]==0
model.slackBus = Constraint(model.ETA, rule=slackBus_rule)

###########################################################################
# OBJECTIVE FUNCTION
###########################################################################

def objFunction_rule(model):
    value = 0
    for t in model.ETA:
        alpha = 1/(1.1**(model.year[t]-1))
        if t>1:
            value += alpha*sum(model.cost[line]*sum((model.x_inv[line,y,t]-model.x_inv[line,y,t-1])\
                                              for y in model.circY)\
                         for line in model.LINE)
        else:
            value += alpha*sum(model.cost[line]*sum(model.x_inv[line,y,t] for y in model.circY)\
                         for line in model.LINE)
    return value
model.objFunction = Objective(rule=objFunction_rule, sense=minimize)
