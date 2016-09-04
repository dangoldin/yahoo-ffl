install.packages("ggplot2")
install.packages("ggthemes")

library(ggplot2)
library(ggthemes)

df <- read.csv("stats-2017.csv")
summary(df)

substr(df$position, 1, 3)

lastTwoChars <- function(s) {
  s <- as.character(s)
  substr(s, nchar(s)-1, nchar(s))
}

df$position_only = sapply(df$position, lastTwoChars)

ggplot(df, aes(x=position_only, y=points)) + stat_summary(fun.y="mean", geom="point")
