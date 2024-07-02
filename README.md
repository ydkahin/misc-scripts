# misc-scripts
Misc scripts used on my blog

## 1. Option Pricing and Greeks Calculator
R functions for pricing European options and calculating Greeks:

- Black-Scholes pricing for vanilla and digital options
- Implied volatility calculation
- Greeks: delta, gamma, theta, vega

Features:

- Modular functions for easy use
- Supports non-dividend paying underlyings
- Uses pracma and stats libraries

Source the script and call functions with appropriate parameters (volatility, spot price, strike, risk-free rate, time to expiration).

## 2. Letterboxd User Film Data Scraper
See [this](https://ydkahin.github.io/posts/letterboxd-scraper-i/)

## 3. Panel
Panel dashboard generator. This comes with a Letterboxd scraper scraper (documented [here](https://ydkahin.github.io/posts/letterboxd-scraper-i/)). The scraper script generates a CSV that the dashboard generator can use.
Requirements are minimal. Just [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and [Panel](https://panel.holoviz.org/). 

You can find a screenshot [here](https://i.imgur.com/V1vTFdu.png)

 
