
# REAL ESTATE SCRAPING

This web app was the last one I made _before joining the bootcamp_, back in 2017. At that time I had already done two more apps in __Angular__, so I decided to make this one to build knowledge.

This was a personal project to build a real state __scraping__ app, gathering data from different real estate web pages, storing the information for a further analysis.

The backend was run in __Amazon AWS__:

· _Amazon EC2_ instance, where the worker scripts, made in __python__, were executed, scheduled by a cron service, to scrape the real estate web pages.

· _AWS Lambda_ was used to host the Api, developed in __python__ as well.

· _PostgreSql_ database was used to store all the data scraped from the web pages.

If you plan to run your own server, you can find a bunch of information about AWS at `__ documentation` folder, hope you find it useful, it helped me a lot.

## Development server

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 1.1.0.

Clone the repo and do:

```bash
$ git clone https://github.com/mtzfactory/real_estate_scraping.git
$ cd real_estate_scraping
$ npm install
```

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `-prod` flag for a production build.

## Screens

· Main view: dashboard reporting stadistics of last web  scraping.
[![m](images/m3.jpg)](images/m3_original.png)
