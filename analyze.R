install.packages("ggplot2")
install.packages("ggthemes")

library(ggplot2)
library(ggthemes)

df <- read.csv("stats-2017.csv")
summary(df)

substr(df$position, 1, 3)

getPosition <- function(s) {
  s <- as.character(s)
  substr(s, nchar(s)-1, nchar(s))
}

getTeam <- function(s) {
  s <- as.character(s)
  dash_loc = regexpr(" -", s, fixed=T)[1]
  substr(s, 1, dash_loc - 1)
}

df$position_only = sapply(df$position, getPosition)
df$team = sapply(df$position, getTeam)

ggplot(df, aes(x=position_only, y=points)) +
  stat_summary(fun.y="mean", geom="point") +
  theme_few()

ggplot(df, aes(x=points)) +
  geom_density(aes(group=position_only)) +
  theme_few()

ggplot(df, aes(x=team, y=points)) +
  stat_summary(fun.y="mean", geom="point") +
  theme_few()

ggplot(df, aes(x=points)) +
  geom_density(aes(group=team)) +
  theme_few()
