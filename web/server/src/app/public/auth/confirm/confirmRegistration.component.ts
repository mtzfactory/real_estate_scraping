import {Component, OnInit, OnDestroy} from '@angular/core';
import {Router, ActivatedRoute} from '@angular/router';
import {UserRegistrationService, UserLoginService, LoggedInCallback} from '../../../services/cognito.service';

@Component({
  templateUrl: './confirmRegistration.html',
  styleUrls: ['../auth.component.css']
})
export class RegistrationConfirmationComponent implements OnInit, OnDestroy {
  code: string;
  email: string;
  errorMessage: string;
  private sub: any;

  constructor(public regService: UserRegistrationService, public router: Router, public route: ActivatedRoute) {}

  ngOnInit() {
    this.sub = this.route.params.subscribe(params => {
      this.email = params['username'];
    });
    this.errorMessage = null;
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  onConfirmRegistration() {
    this.errorMessage = null;
    this.regService.confirmRegistration(this.email, this.code, this);
  }

  cognitoCallback(message: string, result: any) {
    if (message != null) { // error
      this.errorMessage = message;
      console.log('message: ' + this.errorMessage);
    } else { // success
      // move to the next step
      console.log('Moving to securehome');
      // this.configs.curUser = result.user;
      this.router.navigate(['/secure']);
    }
  }

}
