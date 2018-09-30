import { Component, OnInit, Input, ElementRef, AfterViewInit, OnDestroy, ViewChild } from '@angular/core';

import { CounterInterface } from '../../interfaces/report.interface';

declare var c3;
declare var d3;

@Component({
  selector: 'app-c3-chart',
  templateUrl: './c3-chart.component.html',
  styleUrls: ['./c3-chart.component.css']
  // template: `<div #chart id="chart-{{id}}"></div>`
})
export class C3ChartComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('chart') public chartEl: ElementRef;
  @Input() id: string;
  @Input() columns: CounterInterface;
  @Input() yAxis: Array<string>;

  private _chart: any;

  constructor() { }

  ngOnInit() {}

  ngAfterViewInit() {
    const opts = {
      data: {
        json: this.columns.data,
        keys: {
          x: 'fecha',
          xFormat:  '%Y-%m-%d',
          value: this.yAxis,
        },
        type: 'spline'
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: {
            format: '%d/%m',
          }
        },
        y: {
          label: {
            text: this.columns.counter.toUpperCase(),
            position: 'outer-middle'
          }
        }
      },
      grid: {
        x: {
          show: true
        },
        y: {
          show: true
        }
      },
      legend: {
        position: 'bottom'
      },
      subchart: {
        show: true
      },
      line: {
        connectNull: true
      }
    }
    if (this.chartEl && this.chartEl.nativeElement) {
        opts['bindto'] = d3.select(this.chartEl.nativeElement)
        this._chart = c3.generate(opts);
    }

  }

  public ngOnDestroy() {
    this._chart.destroy();
  }

  // * http://blog.trifork.com/2014/07/29/creating-charts-with-c3-js/

  // https://jsfiddle.net/maxklenk/k9Dbf/
  // http://jsfiddle.net/7kYJu/1940/
  // http://c3js.org/samples/axes_x_tick_format.html
  // http://c3js.org/samples/data_url.html

}
