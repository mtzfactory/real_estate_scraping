import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UserRegistrationService, CognitoCallback } from '../../../services/cognito.service';

export class RegistrationUser {
    name: string;
    email: string;
    password: string;
}
/**
 * This component is responsible for displaying and controlling
 * the registration of the user.
 */
@Component({
  templateUrl: './registration.html',
  styleUrls: ['../auth.component.css']
})
export class RegisterComponent implements CognitoCallback {
  registrationUser: RegistrationUser;
  router: Router;
  errorMessage: string;

  constructor(public userRegistration: UserRegistrationService, router: Router) {
    this.router = router;
    this.onInit();
  }

  onInit() {
    this.registrationUser = new RegistrationUser();
    this.errorMessage = null;
  }

  onRegister() {
    this.errorMessage = null;
    this.userRegistration.register(this.registrationUser, this);
  }

  cognitoCallback(message: string, result: any) {
    if (message != null) { // error
      this.errorMessage = message;
      console.log('result: ' + this.errorMessage);
    } else { // success, move to the next step
      console.log('redirecting');
      this.router.navigate(['/home/confirmreg', result.user.username]);
    }
  }

}
