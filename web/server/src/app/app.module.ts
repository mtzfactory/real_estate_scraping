import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule, JsonpModule } from '@angular/http';

import { AppComponent } from './app.component';

import { AppRouting } from './app.routes';

import { KnobComponent } from './components/knob.component';
import { C3ChartComponent } from './components/c3-chart/c3-chart.component';

import { AuthGuard } from './guard/auth.guard'
import { UserLoginService, UserRegistrationService, CognitoUtil } from './services/cognito.service';
import { ReportService } from './services/report.service'

import { PageNotFoundComponent } from './public/pagenotfound/pagenotfound.component'
import { HomeComponent, HomeLandingComponent } from './public/landing/home.component';
import { LoginComponent, LogoutComponent } from './public/auth/login/login.component';
import { RegisterComponent } from './public/auth/register/registration.component';
import { RegistrationConfirmationComponent } from './public/auth/confirm/confirmRegistration.component';
import { ForgotPasswordStep1Component, ForgotPasswordStep2Component } from './public/auth/forgot/forgotPassword.component';
import { ResendCodeComponent } from './public/auth/resend/resendCode.component';
import { SecureHomeComponent, SecureLandingComponent } from './secure/landing/secure-home.component';


@NgModule({
  declarations: [
    AppComponent,
    PageNotFoundComponent,
    HomeComponent,
    HomeLandingComponent,
    LoginComponent,
    LogoutComponent,
    RegisterComponent,
    RegistrationConfirmationComponent,
    ForgotPasswordStep1Component,
    ForgotPasswordStep2Component,
    ResendCodeComponent,
    SecureHomeComponent,
    SecureLandingComponent,
    KnobComponent,
    C3ChartComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    JsonpModule,
    AppRouting
  ],
  providers: [
    AuthGuard,
    CognitoUtil,
    UserLoginService,
    UserRegistrationService,
    ReportService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
