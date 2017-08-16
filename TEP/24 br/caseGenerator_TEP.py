# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#se importa librería xlrd para leer archivo base
from xlrd import open_workbook
#se abre el archivo como wb
import sys
arch = sys.argv[1]
#wb = open_workbook('ILT-br24.xlsx')
wb = open_workbook(arch)
#se abre un archivo para ir escribiendo el caso
case = open('case.dat', 'w')
#--------------------------------------------------------------------
#Funciones auxiliares de escritura
#función para escribir los sets
def wrSets(ws,case):
    nrows = ws.nrows
    cell = ws.cell(1,0)
    if cell.ctype==1: #ctype 1 indica que es un string
        for row in range(1,nrows):
            case.write(str(ws.cell(row,0).value)+' ')
    else:
        for row in range(1,nrows):
            case.write(str(int(ws.cell(row,0).value))+' ')
    case.write(';\n')
#función para hacer los sets de bloques de tiempos
def wrTime(ws,case):
    nrows = ws.nrows
    for i in range(1,nrows):
        case.write(str(i)+' ')
    case.write(';\n')
#función para escribir los parámetros
def wrParams(ws,nrows,ncols,case):
    for row in range(1,nrows):
        for col in range(ncols):
            value = ws.cell(row,col).value
            case.write(str(value)+' ')
        case.write('\n')
#función para escribir los parámetros de inversión
def wrInv(ws,indx,case):
    nrows = ws.nrows
    for row in range(1,nrows):
        for idx in indx:
            value = ws.cell(row,idx).value
            case.write(str(value)+' ')
        case.write('\n')
#--------------------------------------------------------------------
#Sets
#Generadores
case.write('set CENT := ')
ws = wb.sheet_by_name('Generators')
wrSets(ws,case)
#Líneas
case.write('set LINE := ')
ws = wb.sheet_by_name('Lines')
wrSets(ws,case)
#Barras
case.write('set BUS := ')
ws = wb.sheet_by_name('Buses')
nrows = ws.nrows
for i in range(1,nrows):
    case.write(str(i)+' ')
case.write(';\n')
#Cantidad de etapas
case.write('set ETA := ')
ws = wb.sheet_by_name('Demand')
wrTime(ws,case)
#--------------------------------------------------------------------
#Parámetros técnicos
#Transmisión
case.write('param: frombus tobus x fmax n nmax cost :=\n')
ws = wb.sheet_by_name('Lines')
nrows = ws.nrows
ncols = 8
wrParams(ws,nrows,ncols,case)
case.write(';\n')
#Barras
##case.write('param: bindx :=\n')
##ws = wb.sheet_by_name('Buses')
##nrows = ws.nrows
##ncols = 2
##wrParams(ws,nrows,ncols,case)
##case.write(';\n')
#Generadores
case.write('param: location :=\n')
ws = wb.sheet_by_name('Generators')
nrows = ws.nrows
ncols = ws.ncols
wrParams(ws,nrows,ncols,case)
case.write(';\n')
#--------------------------------------------------------------------
#Parámetros temporales
#Demandas
case.write('param demand:\n')
ws = wb.sheet_by_name('Demand')
nrows = ws.nrows
ncols = ws.ncols
#se escriben los índices de la demanda
for i in range(1,ncols-1):
    case.write(str(i)+' ')
case.write(':=\n')
#se llena la matriz de demandas
for t in range(1,nrows):
    case.write(str(t)+' ')
    for bus in range(2,ncols):
        value = ws.cell(t,bus).value
        case.write(str(value)+' ')
    case.write('\n')
case.write(';\n')
#Generación
case.write('param generation:\n')
ws = wb.sheet_by_name('Generation')
nrows = ws.nrows
ncols = ws.ncols
#se escriben los índices de la generación
for i in range(2,ncols):
    value = ws.cell(0,i).value
    case.write(str(value)+' ')
case.write(':=\n')
#se llena la matriz de generación
for t in range(1,nrows):
    case.write(str(t)+' ')
    for bus in range(2,ncols):
        value = ws.cell(t,bus).value
        case.write(str(value)+' ')
    case.write('\n')
case.write(';\n')
#Identificación de año
case.write('param: year :=\n')
for t in range(1,nrows):
    case.write(str(t)+' ')
    case.write(str(ws.cell(t,0).value)+'\n')
case.write(';\n')
#--------------------------------------------------------------------
#Barra slack
case.write('param bslack := ')
ws = wb.sheet_by_name('Buses')
case.write(str(ws.cell(1,2).value)+' ;\n')
#Sbase
case.write('param Sbase := ')
ws = wb.sheet_by_name('Lines')
case.write(str(ws.cell(1,8).value)+' ;\n')
#--------------------------------------------------------------------
#se cierra el archivo de escritura
case.close()
