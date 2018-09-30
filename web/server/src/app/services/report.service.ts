import { Injectable } from '@angular/core';
import { Http, Headers, Response, RequestOptions, Jsonp, URLSearchParams } from '@angular/http';

import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';


@Injectable()
export class ReportService {
  private token: string = null;

  constructor(private _http: Http, private _jsonp: Jsonp) {}

  public getReport(token: string): Observable<any> {
    // const uri = 'https://hylj0t5ud8.execute-api.eu-central-1.amazonaws.com/no2auth/lambda-report';
    const uri = 'https://hylj0t5ud8.execute-api.eu-central-1.amazonaws.com/2auth/lambda-report'

    const headers = new Headers();
    headers.set('Content-Type', 'application/json');
    headers.set('Authorization', token);
    const options = new RequestOptions({ headers: headers });

    const data$ = this._http.get(uri, options)
      .map((res: Response) => res.json()) // .map(this.updaDate)
      .catch((error: any) => Observable.throw(JSON.stringify(error) || 'ReportService#getReport: Server error'));
    return data$;
  }

  private updaDate(res: Response) {
    const r = res.json();
    if (r.data) {
      r.data.forEach((d) => {
        d.fecha = d.fecha.substr(0, 10); // new Date(d.fecha);
      });
    }
    return r;
  }

}
