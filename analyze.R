install.packages("ggplot2")
install.packages("ggthemes")

library(ggplot2)
library(ggthemes)

df <- read.csv("stats-2017.csv")
summary(df)

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

# By position
p <- ggplot(df, aes(x=position_only, y=points, color=position_only)) +
  stat_summary(fun.y="mean", geom="point") +
  xlab("Position") + ylab("Avg Points") + ggtitle("Avg Points by Position") +
  theme_few() + theme(legend.title = element_blank())
ggsave("image/position-avg-points.png", plot=p, width=11, height=6.8)

p <- ggplot(df, aes(x=points, color=position_only)) +
  geom_density(aes(group=position_only)) +
  xlab("Points") + ylab("Density") + ggtitle("Points Density by Position") +
  theme_few() + theme(legend.title = element_blank())
ggsave("image/position-points-density.png", plot=p, width=11, height=6.8)

p <- ggplot(df, aes(factor(position_only), points)) +
  geom_boxplot() +
  xlab("Position") + ylab("Points") + ggtitle("Points by Position") +
  theme_few() + theme(legend.title = element_blank())
ggsave("image/position-points-boxplot.png", plot=p, width=11, height=6.8)

# By team
p <- ggplot(df, aes(x=team, y=points, color=team)) +
  stat_summary(fun.y="mean", geom="point") +
  xlab("Team") + ylab("Avg Points") + ggtitle("Avg Points by Team") +
  theme_few() + theme(legend.title = element_blank())
ggsave("image/team-avg-points.png", plot=p, width=13, height=6.8)

p <- ggplot(df, aes(x=points, color=team)) +
  geom_density(aes(group=team)) +
  xlab("Points") + ylab("Density") + ggtitle("Points Density by Team") +
  theme_few() + theme(legend.title = element_blank())
ggsave("image/team-points-density.png", plot=p, width=11, height=6.8)

p <- ggplot(df, aes(factor(team), points)) +
  geom_boxplot() +
  xlab("Team") + ylab("Points") + ggtitle("Points by Team") +
  theme_few() + theme(legend.title = element_blank())
ggsave("image/team-points-boxplot.png", plot=p, width=11, height=6.8)
