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
provider = 'tecnocasa'
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
    #return 'http://www.tecnocasa.es/anuncios/piso/cataluna/barcelona/barcelona.html/pag-%d' % pagina
    return 'http://www.tecnocasa.es/anuncios/piso/cataluna/barcelona.html/pag-%d' % pagina

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
            neighborhood,
            constructionyear,
            propertytype,
            rooms,
            size,
            haslift,
            price
        ) VALUES ({});""" % TABLE
    records_list_template = ','.join(['%s'] * len(data))
    insert_query = SQL.format(records_list_template)
    try:
        dbCursor.execute(insert_query, data)
        #print (dbCursor.mogrify(insert_query, data).decode('utf8'))
    except Exception, err:
        print '[ERROR] propertyCode %s: %s' % (str(data[1]), err)
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
        paginador = soup.find('ul', { 'class' : 'pagination' })
        if (paginaActual == 1):
            totalViviendas = int(soup.find('div', { 'class' : 'numeroRisultatiImmobile' }).text.split()[3])
            totalPaginas = getNum(paginador.find_all('a')[-1].attrs['href'])
            if (debug):
                print '>> Se han encontrado %d inmuebles.' % totalViviendas
                print '>> %s páginas a procesar.' % totalPaginas
            SQL = """
                INSERT INTO control
                    (proveedor, fecha, hora, totalPaginas, totalInmuebles)
                VALUES (%s, %s, %s, %s, %s);"""
            insert_query = dbCursor.mogrify(SQL, [provider, f, h, totalPaginas, totalViviendas])
            executeSimpleSql(insert_query)

        paginaActual = int(paginador.find('li', { 'class' : 'active' }).find('a').text)

        inmuebles = soup.find_all(class_='immobiliListaAnnuncio')
        if (debug):
            print '>> Página actual: %d/%d' % (paginaActual, totalPaginas)
            print '  + Número de inmuebles en la página %d: %d' % (paginaActual, len(inmuebles))

        for inm in inmuebles:
            data = []
            detalleUrl = inm.find('a', { 'class' : 'immobileLink' }).attrs['href']
            detalleWeb = requests.get(detalleUrl)
            detalleSoup = BeautifulSoup(detalleWeb.content, 'html.parser')
            precioInm = re.sub(r'\.', '', detalleSoup.find('span', { 'class' : 'immobilePrezzo' }).text.split(' ')[0])
            idInm = detalleSoup.find('span', { 'class' : 'schedaAnnuncioRiferimento' }).text.split(' ')[1]
            detallesInm = detalleSoup.find('div', { 'class' : 'schedaAnnuncioCampi' })
            paisInm = 'es'
            strongInm = detallesInm.find('strong', text = 'Provincia')
            provinciaInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].strip()
            strongInm = detallesInm.find('strong', text = 'Ciudad')
            ciudadInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].strip()
            strongInm = detallesInm.find('strong', text = 'Zona')
            zonaInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].split('-')[0].strip()
            strongInm = detallesInm.find('strong', text = 'Tipología')
            tipoInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].strip()
            strongInm = detallesInm.find('strong', text = 'Superficie')
            superficieInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].split(' ')[0].strip()
            strongInm = detallesInm.find('strong', text = 'Habitaciones')
            habitacionesInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].strip()
            strongInm = detallesInm.find('strong', text = 'Subtipología')
            dormitoriosInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].split(' ')[0].strip()
            strongInm = detallesInm.find('strong', text = 'Año de construcción')
            construccionInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].strip()
            strongInm = detallesInm.find('strong', text = 'Categoría')
            categoriaInm = None if strongInm is None else strongInm.next_sibling.split('\n')[1].strip()
            serviciosInm = detalleSoup.find('div', { 'class' : 'serviziAnnuncioCampi'})
            servicioInm = None if serviciosInm is None else serviciosInm.find('li', text = ' - Ascensor ')
            ascensorInm = None if servicioInm is None else 'True'

            data = [ provider, idInm, ciudadInm, provinciaInm, paisInm, detalleUrl, zonaInm, construccionInm, tipoInm, habitacionesInm, superficieInm, ascensorInm, precioInm ]
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
