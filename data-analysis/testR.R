library(ineq)
data <- read.csv(fulldata_google-news_VF.csv)
ineq(data$Type_media, type="Gini")

