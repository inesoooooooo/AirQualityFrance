# my_module_name
## Introduction:

Nous avons décidé, d’un commun accord, de réaliser un site web sur **la qualité de l’air en France métropolitaine**. Nous analyserons l’évolution de la qualité de l’air en France entre **2020 et 2024**. Le public visé par ce site web sont **les personnes sensibles ou vulnérables** souhaitant identifier les ville dans laquelle elles peuvent s'épanouir sans compromettre leur santé physique. Ce sujet nous tient particulièrement à cœur, car, malheureusement, on peut observer que  le nombre de personnes décédant chaque année des suites de maladies liées à une exposition excessive à la pollution ne cesse d’augmenter. Afin de prévenir certaines maladies ou de certains dommages plus importants, il est essentiel d'analyser ce sujet en profondeur.
Nous aimerions ainsi mieux comprendre :
- comment la qualité de l’air a-t-elle évolué au fil des années,  
- quelles villes ont réussi à améliorer la situation,  
- et quelles sont celles qui rencontrent encore des difficultés à réduire la pollution.

## Problèmatique : Comment a évolué la qualité de l'air en France métropolitaine entre 2020 et 2024 ?

## Développement :

Pour répondre au mieux à ce sujet, nous allons créer un site web intéractif permettant de visualiser l'évolution de la qualité de l'air entre 2020 et 2024. Les utilisateurs pourront choisir l’année à l’aide d’un **curseur allant de 2020 à 2024**, ainsi que le polluant qu’ils souhaitent analyser. Le site affichera alors des **cartes intercatives** représentant le niveau de pollution dans les grandes villes françaises, accompagnées de **graphiques temporels** illustrant la variation des principaux polluants sélectionnés pour chaque ville au fil des années.
Pour s'organiser et réussir à allier la continuité du projet tout au long du semestre nous avons établit le diagramme de Gantt qui suit :


## Diagramme de Gantt – AirQualityFrance

```mermaid
gantt
    title AirQualityFrance - Gantt Diagram 
    dateFormat  YYYY-MM-DD
    axisFormat  %d-%m

    section Organisation
    Formation du groupe & choix du sujet (Myriam + Dalia + Inès)    :myriam, 2025-09-16, 2025-09-18
    Création du repo GitHub & branches (Inès)                       :ines, 2025-10-10, 2025-10-10
    Répartition des tâches (Tous)                                   :tous, 2025-10-11, 2025-10-13

    section Recherche
    Recherche des datasets (Dalia + Inès + Myriam)                  :dalia, 2025-09-20, 2025-10-13
    Nettoyage et préparation des données (Dalia + Myriam)           :myriam, 2025-10-21, 2025-10-22
    Analyse exploratoire (Tous)                                     :tous, 2025-10-20, 2025-10-22

    section Analyse & Visualisation
    Création de visualisations (cartes, graphiques) (??? + Dalia)   :dalia, 2025-11-04, 2025-11-12
    Développement de notebooks interactifs (Inès + Myriam)          :ines, 2025-11-13, 2025-11-20

    section Rédaction
    Rédaction du README.qmd et rapport mid-term (Tous)              :tous, 2025-10-21, 2025-10-25
    Préparation des slides pour la présentation (Myriam + ???)      :myriam, 2025-11-26, 2025-11-30

    section Finalisation
    Tests & vérification du code et notebook (Dalia + ???)          :dalia, 2025-12-01, 2025-12-05
    Déploiement site web / app (Inès + ???)                         :ines, 2025-12-06, 2025-12-09
    Répétition présentation orale (Tous)                            :tous, 2025-12-10, 2025-12-11
    Présentation finale (Tous)                                      :tous, 2025-12-12, 2025-12-12
```

Nous avons comme objectif de réaliser un site qui ressemble aux mieux aux croquis qu'on a pu faire :

Concernant l'architecture du site, nous avons un dossier **data** où va se trouver toutes les datas qu'on va utiliser dans ce dossier on a deux sous dossiers, dans le premier il y a les datas brut et dans le deuxième se trouvera les datas qu'on a nettoyé. Nous avons également un dossier **images** dans lequel se trouve l'intégralité des croquis qu'on a pu faire et pour nous permettre de visualiser à quoi notre site doit aboutir. De plus, nous avons également un dossier **site** où va se trouver tout les fichiers menant à la création du site web. 

Concernant la pipeline, nous allons utiliser les packages suivants pour le traitement et la visualisation des données :
-pandas : manipulation et nettoyage des données
-numpy : calculs numériques
-matplotlib et seaborn : visualisations statistiques
-plotly ou leaflet : visualisations interactives (carte et graphiques dynamiques)
-quarto : génération du site web et intégration du rapport

Nous avons également créée des **branches gits**; la branche **main** qui est la version stable du projet, la branche **Data** dans laquelle on va étudier les datas et la branche **carte-interactive** dans laquelle on va créer les cartes interactives ainsi que la branche **site-web** dans laquelle on va créer le site web.


