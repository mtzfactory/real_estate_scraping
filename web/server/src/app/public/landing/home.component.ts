import { Component } from '@angular/core';

@Component({
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {

  constructor() {
    console.log('HomeComponent constructor');
  }

}

@Component({
  templateUrl: './home-landing.html',
  styleUrls: ['./home.component.css']
})
export class HomeLandingComponent {

  constructor() {
    console.log('HomeLandingComponent constructor');
  }

}
