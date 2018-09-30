export interface CounterInterface {
  counter: string,
  data: Array<SetsInterface>
}

export interface SetsInterface {
  fecha: Array<string>,
}

// export interface SetsInterface {
//   hidden: boolean,
//   fill: boolean,
//   data: Array<number>,
//   label: string
// }

export interface SummaryInterface {
  count: number,
  realestate: string
}

// export interface ReportInterface {
//   summary: Array<SummaryInterface>,
//   period: Array<string>,
//   realestate: Array<string>,
//   counters: Array<CounterInterface>,
// }

export interface ReportInterface {
  summary: Array<SummaryInterface>,
  period: Array<string>,
  realestate: Array<string>,
  counters: Array<CounterInterface>,
}
