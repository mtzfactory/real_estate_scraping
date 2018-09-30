import { Component, OnInit, HostBinding } from '@angular/core';

import { CognitoUtil } from '../../services/cognito.service';
import { ReportService } from '../../services/report.service';
import { ReportInterface } from '../../interfaces/report.interface'

@Component({
  templateUrl: './secure-home.component.html',
  styleUrls: ['./secure-home.component.css']
})
export class SecureHomeComponent {

  constructor() {
    console.log('HomeComponent constructor');
  }

}

@Component({
  templateUrl: './secure-landing.html',
  styleUrls: ['./secure-home.component.css']
})
export class SecureLandingComponent implements OnInit {
  public report: ReportInterface;
  public total: number;

  constructor(private reportService: ReportService, private cognitoUtil: CognitoUtil) {
    console.log('SecureLandingComponent constructor');
  }

  ngOnInit() {
    document.body.className = 'waiting';
    this.cognitoUtil.getIdTokennn$()
      .subscribe(
        d => { this.getData(d.token); },
        error => { console.error('SecureHomeComponent#ngOnInit: ' + error); },
        () => { document.body.className = ''; } // document.body.style.cursor = 'default'; }
      );
  }

  getData(token: string) {
    this.report = null;
    this.reportService.getReport(token)
      .subscribe(
        data => {
          if (data.summary) {
            Object.keys(data['summary']).forEach(key => {
              if (data['summary'][key].realestate === 'total') { this.total = data['summary'][key].rows; }
            });
            this.report = data;
          } else { console.error('SecureHomeComponent#getData (1): ' + data.errorMessage); }
        },
        error => { console.error('SecureHomeComponent#getData (2): ' + error); },
        () => {
          if (this.report) { console.log('Correctly downloaded report data'); }
        }
      );
  }

}
