#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

import boto3
import botocore
import hmac
import hashlib
import base64

POOL_ID = 'eu-central-1_J1HZ86uLX'
APP_NAME = 'cognito-app-clients'
APP_ID = '23o6vbtasvatud7f567go7svfk'
APP_SECRET = 'crepq4t9h0doqe2lirk6skp53ahju7inptvuqlnd3g1290e12ag'
USERNAME = 'cognito-user1'
PASSWORD = '@User1pool'
ACCESS_KEY = 'AKIAI5WPBLQZELFPLGGQ'
SECRET_KEY = '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'

class Cognito:
    client_id = APP_ID #app.config.get('AWS_CLIENT_ID')
    user_pool_id = POOL_ID #app.config.get('AWS_USER_POOL_ID')
    #identity_pool_id = app.config.get('AWS_IDENTITY_POOL_ID')
    client_secret = APP_SECRET #app.config.get('AWS_APP_CLIENT_SECRET')
    # Public Keys used to verify tokens returned by Cognito:
    # http://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html#amazon-cognito-identity-user-pools-using-id-and-access-tokens-in-web-api
    #id_token_public_key = app.config.get('JWT_ID_TOKEN_PUB_KEY')
    #access_token_public_key = app.config.get('JWT_ACCESS_TOKEN_PUB_KEY')

    def __get_client(self):
        return boto3.client('cognito-idp')

    def get_secret_hash(self, username):
        # A keyed-hash message authentication code (HMAC) calculated using
        # the secret key of a user pool client and username plus the client
        # ID in the message.
        message = username + self.client_id
        dig = hmac.new(self.client_secret, msg=message.encode('UTF-8'),
                       digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    # REQUIRES that `ADMIN_NO_SRP_AUTH` be enabled on Client App for User Pool
    def login_user(self, username_or_alias, password):
        try:
            return self.__get_client().admin_initiate_auth(
                UserPoolId=self.user_pool_id,
                ClientId=self.client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username_or_alias,
                    'PASSWORD': password,
                    'SECRET_HASH': self.get_secret_hash(username_or_alias)
                }
            )
        except botocore.exceptions.ClientError as e:
            return e.response

# http://boto3.readthedocs.io/en/latest/reference/services/cognito-idp.html#CognitoIdentityProvider.Client.initiate_auth
u = Cognito()
r = u.login_user(USERNAME, PASSWORD)
print r
if r.get('Session'):
    print r['Session']
    print r['ChallengeName']
    print r['ChallengeParameters']
if r.get('AuthenticationResult'):
    print r['AuthenticationResult']['AccessToken']
    print r['AuthenticationResult']['ExpiresIn']
