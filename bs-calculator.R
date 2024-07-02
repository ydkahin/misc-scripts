library(pracma)   # For numerical methods like fsolve
library(stats)    # For normal distribution functions

#function to calculate d1
d1 <- function(sigma, S, K, r, Tt) {
  (log(S / K) + (r + (sigma^2) / 2) * Tt) / (sigma * sqrt(Tt))
}

#function to calculate d2
d2 <- function(sigma, S, K, r, Tt) {
  d1(sigma, S, K, r, Tt) - sigma * sqrt(Tt)
}

#function to calculate the option price
call_option_price <- function(sigma, S, K, r, Tt) {
  Nd1 <- pnorm(d1(sigma, S, K, r, Tt))
  Nd2 <- pnorm(d2(sigma, S, K, r, Tt))
  Nd1 * S - Nd2 * K * exp(-r * Tt)
}

#function to calculate put option price
put_option_price <- function(sigma, S, K, r, Tt) {
  Nd1 <- pnorm(-d1(sigma, S, K, r, Tt))
  Nd2 <- pnorm(-d2(sigma, S, K, r, Tt))
  K * exp(-r * Tt) * Nd2 - S * Nd1
}

#function to calculate digital(aka binary) call option price
digital_option_price <- function(sigma, S, K, r, Tt) {
  Nd2 <- pnorm(d2(sigma, S, K, r, Tt))
  Nd2 * exp(-r * Tt)
}

#function to find implied volatility
find_implied_volatility <- function(C, S, K, r, Tt) {
  implied_vol <- function(sigma) {
    call_option_price(sigma, S, K, r, Tt) - C
  }
  uniroot(implied_vol, c(0.0001, 5))$root
}

# #calculate implied volatilities for the range of option prices
# sigma_Sol <- sapply(C_Range, function(C) {
#   find_implied_volatility(C, S, K, r, Tt)
# })
# 
# #print the results
# sigma_Sol

#-------------------_GREEKS_--------------# (non-dividend)
#function to calculate delta
call_delta <- function(sigma, S, K, r, Tt) {
 Nd1 <- pnorm(d1(sigma, S, K, r, Tt))
 Nd1
}

put_delta <- function(sigma, S, K, r, Tt) {
  Nd1 <- pnorm(d1(sigma, S, K, r, Tt))
  Nd1 - 1
}

#theta
call_theta <- function(sigma, S, K, r, Tt) {
  nd1 <- dnorm(d1(sigma, S, K, r, Tt))
  Nd2 <- pnorm(d2(sigma, S, K, r, Tt))
  -r * K * exp(-r * Tt) * Nd2 - (S * nd1 * sigma)/(2*sqrt(Tt))
}

put_theta <- function(sigma, S, K, r, Tt) {
  nd1 <- dnorm(d1(sigma, S, K, r, Tt))
  Nd2 <- pnorm(-d2(sigma, S, K, r, Tt)) #negative d2
  r * K * exp(-r * Tt) * Nd2 - (S * nd1 * sigma)/(2*sqrt(Tt))
}

#gamma - the same for call/put
option_gamma <- function(sigma, S, K, r, Tt) {
  nd1 <- dnorm(d1(sigma, S, K, r, Tt))
  nd1 / (S * sigma * sqrt(Tt))
}

#vega - the same for call/put
option_vega <- function(sigma, S, K, r, Tt) {
  nd1 <- dnorm(d1(sigma, S, K, r, Tt))
  S * sqrt(Tt) * nd1
}

#delta of digital https://quant.stackexchange.com/a/23271 - assuming constant sigma
digital_delta <- function(sigma, S, K, r, Tt) {
  nd2 <- dnorm(d2(sigma, S, K, r, Tt))
  exp(-r * Tt) * nd2 / (sigma * S * Tt)
}

#digital_option_price(0.1, 171.01, 180, 0.03, 1)-option_vega(0.1, 171.01, 180, 0.03, 1)*(-18/(180^2)) - (digital_option_price(0.1, 171.01, 185, 0.03, 1)-option_vega(18/185, 171.01, 185, 0.03, 1)*(-18/(185^2))) 
