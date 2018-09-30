#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

import os, sys, getopt
import datetime
from datetime import timedelta
import time
from httplib2 import Http
import urllib
import base64
import json
import psycopg2 as pg
import psycopg2.extras

debug = False
provider = "idealista"
apiKey = None
apliSecret = None
dbConn = None
dbCursor = None
properties = []

def usage():
    print 'uso: idealista-worker.py -d'
    print '    --debug,        -d  : imprime información de debugging.'
    sys.exit()

def loadValues(argv):
    global debug
    #---
    try:
        opts, args = getopt.getopt(argv,"hd",[])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        if opt == '-h':
            usage()
        elif opt in ("-d", "--debug"):
            debug = True

def getApiValues():
    global dbConn
    global dbCursor
    #---
    key = ''
    secret = ''
    resetApiValues()
    SQL = "SELECT apiKey, apiSecret FROM idealista_api ORDER BY numUsed ASC, lastDay;"
    try:
        dbCursor.execute(SQL)
    except (Exception, psycopg2.DatabaseError) as error:
        print "[ERROR] %s" % error
        pass
    else:
        rows = dbCursor.fetchall()
        key = urllib.quote(rows[0][0])
        secret = urllib.quote(rows[0][1])
    return key, secret

def resetApiValues():
    SQL = "UPDATE idealista_api SET numUsed = 0 FROM (SELECT * FROM idealista_api WHERE EXTRACT(month FROM age(CURRENT_DATE, lastDay)) >= 1) AS t;"
    dbCursor.execute(SQL)

def updateApiValues(key):
    SQL = "UPDATE idealista_api SET numUsed = numUsed::int +1, lastDay = CURRENT_DATE, lastTime = CURRENT_TIME WHERE apikey = '%s';" % key
    dbCursor.execute(SQL)

def getOauthToken(apiKey, apiSecret):
    url = "https://api.idealista.com/oauth/token"
    #---
    http_obj = Http()
    auth = base64.b64encode(apiKey + ':' + apiSecret)
    body = {'grant_type':'client_credentials'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Authorization' : 'Basic ' + auth}
    resp, content = http_obj.request(url, method='POST', headers=headers, body=urllib.urlencode(body))
    return resp, json.loads(content)

def getJsonData(token, page = None):
    global apiKey
    global properties
    #---
    lon = 41.390205
    lat = 2.154007
    distance = "&distance=" + str(8000)
    center = "&center=" + str(lon) + "," + str(lat)
    page = 1 if page is None else page
    numPage = "&numPage=" + str(page)
    maxItems = "&maxItems=" + str(50)
    options = "&propertyType=homes&operation=sale&order=publicationDate&sort=desc&t=1"
    url = "http://api.idealista.com/3.5/es/search?country=es" + numPage + maxItems + center + distance + options
    #---
    http_obj = Http()
    headers = {'Authorization' : 'Bearer ' + token}
    resp, content = http_obj.request(url, method='POST', headers=headers)
    try:
        jcontent = json.loads(content)
    except Exception, err:
        result = {"error": numPage, "error_description": err}
    else:
        updateApiValues(apiKey)
        result = jcontent['elementList']
        properties += result
        if debug: print "  + Descargada página %s de %s, con %d inmuebles." % (jcontent['actualPage'], jcontent['totalPages'], len(result))
        if (jcontent['actualPage'] < 3): #jcontent['totalPages']):
            time.sleep(1)
            getJsonData(token, page + 1)
    return resp, result

def connectToDatabase():
    global dbConn
    global dbCursor
    #---
    HOST = "apttoyou-postgresql.czqsvjcidxtf.eu-central-1.rds.amazonaws.com"
    DBNAME = "apttoyou_db"
    USER = "apttoyou"
    PASSWORD = "F7e-QhV-Mfm-ybD"
    PG_CONN_STRING = "host='%s' dbname='%s' user='%s' password='%s'  port='5432'" % (HOST, DBNAME, USER, PASSWORD)
    #---
    if debug: print ">> Conectando a la base de datos: %s" % (HOST)
    try:
        dbConn = pg.connect(PG_CONN_STRING)
    except psycopg2.DatabaseError, ex:
        print "[ERROR] Problema de conexión a la base de datos: %s" % ex
        sys.exit(1)
    else:
        if debug: print ">> Conectado a la base de datos!"
        dbCursor = dbConn.cursor()

def insertNewProperty(data):
    global dbConn
    global dbCursor
    global provider
    #---
    i = 0
    TABLE = "t9m1732_%s" % provider
    for el in data:
        SQL = """
            INSERT INTO %s (
                realestate,
                propertycode,
                externalreference,
                neighborhood,
                district,
                municipality,
                province,
                country,
                latitude,
                longitude,
                distance,
                thumbnail,
                url,
                address,
                propertyType,
                status,
                bathrooms,
                hasLift,
                newDevelopment,
                rooms,
                exterior,
                size,
                floor,
                price,
                priceByArea)
            VALUES ($$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$, $$%s$$);""" % (
                TABLE,
                provider,
                el['propertyCode'],
                el.get('externalReference', ''),
                el.get('neighborhood', ''),
                el.get('district', ''),
                el.get('municipality', ''),
                el.get('province', ''),
                el.get('country', ''),
                el.get('latitude', ''),
                el.get('longitude', ''),
                el.get('distance', ''),
                el.get('thumbnail', ''),
                el.get('url', ''),
                el.get('address', ''),
                el.get('propertyType', ''),
                el.get('status', ''),
                el.get('bathrooms', ''),
                el.get('hasLift', ''),
                el.get('newDevelopment', ''),
                el.get('rooms', ''),
                el.get('exterior', ''),
                el.get('size', ''),
                el.get('floor', ''),
                el.get('price', ''),
                el.get('priceByArea', '')
            )
        try:
            dbCursor.execute(SQL)
        except Exception, err:
            print "[ERROR] propertyCode %s: %s" % (el['propertyCode'], err.pgerror)
            dbConn.rollback()
            pass
        else:
            i += 1
    dbConn.commit()
    return i


#-- http://www.the-art-of-web.com/sql/upsert/
def updateMainDatabase():
    SQL = "INSERT INTO public.t9m1732 SELECT * FROM t9m1732_%s ON CONFLICT DO NOTHING;" % provider
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
    SQL = "TRUNCATE public.t9m1732_%s" % provider
    return executeSimpleSql(SQL)

def executeSimpleSql(SQL):
    rowCount = 0
    try:
        dbCursor.execute(SQL)
    except (Exception, psycopg2.DatabaseError) as error:
        print "[ERROR] %s" % error
        dbConn.rollback()
        pass
    else:
        rowCount = dbCursor.rowcount
    dbConn.commit()
    return rowCount

def main():
    global properties
    global apiKey, apiSecret
    #---
    if debug:
        print '>> Procensando %s.' % provider.title()
        print ">> Obteniendo token."
    start_time = time.time()
    connectToDatabase()
    truncateTempTable()
    apiKey, apiSecret = getApiValues()
    r, t = getOauthToken(apiKey, apiSecret)
    if (r.status == 200):
        s, c = getJsonData(t['access_token'])
        if (len(properties) > 0):
            i = insertNewProperties(properties)
            if debug: print "  + %d registros insertados en la tabla de %s." % (i, provider)
        if (s.status != 200):
            print "[ERROR] Al realizar la consulta (%d): %s, %s." % (s.status, c['error'], c['error_description'])
            sys.exit(1)
    else:
        print "[ERROR] Al obtener el token (%d): %s, %s." % (r.status, t['error'], t['error_description'])
        sys.exit(1)

    if debug:
        n = updateMainDatabase()
        print ">> %s registros insertados en la tabla principal." % n
        m = updateSoldProperties()
        print ">> %s propiedades vendidas." % m
        elapsed_time_secs = time.time() - start_time
        print ">> Tiempo de ejecución: %s secs" % timedelta(seconds=round(elapsed_time_secs))
        print ">> Finalizado."

    dbCursor.close()
    dbConn.close()

if __name__ == "__main__":
    loadValues(sys.argv[1:])
    main()

#-- http://www.postgresqltutorial.com/postgresql-python/connect/
