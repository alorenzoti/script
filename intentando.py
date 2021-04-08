import arcpy
import os
import pandas as pd
from arcpy.management import CopyRaster
from arcpy.sa import ExtractByMask
from arcpy.sa import *
import shutil


arcpy.env.overwriteOutput = True

#Comprobamos si existe la carpeta workspace
existe = os.path.isdir(r"C:\script\workspace")
if existe == True:
    a = (r"C:\script\workspace")
    shutil.rmtree(a)
    os.makedirs(r"C:\script\workspace\tablas")
else:
    os.makedirs(r"C:\script\workspace\tablas")

print("empieza el script")

# Creamos gdb de uso:
pruebaGDB = arcpy.CreateFileGDB_management(r"C:\script\workspace", "datosInput.gdb")





# Inputs:
# Falta input cultivo


# Rutas:
catastro = r"C:\script\catastro\catastrogdb.gdb"
catastro_capa = r"C:\script\catastro\catastrogdb.gdb\Catastro_murcia"
precipitaciones = r"C:\script\climatologia\precipitaciones.gdb"
temperaturasMax = r"C:\script\climatologia\temperaturasMax.gdb"
temperaturasMin = r"C:\script\climatologia\temperaturasMin.gdb"
geologia = r"C:\script\datosConstantes\Geologia.gdb"
geologia_capa = r"C:\script\datosConstantes\Geologia.gdb\litologia"
hidrologia = r"C:\script\datosConstantes\Hidrologia.gdb"
hidrologia_capa = r"C:\script\datosConstantes\Hidrologia.gdb\aguaRaster"
pendiente = r"C:\script\datosConstantes\pendiente.gdb"
pendiente_capa = r"C:\script\datosConstantes\pendiente.gdb\pendiente"

# Realizacion de meses procedentes de input:
# Datos Raster:
# Creamos una lista para iterar las precipitaciones:
espacioTrabajo = arcpy.env.workspace = r"C:\script\climatologia\precipitaciones.gdb"
listaPrecipitaciones = arcpy.ListDatasets("*","Raster")
print(listaPrecipitaciones)

listameses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def pedirentrada():
    mesEntrada = input("introduce un mes de inicio de poliza \t")
    #mesEntrada = arcpy.GetParameterAsText(0)
    mesSalida = input('introduce un mes de fin de poliza \t')
    #mesSalida = arcpy.GetParameterAsText(1)
    return (mesEntrada,mesSalida)



def getperiod(inicio,final):
    """dado inicio y final saca los meses de entre medias"""
    a = listameses.index(inicio)
    b =listameses.index(final)
    return listameses[a:b+1]
assert len(getperiod("enero","febrero"))==2


def recorrer (mesEntrada,mesSalida):
    """recorre el periodo y devuelve y copio los datos en la ruta"""
    periodo = getperiod(mesEntrada,mesSalida)
   # print(f"te vamos a copiar estos datos: {periodo}")
    for mes in periodo:
        #print(f"estoy copiando precipitaciones {mes} ")
        arcpy.management.CopyRaster(mes, os.path.join(r"C:\script\workspace\datosInput.gdb", mes + "Pre"))

       # print(f"estoy copiando temperaturas maximas {mes} ")
        arcpy.env.workspace = r"C:\script\climatologia\temperaturasMax.gdb"
        arcpy.management.CopyRaster(mes, os.path.join(r"C:\script\workspace\datosInput.gdb", mes +"TMax"))

      #  print(f"estoy copiando temperaturas minimas {mes} ")
        arcpy.env.workspace = r"C:\script\climatologia\temperaturasMin.gdb"
        arcpy.management.CopyRaster(mes, os.path.join(r"C:\script\workspace\datosInput.gdb", mes + "TMin"))




inicio,final = pedirentrada()
recorrer(inicio,final)

#### INPUT CATASTRO + SELECT:

input_catastro = input("introduce el numero de parcela catastral \t")
#input_catastro = arcpy.GetParameterAsText(2)

campo = "OBJECTID"

entidadRecorte = arcpy.Select_analysis(catastro_capa,r"C:\script\workspace\datosInput.gdb",campo + "=" + str(input_catastro))
#entidadRecorte = arcpy.Select_analysis(catastro_capa,r"C:\script\workspace\datosInput.gdb",campo + "= '" + str(numero) + "'")


### REALIZAMOS EL CLIP DE CATASTRO CON LOS DATOS CLIMATICOS:
arcpy.env.workspace = r"C:\script\workspace\datosInput.gdb"
lista_capas_gdb = arcpy.ListDatasets("*","Raster")
#print(lista_capas_gdb)

for capa in lista_capas_gdb:
    inRaster = capa
    inMaskData = entidadRecorte
    outExtractByMask = ExtractByMask(inRaster, inMaskData)
    outExtractByMask.save(os.path.join(r"C:\script\workspace\datosInput.gdb", capa +"_recorte"))
   # print(f"estoy recortando {capa}")

#RECORTE DATOS CONSTANTES:

    #RECORTAMOS LA CAPA DE GEOLOGIA
enRaster = geologia_capa
enMaskData = entidadRecorte
outExtractByMask = ExtractByMask(enRaster, enMaskData)
outExtractByMask.save(r"C:\script\workspace\datosInput.gdb\geologia_recorte")
#print("He recortado geologia")

   #RECORTAMOS CAPA DE PENDIENTE:
raster = pendiente_capa
mask = entidadRecorte
outExtractByMask = ExtractByMask(raster, mask)
outExtractByMask.save(r"C:\script\workspace\datosInput.gdb\pendiente_recorte")
#print("he recortado pendiente")

  #RECORTAMOS CAPA DE HIDROLOGÍA:
raster_agua = hidrologia_capa
mask_agua = entidadRecorte
outAgua = ExtractByMask(raster_agua,mask_agua)
outExtractByMask.save(r"C:\script\workspace\datosInput.gdb\hidrologia_recorte")
#print("he recortado hidrologia")



#CREAMOS UNA NUEVA GDB SOLO CON LAS CAPAS DE RECORTE
lista_recorte = arcpy.ListDatasets("*", "Raster")
#print(lista_recorte)

arcpy.CreateFileGDB_management(r"C:\script\workspace", "datos_finales.gdb")
arcpy.env.workspace = r"C:\script\workspace\datos_finales.gdb"


for capa in lista_recorte:
    if len(capa) > 14:
        arcpy.env.workspace = r"C:\script\workspace\datosInput.gdb"
        #print(f"{capa}+esta capa es resultado")
        arcpy.management.CopyRaster(capa, os.path.join(r"C:\script\workspace\datos_finales.gdb", capa + "_def"))
    #elif (len(capa) < 14):
         #print(f"{capa} + tiene menos de 14 caracteres")
    #else:
         #print("no se que esta haciendo")

#TRANSFORMAMOS LOS DATOS A CSV:
arcpy.env.overwriteOutput = True
datos = r"C:\script\workspace\datos_finales.gdb"
arcpy.env.workspace = r"C:\script\workspace\datos_finales.gdb"
lista = arcpy.ListRasters("*", "ALL")

for elemento in lista:
    if arcpy.Exists(os.path.join(r"C:\script\workspace\tablas", elemento+".csv")):
        arcpy.Delete_management(os.path.join(r"C:\script\workspace\tablas", elemento+".csv"))
    arcpy.conversion.TableToTable(elemento, r"C:\script\workspace\tablas", elemento+".csv")
   # print(elemento)

#PANDAS

#1. LISTO LAS TABLAS:
arcpy.env.workspace = r"C:\script\workspace\tablas"
lista2 = arcpy.ListFiles("*.csv")
#print(lista2)


ruta = r"C:\script\workspace\tablas"

#Calculo la media de las columnas Value de los CSVs:

lista_media = []

for me in lista2:
    leercsv = pd.read_csv(os.path.join(ruta, me), sep=";", header=0)
    media = leercsv['Value'].mean()
    lista_media.append(media)
print("A continuacion viene la lista de la media de la columna value de los CSVs")
print(lista_media)




#MULTIPLICO LOS NÚMERO DE LAS LISTAS [a*b*c]
total = 1
for i in lista_media:
    total= total+i
    (total)
dividendo = print("dividendo " + str(total))
longitudlista = len(lista_media)
divisor = print("divisor " + str(longitudlista))


#Numero final de multiplicación entre numero de capas:

division_final = total/longitudlista
print("el resultado es  " + str(division_final))


#Precios seguros:

if (division_final>1 and division_final<2.3):
    print("la vulnerabilidad es máxima")
    print("el seguro a todo riesgo es 3000€")
    print("el seguro a medio riesgo es 2500€")
    print("el seguro a tercero es 2000€")
elif (division_final>2.3 and division_final<4.6):
    print("la vulnerabilidad es media")
    print("el seguro a todo riesgo es 2000€")
    print("el seguro a medio riesgo es 1500€")
    print("el seguro a tercero es 1000€")
elif (division_final>4.6 and division_final<7):
    print("la vulnerabilidad es baja")
    print("el seguro a todo riesgo es 1000€")
    print("el seguro a medio riesgo es 500€")
    print("el seguro a tercero es 250€")
else:
    print("Perdone las molestias, algo ha fallado. Volveremos a calcularlo")



