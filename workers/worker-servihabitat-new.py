#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

import os, sys, getopt
import requests
from bs4 import BeautifulSoup
import re
import datetime
from datetime import timedelta
import time
import psycopg2 as pg
import psycopg2.extras

debug = False
provider = 'servihabitat'
dbConn = None
dbCursor = None

def usage():
    print 'uso: %s-worker.py -d' % provider
    print '    --debug,        -d  : imprime información de debugging.'
    sys.exit()

def loadValues(argv):
    global debug
    #---
    try:
        opts, args = getopt.getopt(argv,'hd',[])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ('-d', '--debug'):
            debug = True

def getUrl(pagina):
    return 'https://www.servihabitat.com/es/venta/vivienda/barcelona?p=%d' % pagina

def handle_exception(handler):
    def decorate(func):
        def call_function(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception, e:
                handler(e)
        return call_function
    return decorate

def connectToDatabase():
    global dbConn
    global dbCursor
    #---
    HOST = 'apttoyou-postgresql.czqsvjcidxtf.eu-central-1.rds.amazonaws.com'
    DBNAME = 'apttoyou_db'
    USER = 'apttoyou'
    PASSWORD = 'F7e-QhV-Mfm-ybD'
    PG_CONN_STRING = "host='%s' dbname='%s' user='%s' password='%s'  port='5432'" % (HOST, DBNAME, USER, PASSWORD)
    #---
    if (debug): print '>> Conectando a la base de datos: %s' % (HOST)
    try:
        dbConn = pg.connect(PG_CONN_STRING)
    except psycopg2.DatabaseError, ex:
        print '[ERROR] Problema de conexión a la base de datos: %s' % ex
        sys.exit(1)
    else:
        if (debug): print '>> Conectado a la base de datos con exito!'
        dbCursor = dbConn.cursor()

#-- https://nelsonslog.wordpress.com/2015/04/27/inserting-lots-of-data-into-a-remote-postgres-efficiently/
#-- https://stackoverflow.com/questions/29461933/insert-python-dictionary-using-psycopg2
def insertNewProperty(data):
    global dbConn
    global dbCursor
    global provider
    #---
    i = 0
    TABLE = 't9m1732_%s' % provider
    SQL = """
        INSERT INTO %s (
            realestate,
            propertycode,
            municipality,
            province,
            country,
            url,
            address,
            constructionyear,
            lastRefurbished,
            exterior,
            floor,
            rooms,
            bathrooms,
            size,
            terrace,
            terraceSize,
            heating,
            status,
            storageRoom,
            haslift,
            price
        ) VALUES ({});""" % TABLE
    records_list_template = ','.join(['%s'] * len(data))
    insert_query = SQL.format(records_list_template)
    try:
        dbCursor.execute(insert_query, data)
    except Exception, err:
        print '[ERROR] propertyCode %s (%s): %s' % (str(data[1]), data[5], err)
        if (debug): print (dbCursor.mogrify(insert_query, data).decode('utf8'))
        dbConn.rollback()
        pass
    else:
        i = 1
    dbConn.commit()
    return i

#-- http://www.the-art-of-web.com/sql/upsert/
def updateMainDatabase():
    SQL = 'INSERT INTO public.t9m1732 SELECT * FROM t9m1732_%s ON CONFLICT DO NOTHING;' % provider
    return executeSimpleSql(SQL)

def updateSoldProperties():
    SQL = """
        UPDATE t9m1732 SET sold = CURRENT_DATE WHERE propertycode IN
        (SELECT t1.propertycode
        FROM t9m1732 t1
        LEFT JOIN t9m1732_%s t2 USING(propertycode)
        WHERE t2.propertycode IS NULL AND t1.sold IS NULL AND t1.realestate = '%s');""" % (provider, provider)
    return executeSimpleSql(SQL)

def truncateTempTable():
    SQL = 'TRUNCATE public.t9m1732_%s' % provider
    return executeSimpleSql(SQL)

def executeSimpleSql(SQL):
    rowCount = 0
    try:
        dbCursor.execute(SQL)
    except (Exception, psycopg2.DatabaseError) as error:
        print '[ERROR] %s' % error
        dbConn.rollback()
        pass
    else:
        rowCount = dbCursor.rowcount
    dbConn.commit()
    return rowCount

def getNum(x):
    return int(''.join(ele for ele in x if ele.isdigit()))

def main():
    i = 0
    paginaActual = 1
    totalPaginas = 1
    if (debug): print '>> Procensando %s.' % provider.title()
    os.environ['TZ'] = 'Europe/Madrid'
    time.tzset()
    start_time = time.time()
    f = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')
    h = datetime.datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
    connectToDatabase()
    truncateTempTable()
    while (paginaActual <= totalPaginas):
        try:
            web = requests.get(getUrl(paginaActual))
        except Exception, e:
            print '[ERROR] No se ha podido abrir la página web.\n%s\n' % e
            sys.exit(1)
        if web.status_code != requests.codes.ok:
            print '[ERROR] No se ha podido abrir la página web. (%d)\n' % web.status_code
            sys.exit(1)
        soup = BeautifulSoup(web.content, 'html.parser')
        pagina404 = soup.find('div', { 'class' : 'error404' })
        if (pagina404 is not None):
            print '>> La página %d no se ha podidio cargar' % paginaActual
        else:
            resultados = soup.find('div', { 'class' : 'nido-enlaces' })
            paginador = soup.find('nav', { 'id' : 'topNav' })
            if (paginaActual == 1):
                totalViviendas = int(resultados.find('h2').text.split()[0])
                totalPaginas = int(paginador.find_all('option')[-1].text)
                if (debug):
                    print '>> Se han encontrado %s inmuebles.' % totalViviendas
                    print '>> %s páginas a procesar.' % totalPaginas
                # SQL = """
                #     INSERT INTO control
                #         (proveedor, fecha, hora, totalPaginas, totalInmuebles)
                #     VALUES (%s, %s, %s, %s, %s);"""
                # insert_query = dbCursor.mogrify(SQL, [provider, f, h, totalPaginas, totalViviendas])
                # executeSimpleSql(insert_query)

            divInmuebles = soup.find('ul', { 'class' : 'no-list product-list' })
            inmuebles = divInmuebles.find_all('li', { 'class' : 'product-item' })
            if (debug):
                print '>> Página actual: %d/%d' % (paginaActual, totalPaginas)
                print '  + Número de inmuebles en la página %d: %d' % (paginaActual, len(inmuebles))

            for inm in inmuebles:
                data = []
                detalleTemp = inm.find('section', { 'class' : 'info' }).div.h2.a
                detalleUrl = 'https://www.servihabitat.com' + detalleTemp.get('href')
                idInm = detalleTemp.get('id').replace('link-', '')

                detalleWeb = requests.get(detalleUrl)
                detalleSoup = BeautifulSoup(detalleWeb.content, 'html.parser')

## curl 'https://www.servihabitat.com/api/jsonws/invoke' --data 'cmd=%7B%22%2Fservihabitat-retail-promociones-portlet.promocionessvhjsonws%2Fconsultar-inmuebles-por-pagina%22%3A%7B%22referencia%22%3A%2208110063%22%2C%22tipoOperacion%22%3A%22venta%22%2C%22tipologia%22%3A%22vivienda%22%2C%22listaReferenciasS%22%3A%2281015050%22%2C%22pagina%22%3A1%2C%22elementsPerPage%22%3A5%2C%22scopeGroupId%22%3A20182%2C%22language%22%3A%22es%22%7D%7D'
# {"/servihabitat-retail-promociones-portlet.promocionessvhjsonws/consultar-inmuebles-por-pagina":{"referencia":"08110063","tipoOperacion":"venta","tipologia":"vivienda","listaReferenciasS":"81015050","pagina":1,"elementsPerPage":5,"scopeGroupId":20182,"language":"es"}}

                tituloInm = detalleSoup.find('td', { 'class' : 'tituloInmuebleTD' })
                direccionInmTemp = tituloInm.h1.text.split(',') if tituloInm.h1.a is None else tituloInm.h1.a.div.text.split(',')

                paisInm = 'es'
                provinciaInm = direccionInmTemp[0].strip().split(' ')[1]
                ciudadInm = direccionInmTemp[1].strip()
                direccionInm = tituloInm.h3.text.strip()

                fichaInm = detalleSoup.find('div', { 'class' : 'ficha_typ' })

                tempValue = fichaInm.find('span', { 'class' : 'value' }).text.split(' ')
                opciones = { 'Precio': None, 'Desde': tempValue[1] }
                precioInm = re.sub(r'\.', '', opciones.get(tempValue[0], tempValue[0]))

                listaTemp = detalleSoup.find('div', { 'class' : 'product-main'})
                tempValue = listaTemp.find('li', text = re.compile(r'Superficie'))
                superficieInm = None if tempValue is None else float(re.sub(r'\,', '.', tempValue.text.split('\n')[1].strip()))

                tempValue = listaTemp.find('li', text = re.compile(r'habitaciones'))
                habitacionesInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(u'ba\xf1os'))
                banosInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(r'Terraza'))
                terrazaInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(r'Superficie terraza'))
                supterrazaInm = None if tempValue is None else float(re.sub(r'\,', '.', tempValue.text.split('\n')[1].strip()))

                tempValue = listaTemp.find('li', text = re.compile(u'Situaci\xf3n'))
                situacionInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(u'Calefacci\xf3n'))
                calefaccionInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(u'construcci\xf3n'))
                construccionInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(u'\xfaltima reforma'))
                reformaInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(r'Altura'))
                alturaInm = None if tempValue is None else int(float(re.sub(r'\,', '.', tempValue.text.split('\n')[1].strip())))

                tempValue = listaTemp.find('li', text = re.compile(u'conservaci\xf3n'))
                conservacionInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                tempValue = listaTemp.find('li', text = re.compile(r'Trastero'))
                if tempValue is None:
                    trasteroInm = None
                elif tempValue.a is None:
                    trasteroInm = tempValue.text.split('\n')[1].strip()
                else:
                    trasteroInm = tempValue.a.text.split(' ')[1].strip()
                    #print '%s, %s' % (idInm, trasteroInm)

                tempValue = listaTemp.find('li', text = re.compile(r'Ascensor'))
                ascensorInm = None if tempValue is None else tempValue.text.split('\n')[1].strip()

                data = [ provider, idInm, ciudadInm, provinciaInm, paisInm, detalleUrl, direccionInm, \
                construccionInm, reformaInm, situacionInm, alturaInm, habitacionesInm, banosInm, superficieInm, \
                terrazaInm, supterrazaInm, calefaccionInm, conservacionInm, trasteroInm, ascensorInm, precioInm ]
                i += insertNewProperty(data)

        paginaActual += 1
        if (debug): print '  + %d/%d registros insertados en la tabla de %s.' % (i, totalViviendas, provider)

    n = updateMainDatabase()
    m = updateSoldProperties()

    if (debug):
        print '>> %d/%d registros insertados en la tabla principal.' % (n, totalViviendas)
        print '>> %d propiedades vendidas.' % m

    elapsed_time_secs = time.time() - start_time

    if (debug):
        print '>> Tiempo de ejecución: %s secs.' % timedelta(seconds=round(elapsed_time_secs))
        print '>> Finalizado!.\n'

    SQL = """
        UPDATE control
        SET totalInsertados=%s, totalBaja=%s, tiempoEjecucion=%s
        WHERE fecha=%s AND hora=%s AND proveedor=%s;"""
    update_query = dbCursor.mogrify(SQL, [n, m, elapsed_time_secs, f, h, provider]).decode('utf8')

    executeSimpleSql(update_query)
    dbCursor.close()
    dbConn.close()

if __name__ == '__main__':
    loadValues(sys.argv[1:])
    main()

#-- http://www.postgresqltutorial.com/postgresql-python/connect/
#-- table = bs.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=='Table1')
