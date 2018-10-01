
# REAL ESTATE SCRAPING

This web app was the last one I made _before joining the programming bootcamp_, back in 2017. At that time I had already done two more apps in __Angular__, so I decided to make this third one to build up knowledge.

This was a personal project to build a real estate __scraping__ app, which gathered data from different real estate web pages and stored information for further analysis later on.

The backend was run in __Amazon AWS__:

· The worker scripts written in _Python_ were executed in an _Amazon EC2_ instance and scheduled by a cron service to scrape the real estate web pages.

· _AWS Lambda_ was used to host the Api, which was also written in __python__.

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

· Dashboard reporting statistics of last web scraping.
[![m](images/m3.jpg)](images/m3_original.png)
