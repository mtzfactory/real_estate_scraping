import { Component, OnInit, HostBinding } from '@angular/core';
import {Router} from '@angular/router';

import { UserLoginService, CognitoCallback} from '../../../services/cognito.service';

@Component({
  templateUrl: './login.component.html',
  styleUrls: ['../auth.component.css']
})
export class LoginComponent implements OnInit, CognitoCallback {
  email: string;
  password: string;
  errorMessage: string;

  constructor(public router: Router, public userService: UserLoginService) {
    console.log('LoginComponent constructor');
  }

  ngOnInit() {
    this.errorMessage = null;
    console.log('Checking if the user is already authenticated. If so, then redirect to the secure site');
    if (this.userService.authState) { this.router.navigate(['/secure']); }
  }

  onLogin() {
    this.errorMessage = null;
    if (this.email == null || this.password == null) {
      this.errorMessage = 'Todos los campos son requeridos.';
      return;
    }
    document.body.style.cursor = 'wait';
    this.userService.authenticate(this.email, this.password, this);
  }

  cognitoCallback(message: string, result: any) {
    if (message != null) { // error
      this.errorMessage = message;
      console.log('result: ' + this.errorMessage);
      if (this.errorMessage === 'User is not confirmed.') {
        console.log('Redirecting');
        this.router.navigate(['/home/confirmreg', this.email]);
        }
    } else { // success
      console.log('LoginComponent@onLogin success, callback redirecting to /secure.');
      this.router.navigate(['/secure']);
    }
    document.body.style.cursor = 'default';
  }

} // LoginComponent


@Component({
    template: ''
})
export class LogoutComponent {

  constructor(public router: Router, public userService: UserLoginService) {
    if (this.userService.authState) {
      this.userService.logout();
    }
      this.router.navigate(['/home']);
  }

} // LogoutComponent
