# Tämä ohjelma esittää, miten R-aliohjelmia käytetään
# tehty 28.02.2022 Annika Kangas

source("./tests/resources/cross_cutting/ApteerausNasberg.R")
source("./tests/resources/cross_cutting/Runkokayraennusteet.R")
source("./tests/resources/cross_cutting/Tilavuus.R")
source("./tests/resources/cross_cutting/Runkokayran korjausmalli.R")
source("./tests/resources/cross_cutting/Korjauskertoimet.R")


taper_curve_list <- list("birch" = readRDS(file.path("./tests/resources/cross_cutting/taper_curves/birch.rds")),
                         "pine" = readRDS(file.path("./tests/resources/cross_cutting/taper_curves/pine.rds")),
                         "spruce" = readRDS(file.path("./tests/resources/cross_cutting/taper_curves/spruce.rds")))

timber_grades_table <- read.table("./tests/resources/cross_cutting/Puutavaralajimaarittelyt.txt")


# species_string can be one of "pine", "spruce" or "birch".
# dbh is breast height diameter
# height is the tree height 
# hkanto is "kannonkorkeus" i.e. stump height i.e. height at which the cross cutting starts (default 10cm)
# Div is the segment height in cm (default 10cm)
cross_cut <- function(species_string, dbh, height, hkanto=0.1, div=10) {

    taper_curve <- taper_curve_list[[species_string]]

    # josta ne voi lukea tavalliseksi vektoriksi
    # Laasasenahon malli "climbed", VAPU-aineistosta malli "felled"
    # TLS aineistosta malli "scanned"

    P <- timber_grades_table

    ##################################

    # m -- number of timber assortment price classes, integer
    m <- length(P[, 1])

    # read taper curve coefficients using the "climbed" model
    coefs <- taper_curve[["climbed"]]$coefficients

    # esimerkkipuu
    # hkanto <- 0.1 # kannonkorkeus
    # dbh <- 30
    # # testiä varten oletetaan myös d6 tunnetuksi
    # # d6<-20
    # # d20p oletetaan olevan tuntematon,
    # # ja lasketaan iteratiivisesti kuten C Snellman ohjelmassa
    # height <- 25

    # vaihe 1. lasketaan runkokäyrän korjausmalli Joukon vanhalla mallilla
    # ts. tätä ei ole vielä laskettu uudestaan uudesta aineistosta
    # tilanteisiin, joissa d6 tunnettu, tarvitaan oma korjausmalli
    # ensin korjausyhtälön pisteet
    p <- tapercurvecorrection1(dbh, height, species_string)
    # sitten itse kertoimet
    b <- cpoly3(p)
    # ja lopuksi uudet kertoimet
    coefnew <- coefs
    for (i in 1:3) {
        # korjausmallilla vaikutetaan kolmeen ensimmäiseen kertoimeen
        coefnew[i] <- coefnew[i] + b[i]
    }

    # vaihe 2,  lasketaan ennuste 20% läpimitalle ennustetun runkokäyrän pohjalta
    # c on suhde dx/d20 tai dx/d80 latvasta katsoen
    # jolloin d20=dx/c
    # käytännössä d20=d13/c, jossa c on suhde d13/d20
    hx <- 1.3
    c <- crkt(hx, height, coefnew)
    d20 <- dbh / c
    # kun kerrotaan alkuperäinen runkokäyrämalli d20:n ennusteella,
    # saadaan runkokäyrämalli, joka ennustaa läpimitan tietyllä korkeudella
    # läpimitan funktiona
    coefnew <- coefnew * d20

    # vaihe 3. lasketaan tilavuus integroimalla runkokäyrää

    vhat <- volume(hkanto, dbh, height, coefnew)

    # vaihe 4. muodostetaan puutason lähtötiedot apteeraukseen
    # n -- number of tree segments, integer
    n <- (height * 100) / div - 1

    # T -- tree stem profile as a 2-dimensional array of size n x 3
    T <- array(data = NA, dim = c(n, 3), dimnames = NULL)
    T[, 1] <- vhat$dpiece * 10 # diameter at the end of piece in mm
    T[, 2] <- vhat$hpiece # height at the end of each piece
    T[, 3] <- vhat$vcum # cumulative volume by pieces

    # Apteerausaliohjelman kutsu
    Apt <- apt(T, P, m, n, div)

    return(Apt)
}
