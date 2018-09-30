#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

## COGNITO_JWKS
# https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_J1HZ86uLX/.well-known/jwks.json

from warrant import Cognito

POOL_ID = 'eu-central-1_J1HZ86uLX'
APP_NAME = 'cognito-app-clients'
APP_ID = '6h58tr9l145ek8vqhqo9g3vi4d'
USERNAME = 'cognito-user1'
PASSWORD = '@User1pool'

u = Cognito(POOL_ID, APP_ID, username=USERNAME)
u.authenticate(password=PASSWORD)
print u
