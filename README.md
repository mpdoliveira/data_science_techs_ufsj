[English](README.md) | [Português](README.pt-BR.md)
# Data Science Technologies — UFSJ

This repository contains projects developed for the **Data Science Technologies** elective course at the Federal University of São João del-Rei (UFSJ), taught by Prof. Carolina Xavier.

The activities explore different areas of Data Science, including clustering, graph analysis, exploratory data analysis, scientific research, statistical analysis, and distributed data processing.

## Activities

### Activity 1 — K-Means

Implementation of the **K-Means clustering algorithm from scratch using native Python**.

The main goal was to understand the internal logic of the algorithm instead of relying on ready-made Machine Learning libraries.

Main concepts:

- Unsupervised learning
- Clustering
- Euclidean distance
- Centroid calculation
- Iterative algorithms
- Convergence criteria
- CSV data processing

The algorithm was implemented without libraries such as Scikit-learn, NumPy, Pandas, or SciPy.

Directory: [`activity_1_kmeans/`](./activity_1_kmeans/)

---

### Activity 2 — Label Propagation

Implementation of a **community detection algorithm based on Label Propagation**.

The project explores graph structures and community detection by iteratively propagating labels between neighboring vertices until convergence.

Main concepts:

- Graphs and networks
- Adjacency matrices
- Community detection
- Label Propagation
- NumPy
- NetworkX
- Virtual environments with Conda
- Git and GitHub workflow

The Label Propagation algorithm itself was implemented manually rather than using an existing community detection implementation.

Directory: [`activity_2_label_propagation/`](./activity_2_label_propagation/)

---

### Activity 3 — Titanic Analysis with Pandas

Exploratory Data Analysis of the **Titanic dataset using Pandas**.

The activity investigates demographic and socioeconomic patterns associated with passenger survival.

Main analyses:

- Age distribution by sex and passenger class
- Mean, median, and standard deviation
- Survival rate by age group
- Relationship between ticket fare and survival
- Comparison between survivors and non-survivors
- Data visualization

Main technologies:

- Python
- Pandas
- Matplotlib

The activity focuses on data manipulation, aggregation, descriptive statistics, and visualization.

Directory: [`activity_3_titanic_pandas/`](./activity_3_titanic_pandas/)

---

### Activity 4 — Data Science Seminar

Technical seminar based on a recent scientific article in **Data Science, Artificial Intelligence, or Machine Learning**.

The activity focuses on reading, understanding, critically analyzing, and communicating scientific research.

The presentation covers:

- Problem definition and context
- Methodology
- Model architecture or data pipeline
- Experimental results
- Performance metrics
- Limitations
- Conclusions and future work

Directory: [`activity_4_seminar/`](./activity_4_seminar/)

---

### Activity 5 — Cadastro Único Analysis with PySpark

Exploratory analysis of the Brazilian **Cadastro Único 2018 public microdata**.

The original assignment was proposed using Pandas, but the implementation in this repository was adapted to **PySpark** in order to explore distributed data processing and efficiently work with the complete dataset.

The analysis includes:

- Age statistics grouped by sex and race/color
- Formal and informal employment analysis
- Employment rates by age group
- Income analysis by education level
- Family income aggregation
- Family income per capita
- Distribution of people with disabilities across income groups
- Missing-value treatment
- Categorical mappings
- Data bucketization

Main technologies and PySpark concepts:

- Python
- PySpark
- Apache Spark
- Spark SQL
- Spark ML `Bucketizer`
- Window functions
- DataFrame transformations and aggregations
- JSON-based category mappings

Directory: [`activity_5_pyspark/`](./activity_5_pyspark/)

---

## Technologies

Technologies and concepts explored throughout the repository include:

- Python
- Pandas
- PySpark
- Apache Spark
- NumPy
- NetworkX
- Matplotlib
- Conda
- Python virtual environments
- Git
- GitHub
- Exploratory Data Analysis
- Statistical analysis
- Clustering
- Graph algorithms
- Community detection
- Distributed data processing

## Repository Structure

```text
data_science_techs_ufsj/
├── activity_1_kmeans/
├── activity_2_label_propagation/
├── activity_3_titanic_pandas/
├── activity_4_seminar/
├── activity_5_pyspark/
├── .gitattributes
└── README.md
