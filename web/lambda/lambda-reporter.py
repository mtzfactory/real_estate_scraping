#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

# virtualenv venv
# source venv/bin/activate
# pip install sqlalchemy
# pip install marshmallow-sqlalchemy
# pip install psycopg2
# https://github.com/jkehler/awslambda-psycopg2
# deactivate
# cd ~/venv/lib/python2.7/site-packages/
# zip -r9 ~/lambda-reporter.zip *
# cd ~/venv/lib64/python2.7/site-packages/
# zip -r9 ~/lambda-reporter.zip *
# cd ~
# chmod u=rwx,go=r lambda-reporter.py
# zip -g lambda-reporter.zip lambda-reporter.py

import os
import json

import sqlalchemy
from sqlalchemy import Column, Integer, REAL, String, Time, Date, func, literal
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.sql import label

HOST = 'xxxxxxxxxx-postgresql.xxxxxxxxxx.eu-central-1.rds.amazonaws.com'
DBNAME = 'xxxxxxxxxx'
USER = 'xxxxxxxxxx'
PASSWORD = 'xxxxxxxxxx'

session = None
Base = declarative_base()


class Control(Base):
    __tablename__ = 'control'
    fecha = Column(Date, primary_key=True)
    hora = Column(Time, primary_key=True)
    proveedor = Column(String, primary_key=True)
    totalpaginas = Column(Integer)
    totalinmuebles = Column(Integer)
    totalinsertados = Column(Integer)
    totalbaja = Column(Integer)
    tiempoejecucion = Column(REAL)


class ControlSchema(ModelSchema):
    global session

    class Meta:
        model = Control
        sqla_session = session  # optionally attach a Session to use for deserialization


class t9m1732(Base):
    __tablename__ = 't9m1732'
    realestate = Column(String, primary_key=True)
    rows = Column(Integer)


class t9m1732Schema(ModelSchema):
    global session

    class Meta:
        model = t9m1732
        sqla_session = session  # optionally attach a Session to use for deserialization


def array_column(matrix, i):
    return [row[i] for row in matrix]


def array_filter(A, field, filter):
    # [a for a in A if a not in subset_of_A]
    return [u for u in A if u[field] == filter]


def connect(user, password, db, host='localhost', port=5432):
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    con = sqlalchemy.create_engine(url, client_encoding='utf8')
    meta = sqlalchemy.MetaData(bind=con, reflect=True)
    return con, meta


def main():
    global session

    con, meta = connect(USER, PASSWORD, DBNAME, HOST)

    Session = sessionmaker(bind=con)
    session = Session()

    realestate = []
    for r in session.query(Control.proveedor).distinct():
        realestate.append(r.proveedor)

    fechas = []
    for r in session.query(func.to_char(Control.fecha, 'yyyy-mm-dd').label('fecha')).order_by(Control.fecha).distinct():
        fechas.append(r.fecha)

    # rset1 = session.query(Control).order_by(Control.proveedor.asc(), Control.fecha.desc()).all()
    rset1 = session.query(Control).order_by(Control.proveedor.asc(), Control.fecha).all()
    control_schema = ControlSchema(many=True)
    result1 = control_schema.dump(rset1)

    s1 = sqlalchemy.sql.select([t9m1732.realestate, label('rows', func.count(t9m1732.realestate))]).group_by(t9m1732.realestate)
    s2 = sqlalchemy.sql.select([literal('total').label('realestate'), label('rows', func.count(t9m1732.realestate))])
    q = s1.union(s2).alias('summary')

    rset2 = session.query(q).all()
    t9m1732_schema = t9m1732Schema(many=True)
    result2 = t9m1732_schema.dump(rset2)

    columns = [col.key for col in Control.__table__.columns]
    pk = [col.name for col in Control.__table__.primary_key.columns.values()]
    cols = [col for col in columns if col not in set(pk)]

    ## charts.js
    # counters = []
    # for c in cols:
    #     datasets = []
    #     for r in realestate:
    #         r_data = array_filter(result1.data, 'proveedor', r)
    #         r_data_x = array_column(r_data, c)
    #         json1 = {'label': r, 'data': r_data_x, 'fill': False, 'hidden': False}
    #         datasets.append(json1)
    #     json2 = {'counter': c, 'sets': datasets}
    #     counters.append(json2)

    ## C3js
    counters = []
    for c in cols:
        datasets = []
        for f in fechas:
            f_data = array_filter(result1.data, 'fecha', f)
            #print f_data
            r_data = {}
            r_data['fecha'] = f
            for fd in f_data:
                r_data[fd['proveedor']] = 'null' if fd[c] is None else fd[c]
            datasets.append(r_data)
        counters.append({'counter': c, 'data': datasets})

    # xhr = {'data': result1.data, 'realestate': realestate, 'period': fechas, 'summary': result2.data}
    xhr = {'counters': counters, 'realestate': realestate, 'period': fechas, 'summary': result2.data}
    return xhr


def lambda_handler(event, context):
    return main()


if __name__ == '__main__':
    print main()
