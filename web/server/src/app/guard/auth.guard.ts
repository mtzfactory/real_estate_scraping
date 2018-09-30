import { Injectable, OnDestroy } from '@angular/core';
import { CanLoad, CanActivateChild, CanActivate, Router, Route, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import { Subscription } from 'rxjs/Subscription';

import { UserLoginService } from '../services/cognito.service';

@Injectable()
export class AuthGuard implements CanActivate, CanActivateChild, CanLoad, OnDestroy {
  private authState = false;
  private subscription: Subscription;

  constructor(private userService: UserLoginService, private router: Router) {
    console.log('AuthGuard constructor.')
    this.subscription = this.userService.isAuthenticated$().subscribe(
      (s) => { this.authState = s.isValid; console.log('AuthGuard#userService subscription: session is ' + s.isValid); },
      error => { this.authState = false; console.log('AuthGuard#userService subscription: error: ' + error); }
    );
  }

  ngOnDestroy() {
    console.log('AuthGuard ngOnDestroy.')
    this.subscription.unsubscribe()
  }

  canActivate(
      next: ActivatedRouteSnapshot,
      state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    console.log('AuthGuard#canActivate called');
    const url: string = state.url;
    return this.checkLogin(url);
  }

  canActivateChild(
      next: ActivatedRouteSnapshot,
      state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    console.log('AuthGuard#canActivateChild called');
    return this.canActivate(next, state);
  }

  canLoad(route: Route): boolean {
    const url = `/${route.path}`;
    return this.checkLogin(url);
  }

  checkLogin(url: string): boolean {

    console.log('AuthGuard#checkLogin: ' + this.authState);
    if (this.authState) { return true; }

    // Store the attempted URL for redirecting
    this.userService.redirectUrl = url;
    console.log(url + ' needs authentication.');

    // Navigate to the login page with extras
    this.router.navigate(['/home/login']);
    return false;
  }

}
