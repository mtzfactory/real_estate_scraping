import {Routes, RouterModule} from '@angular/router';
import {ModuleWithProviders} from '@angular/core';

import { AuthGuard } from './guard/auth.guard';

import { HomeComponent, HomeLandingComponent } from './public/landing/home.component'
import { PageNotFoundComponent } from './public/pagenotfound/pagenotfound.component'
import { LoginComponent, LogoutComponent } from './public/auth/login/login.component';
import { RegisterComponent } from './public/auth/register/registration.component';
import { RegistrationConfirmationComponent } from './public/auth/confirm/confirmRegistration.component';
import { ForgotPasswordStep1Component, ForgotPasswordStep2Component } from './public/auth/forgot/forgotPassword.component';
import { ResendCodeComponent } from './public/auth/resend/resendCode.component';
import { SecureHomeComponent, SecureLandingComponent } from './secure/landing/secure-home.component';


const homeRoutes: Routes = [
  {
    path: 'home',
    component: HomeComponent,
    children: [
      {
        path: '',
        children: [
          { path: '404', component: PageNotFoundComponent},
//          {path: 'about', component: AboutComponent},
          { path: 'login', component: LoginComponent },
          { path: 'register', component: RegisterComponent },
          { path: 'confirmreg/:username', component: RegistrationConfirmationComponent},
          { path: 'resendcode', component: ResendCodeComponent},
          { path: 'forgot/:email', component: ForgotPasswordStep2Component },
          { path: 'forgot', component: ForgotPasswordStep1Component },
          { path: '', component: HomeLandingComponent }
        ]
      }
    ]
  }
];

const secureHomeRoutes: Routes = [
  {
    path: 'secure',
    component: SecureHomeComponent,
    // canActivate: [AuthGuard],
    children: [
      {
        path: '',
        canActivateChild: [AuthGuard],
        canLoad: [AuthGuard],
        children: [
          { path: 'logout', component: LogoutComponent },
//          { path: 'jwttokens', component: JwtComponent },
//          { path: 'profile', component: MyProfileComponent },
//          { path: 'useractivity', component: UseractivityComponent },
          { path: '', component: SecureLandingComponent }
        ]
      }
    ]
  }
];

const routes: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: '',
    children: [
      ...homeRoutes,
      ...secureHomeRoutes,
      {
        path: '',
        component: HomeComponent
      },
      { path: '**', redirectTo: 'home/404' } // otherwise redirect to home
    ]
  },
];

export const AppRouting: ModuleWithProviders = RouterModule.forRoot(routes);
