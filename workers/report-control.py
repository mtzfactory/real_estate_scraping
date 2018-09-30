#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

import os, datetime
from datetime import timedelta
import time

import pandas as pd
from tabulate import tabulate

import sqlalchemy
from sqlalchemy.inspection import inspect
from sqlalchemy import Table, Column, Integer, BigInteger, REAL, String, Time, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from collections import defaultdict

HOST = 'apttoyou-postgresql.czqsvjcidxtf.eu-central-1.rds.amazonaws.com'
DBNAME = 'apttoyou_db'
USER = 'apttoyou'
PASSWORD = 'F7e-QhV-Mfm-ybD'

Base = declarative_base()


class Control(Base):
    __tablename__ = 'control'
    fecha = Column(Date, primary_key=True)
    hora = Column(Time, primary_key=True)
    proveedor = Column(String)
    totalpaginas = Column(Integer)
    totalinmuebles = Column(Integer)
    totalinsertados = Column(Integer)
    totalbaja = Column(Integer)
    tiempoejecucion = Column(REAL)

    def __repr__(self):
        return "{fecha:'%s', proveedor:'%s', totalPaginas:'%d', totalInmuebles:'%d', totalInsertados:'%d', totalBaja:'%d', tiempoEjecucion:'%s'}" % \
            (self.fecha, self.proveedor, self.totalpaginas, self.totalinmuebles, self.totalinsertados, self.totalbaja, self.tiempoejecucion)


class t9m1732(Base):
    __tablename__ = 't9m1732'
    realestate = Column(String(30), primary_key = True)
    propertyCode = Column(BigInteger)
    sold = Column(Date)

    def __repr__(self):
        return "{realestate:'%s'}" % \
            (self.realestate)


def connect(user, password, db, host='localhost', port=5432):
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    con = sqlalchemy.create_engine(url, client_encoding = 'utf8')
    meta = sqlalchemy.MetaData(bind = con, reflect = True)
    return con, meta


def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)
    return result


def main():
    os.environ['TZ'] = 'Europe/Madrid'
    time.tzset()
    start_time = time.time()
    con, meta = connect(USER, PASSWORD, DBNAME, HOST)
    # for table in meta.tables:
    #     print table
    # control = meta.tables['control']
    # rset = con.execute(control.select())

    Session = sessionmaker(bind = con)
    session = Session()
    rset = session.query(Control).order_by(Control.proveedor.asc(), Control.fecha.desc()).all()
    print ''
    print tabulate(pd.DataFrame(query_to_dict(rset)), headers='keys', tablefmt='psql')
    rset = session.query(t9m1732.realestate, func.count(t9m1732.realestate)).group_by(t9m1732.realestate).all()
    print ''
    print rset
    elapsed_time_secs = time.time() - start_time
    print ''
    print '>> Tiempo de ejecución: %s secs.\n' % timedelta(seconds=round(elapsed_time_secs))


if __name__ == '__main__':
    main()
