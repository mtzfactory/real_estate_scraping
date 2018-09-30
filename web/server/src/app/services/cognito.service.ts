import { Injectable, Inject, OnInit } from '@angular/core';
import { RegistrationUser } from '../public/auth/register/registration.component';
import { environment } from '../../environments/environment';

import { Observable } from 'rxjs/Observable' // 'rxjs/Rx'; //
import { Observer } from 'rxjs/Observer';
import { Subject } from 'rxjs/Subject';
import 'rxjs/add/observable/of';
import 'rxjs/add/observable/bindNodeCallback';

declare var AWSCognito: any;
declare var AWS: any;

export interface CognitoCallback {
  cognitoCallback(message: string, result: any): void;
}

export interface LoggedInCallback {
  isLoggedIn(message: string, loggedIn: boolean): void;
}

export interface Callback {
  callback(): void;
  callbackWithParam(result: any): void;
}

@Injectable()
export class CognitoUtil {
  public static _REGION = environment.region;
  public static _IDENTITY_POOL_ID = environment.identityPoolId;
  public static _USER_POOL_ID = environment.userPoolId;
  public static _CLIENT_ID = environment.clientId;

  public static _POOL_DATA = {
    UserPoolId: CognitoUtil._USER_POOL_ID,
    ClientId: CognitoUtil._CLIENT_ID
  };

  public static getAwsCognito(): any {
    return AWSCognito
  }

  constructor() {
    AWSCognito.config.region = environment.region;
    AWS.config.region = environment.region;
  }

  getUserPool() {
    return new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(CognitoUtil._POOL_DATA);
  }

  getCurrentUser() {
    return this.getUserPool().getCurrentUser();
  }

  getCognitoIdentity(): string {
    return AWS.config.credentials.identityId;
  }

  getAccessToken(callback: Callback): void {
    if (callback == null) {
      console.log('CognitoUtil: callback in getAccessToken is null... returning.');
      throw new Error('CognitoUtil: callback in getAccessToken is null... returning.');
    }
    if (this.getCurrentUser() != null) {
      this.getCurrentUser().getSession(function (err, session) {
        if (err) {
          console.log('CognitoUtil: Can\'t set the credentials:' + err);
          callback.callbackWithParam(null);
        } else {
          if (session.isValid()) {
            callback.callbackWithParam(session.getAccessToken().getJwtToken());
          }
        }
      });
    } else { callback.callbackWithParam(null); }
  }

  getIdTokennn$(): Observable<any> {
    return Observable.create((observer: Observer<any>) => {
      if (this.getCurrentUser() == null) {
        console.log('CognitoUtil#getIdTokennn cognito user cannot be null.');
        observer.error(new Error('Cognito user cannot be null.'));
        return;
      } else {
        this.getCurrentUser().getSession(function (err, session) {
          if (err) {
            console.log('CognitoUtil#getIdTokennn can\'t set the credentials:' + err);
            observer.error(err); // callback.callbackWithParam(null);
            return;
          } else {
            if (session.isValid()) {
              // callback.callbackWithParam(session.getIdToken().getJwtToken());
              observer.next({ token: session.getIdToken().getJwtToken() });
              observer.complete();
            } else {
              console.log('CognitoUtil#getIdTokennn got the id token, but the session isn\'t valid');
              observer.error(new Error('Session is invalid'));
              return;
            }
          }
        });
      }
    });
  }

  getIdToken(callback: Callback): void {
    if (callback == null) {
      console.log('CognitoUtil: callback in getIdToken is null... returning');
      throw new Error('CognitoUtil: callback in getIdToken is null... returning');
    }
    if (this.getCurrentUser() != null) {
      this.getCurrentUser().getSession(function (err, session) {
        if (err) {
          console.log('CognitoUtil: Can\'t set the credentials:' + err);
          callback.callbackWithParam(null);
        } else {
          if (session.isValid()) {
            callback.callbackWithParam(session.getIdToken().getJwtToken());
          } else {
            console.log('CognitoUtil: Got the id token, but the session isn\'t valid');
          }
        }
      });
    } else { callback.callbackWithParam(null); }
  }

  getRefreshToken(callback: Callback): void {
    if (callback == null) {
      console.log('CognitoUtil: callback in getRefreshToken is null... returning');
        throw new Error('CognitoUtil: callback in getRefreshToken is null... returning');
    }
    if (this.getCurrentUser() != null) {
      this.getCurrentUser().getSession(function (err, session) {
        if (err) {
          console.log('CognitoUtil: Can\'t set the credentials:' + err);
          callback.callbackWithParam(null);
        } else {
          if (session.isValid()) {
            callback.callbackWithParam(session.getRefreshToken());
          }
        }
      });
    } else { callback.callbackWithParam(null); }
  }

  refresh(): void {
    this.getCurrentUser().getSession(function (err, session) {
      if (err) {
        console.log('CognitoUtil: Can\'t set the credentials:' + err);
      } else {
        if (session.isValid()) {
          console.log('CognitoUtil: refreshed successfully.');
        } else {
          console.log('CognitoUtil: refreshed but session is still not valid.');
        }
      }
    });
  }

} // CognitoUtil


@Injectable()
export class UserRegistrationService {

  constructor(@Inject(CognitoUtil) public cognitoUtil: CognitoUtil) {}

  register(user: RegistrationUser, callback: CognitoCallback): void {
    console.log('UserRegistrationService: user is ' + user);

    const attributeList = []
    const dataEmail = {
      Name: 'email',
      Value: user.email
    };
    const dataNickname = {
      Name: 'nickname',
      Value: user.name
    };

    attributeList.push(new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataEmail));
    attributeList.push(new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataNickname));

    this.cognitoUtil.getUserPool().signUp(user.email, user.password, attributeList, null, function (err, result) {
      if (err) {
        callback.cognitoCallback(err.message, null);
      } else {
        console.log('UserRegistrationService: registered user is ' + result);
        callback.cognitoCallback(null, result);
      }
    });
  }

  confirmRegistration(username: string, confirmationCode: string, callback: CognitoCallback): void {
    const userData = {
      Username: username,
      Pool: this.cognitoUtil.getUserPool()
    };
    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

    cognitoUser.confirmRegistration(confirmationCode, true, function (err, result) {
      if (err) {
        callback.cognitoCallback(err.message, null);
      } else {
        callback.cognitoCallback(null, result);
      }
    });
  }

  resendCode(username: string, callback: CognitoCallback): void {
    const userData = {
      Username: username,
      Pool: this.cognitoUtil.getUserPool()
    };
    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

    cognitoUser.resendConfirmationCode(function (err, result) {
      if (err) {
        callback.cognitoCallback(err.message, null);
      } else {
        callback.cognitoCallback(null, result);
      }
    });
  }

} // UserRegistrationService


@Injectable()
export class UserLoginService {
  // store the URL so we can redirect after logging in
  public redirectUrl: string;
  public authState = false;

  constructor(public cognitoUtil: CognitoUtil) {}

  authenticate(username: string, password: string, callback: CognitoCallback) {
    console.log('UserLoginService: starting the authentication.')
    // Need to provide placeholder keys unless unauthorised user access is enabled for user pool
    AWSCognito.config.update({ accessKeyId: 'anything', secretAccessKey: 'anything' })

    const authenticationData = {
      Username: username,
      Password: password,
    };
    const authenticationDetails = new AWSCognito.CognitoIdentityServiceProvider.AuthenticationDetails(authenticationData);
    const userData = {
      Username: username,
      Pool: this.cognitoUtil.getUserPool()
    };

    console.log('UserLoginService: Params set... Authenticating the user.');
    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
      onSuccess: function (result) {
        const logins = {}
        logins['cognito-idp.' + CognitoUtil._REGION + '.amazonaws.com/' + CognitoUtil._USER_POOL_ID] = result.getIdToken().getJwtToken();

        // Add the User's Id Token to the Cognito credentials login map.
        AWS.config.credentials = new AWS.CognitoIdentityCredentials({
          IdentityPoolId: CognitoUtil._IDENTITY_POOL_ID,
          Logins: logins
        });

        console.log('UserLoginService: set the AWS credentials - ' + JSON.stringify(AWS.config.credentials));
        console.log('UserLoginService: set the AWSCognito credentials - ' + JSON.stringify(AWSCognito.config.credentials));

        AWS.config.credentials.get(function (err) {
          if (!err) {
            // console.log('UserLoginService: credentials identityId: ' + AWS.config.credentials.identityId);
            // console.log('UserLoginService: credentials accessKeyId: ' + AWS.config.credentials.accessKeyId);
            // console.log('UserLoginService: credentials secretAccessKey: ' + AWS.config.credentials.secretAccessKey);
            // console.log('UserLoginService: credentials sessionToken: ' + AWS.config.credentials.sessionToken);
            callback.cognitoCallback(null, result);
          } else {
            callback.cognitoCallback(err.message, null);
          }
        });
      },
      onFailure: function (err) {
        this.token = null;
        callback.cognitoCallback(err.message, null);
      },
      mfaRequired: function(codeDeliveryDetails) {
        console.log('UserLoginService#authenticateUser needs mfaRequired code.');
        // cognitoUser.sendMFACode(verificationCode, this);
      }
    });
  }

  forgotPassword(username: string, callback: CognitoCallback) {
    const userData = {
      Username: username,
      Pool: this.cognitoUtil.getUserPool()
    };
    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

    cognitoUser.forgotPassword({
      onSuccess: function (result) {
      },
      onFailure: function (err) {
        callback.cognitoCallback(err.message, null);
      },
      inputVerificationCode() {
        callback.cognitoCallback(null, null);
      }
    });
  }

  confirmNewPassword(email: string, verificationCode: string, password: string, callback: CognitoCallback) {
    const userData = {
      Username: email,
      Pool: this.cognitoUtil.getUserPool()
    };

    const cognitoUser = new AWSCognito.CognitoIdentityServiceProvider.CognitoUser(userData);

    cognitoUser.confirmPassword(verificationCode, password, {
      onSuccess: function (result) {
        callback.cognitoCallback(null, result);
      },
      onFailure: function (err) {
        callback.cognitoCallback(err.message, null);
      }
    });
  }

  logout() {
    console.log('UserLoginService: Logging out.');
    this.authState = false;
    this.cognitoUtil.getCurrentUser().signOut();
    if (AWS.config.credentials !== null) { AWS.config.credentials.clearCachedId(); }
    AWS.config.credentials = new AWS.CognitoIdentityCredentials({
        IdentityPoolId: CognitoUtil._IDENTITY_POOL_ID,
      });
  }

  isAuthenticated$(): Observable<any> {
    const currentUser = this.cognitoUtil.getCurrentUser();
    this.authState = false;
    return Observable.create((observer: Observer<any>) => {
      if (currentUser === null) {
        console.log('UserLoginService#getSession cognito user cannot be null.');
        observer.error(new Error('Cognito user cannot be null.'));
        return;
      }

      currentUser.getSession((err, session) => {
        if (err) {
          console.log('UserLoginService#getSession error: ' + JSON.stringify(err));
          observer.error(err);
          return;
        }

        this.authState = session.isValid();
        if (!session.isValid()) {
          console.log('UserLoginService#getSession session is invalid.');
          observer.error(new Error('Session is invalid'));
          return;
        }
        console.log('UserLoginService#getSession sending the session down through the observable. isValid: ' + session.isValid());
        observer.next({ isValid: session.isValid() });
        observer.complete();
      });
    });
  }

} // UserLoginService


@Injectable()
export class UserParametersService {

  constructor(public cognitoUtil: CognitoUtil) {}

  getParameters(callback: Callback) {
    const cognitoUser = this.cognitoUtil.getCurrentUser();

    if (cognitoUser != null) {
      cognitoUser.getSession(function (err1, session) {
        if (err1) {
          console.log('UserParametersService: Couldn\'t retrieve the user');
        } else {
          cognitoUser.getUserAttributes(function (err2, result) {
            if (err2) {
              console.log('UserParametersService: in getParameters: ' + err2);
            } else {
              callback.callbackWithParam(result);
            }
          });
        }
      });
    } else {
      callback.callbackWithParam(null);
    }
  }

} // UserParametersService
