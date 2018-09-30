import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CognitoCallback, UserLoginService } from '../../../services/cognito.service';

@Component({
  templateUrl: './forgotPasswordStep1.html',
  styleUrls: ['../auth.component.css']
})
export class ForgotPasswordStep1Component implements CognitoCallback {
  email: string;
  errorMessage: string;

  constructor(public router: Router, public userService: UserLoginService) {
    this.errorMessage = null;
  }

  onNext() {
    this.errorMessage = null;
    this.userService.forgotPassword(this.email, this);
  }

  cognitoCallback(message: string, result: any) {
    if (message == null && result == null) { // error
      this.router.navigate(['/home/forgot', this.email]);
    } else { // success
      this.errorMessage = message;
    }
  }

}


@Component({
  templateUrl: './forgotPasswordStep2.html',
  styleUrls: ['../auth.component.css']
})
export class ForgotPasswordStep2Component implements CognitoCallback, OnInit, OnDestroy {
  code: string;
  email: string;
  password: string;
  errorMessage: string;
  private sub: any;

  constructor(public router: Router, public route: ActivatedRoute, public userService: UserLoginService) {
    console.log('ForgotPasswordStep2Component: email from the url: ' + this.email);
  }

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.email = params['email'];
    });
    this.errorMessage = null;
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  onNext() {
    this.errorMessage = null;
    this.userService.confirmNewPassword(this.email, this.code, this.password, this);
  }

  cognitoCallback(message: string) {
    if (message != null) { // error
      this.errorMessage = message;
      console.log('result: ' + this.errorMessage);
    } else { // success
      this.router.navigate(['/home/login']);
    }
  }

}
