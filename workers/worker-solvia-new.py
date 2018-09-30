#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

# curl 'https://www.solvia.es/api/search/Geo' \
# -XPOST \
# -H 'Content-Type: application/json' \
# -H 'Referer: https://www.solvia.es/es/resultadosOportunidades?landing=1&filtroTipo=compra&idProvincia=8&viewMode=map' \
# -H 'Accept: */*' \
# -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4' \
# -H 'Origin: https://www.solvia.es' \
# -H 'x-solv-idioma: 1' \
# -H 'x-solv-land: 1' \
# -H 'x-solv-token: ' \
# -H 'x-solv-version: 1' \
# --data-binary $'{\n  "filtroTipo": "compra",\n  "idProvincia": "8"\n}'

# curl 'https://www.solvia.es/api/search/searchByIdList' \
# -XPOST \
# -H 'Content-Type: application/json' \
# -H 'Referer: https://www.solvia.es/es/propiedades/comprar/locales-barcelona-51025-64991' \
# -H 'Accept: */*' \
# -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4' \
# -H 'Origin: https://www.solvia.es' \
# -H 'x-solv-idioma: 1' \
# -H 'x-solv-land: 1' \
# -H 'x-solv-token: ' \
# -H 'x-solv-version: 1' \
# --data-binary $'{\n  "idsVivienda": [\n    60971,\n    64991,\n    1402\n  ]\n}'

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
provider = 'solvia'
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
    return 'https://www.solvia.es/resultadosOportunidades.asp?numImagenes=15&idCategoriaTipoVivienda=1&categoriaTipoVivienda=Viviendas&idProvincia=8&filtroTipoObraNueva=S&filtroTipoObraCurso=S&filtroTipoSegundaMano=S&nav=%d&mapa=N&web=O' % pagina

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
    if debug: print '>> Conectando a la base de datos: %s' % (HOST)
    try:
        dbConn = pg.connect(PG_CONN_STRING)
    except psycopg2.DatabaseError, ex:
        print '[ERROR] Problema de conexión a la base de datos: %s' % ex
        sys.exit(1)
    else:
        if debug: print '>> Conectado a la base de datos!'
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
            address,
            status,
            rooms,
            size,
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
    SQL = 'truncate public.t9m1732_%s' % provider
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

def main():
    i = 0
    paginaActual = 1
    totalPaginas = 1
    if debug: print '>> Procensando %s.' % provider.title()
    os.environ['TZ'] = 'Europe/Madrid'
    time.tzset()
    start_time = time.time()
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
        marcadorPagina = soup.find('select', { 'class' : 'divMarcadorPaginaSig2', 'name' : 'pagina' })
        if (paginaActual == 1 and debug):
            totalViviendas = int(soup.find(id = 'resultados').b.string)
            print '>> %d viviendas a procesar.' % totalViviendas
            totalPaginas = len(marcadorPagina.find_all('option'))
            print '>> %d páginas a procesar.' % totalPaginas
            selectResultados = soup.find('select', { 'class' : 'divMarcadorPaginaSig2', 'name' : 'numInmuebles' })
            resultadosPagina = int(selectResultados.find('option', selected = True).string)
            print '>> %d resultados por pagina.' % resultadosPagina
            SQL = """
                INSERT INTO control
                    (proveedor, fecha, totalPaginas, totalInmuebles)
                VALUES (%s, %s, %s, %s);"""
            t = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            insert_query = dbCursor.mogrify(SQL, [provider, t, totalPaginas, totalViviendas])
            executeSimpleSql(insert_query)

        try:
            paginaActual = int(marcadorPagina.find('option', selected = True).string)
        except Exception, e:
            print marcadorPagina

        inmuebles = soup.find_all(class_ = 'cuadro_inmueble', id = re.compile('^inm_'))
        if debug:
            print '>> Página actual: %d/%d' % (paginaActual, totalPaginas)
            print '  + Número de viviendas en la página %d: %d' % (paginaActual, len(inmuebles))

        for inm in inmuebles:
            idInm= inm.attrs['id'].split('_')[1]
            campos = inm.find_all('span')
            urlInm = campos[0].a.attrs['href'].strip()
            estadoInmTemp = campos[0].a.findAll('img')
            estadoInm = estadoInmTemp[1].attrs['title'] if len(estadoInmTemp) > 1 else None
            descInm = campos[1].a.b.string.strip()
            direccionInm = campos[1].text.split('\n')[3].strip()
            munInm = campos[1].text.split('\n')[4].strip()
            provInm = 'Barcelona'
            paisInm = 'es'
            supInm = re.sub(r'desde', '', campos[2].text.strip().split()[0])
            habInmTemp = re.sub(r'desde', '', campos[3].text.strip().split()[0])
            habInm = habInmTemp if habInmTemp != '--' else None
            precioInmTemp = re.sub(r'\.', '', campos[6].text.strip()).split()
            opciones = { 'Precio': None, 'Desde': precioInmTemp[1] }
            precioInm = opciones.get(precioInmTemp[0], precioInmTemp[0])

            data = [ provider, idInm, munInm, provInm, paisInm, urlInm, direccionInm, estadoInm, habInm, supInm, precioInm ]
            i += insertNewProperty(data)

        paginaActual += 1
        if debug: print '  + %d/%d registros insertados en la tabla de %s.' % (i, totalViviendas, provider)

    n = updateMainDatabase()
    m = updateSoldProperties()

    if debug:
        print '>> %d/%d registros insertados en la tabla principal.' % (n, totalViviendas)
        print '>> %d propiedades vendidas.' % m

    elapsed_time_secs = time.time() - start_time

    if debug:
        print '>> Tiempo de ejecución: %s secs.' % timedelta(seconds=round(elapsed_time_secs))
        print '>> Finalizado!.\n'

    SQL = """
        UPDATE control
        SET totalInsertados=%s, totalBaja=%s, tiempoEjecucion=%s
        WHERE fecha=%s AND proveedor=%s;"""
    update_query = dbCursor.mogrify(SQL, [n, m, elapsed_time_secs, datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'), provider]).decode('utf8')
    executeSimpleSql(update_query)
    dbCursor.close()
    dbConn.close()

if __name__ == '__main__':
    loadValues(sys.argv[1:])
    main()

#-- http://www.postgresqltutorial.com/postgresql-python/connect/
#-- table = bs.find(lambda tag: tag.name=='table' and tag.has_key('id') and tag['id']=='Table1')
