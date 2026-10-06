[English](README.md) | [Português](README.pt-BR.md)

# Cadastro Único 2018 Analysis with PySpark

## Overview

This project analyzes the **2018 Cadastro Único public microdata** using **PySpark**. It was developed for Activity 5 of the *Data Science Technologies* course at the Federal University of São João del-Rei (UFSJ).

The original assignment specified Pandas. This implementation uses PySpark to process both a sample and the complete dataset.

## Analyses

The project implements the following analyses:

1. Age distribution by sex and race/color.
2. Employment-income classification among individuals aged 18–65.
3. Annual gross income by educational category and completion status.
4. Paid work by age group.
5. Proportion of people with disabilities (PCD) by family income per capita.

## Technologies

- Python
- PySpark
- Apache Spark
- Spark SQL
- Spark ML `Bucketizer`
- Spark Window functions
- JSON-based categorical mappings

## Project Structure

```text
activity_5_pyspark/
├── main.py
├── labels.json
├── amostra.csv/
└── README.md
```

`labels.json` stores dataset column names, categorical mappings, and interval definitions used by the analyses.

## Running the Project

### Sample dataset

```bash
python main.py
```

Default input:

```text
amostra.csv/*.csv
```

### Complete dataset

The complete `PESSOA_2018.TXT` file is semicolon-delimited:

```bash
python main.py "C:\path\to\PESSOA_2018.TXT" ";"
```

## Data Processing

### Age

Age is approximated from the reference year:

```text
age = 2018 - birth year
```

Records with calculated ages outside `0–130` are excluded.

| Age group | Range |
|---|---:|
| Criança | 0–12 |
| Adolescente | 13–19 |
| Jovem | 20–29 |
| Adulto | 30–59 |
| Idoso | 60–130 |

### Categorical variables

Numerical codes are converted to descriptive labels using Spark map expressions and mappings stored in `labels.json`.

Examples:

```text
Sex
1 → Homem
2 → Mulher
```

```text
Race/color
1 → Branca
2 → Preta
3 → Amarela
4 → Parda
5 → Indígena
```

### Family income per capita

Annual income is aggregated by family identifier and converted to estimated monthly income per capita:

```text
monthly family income per capita = annual family income / family members / 12
```

Income groups used in the analysis:

| Group | Monthly family income per capita |
|---|---:|
| 1 | R$ 0 ≤ income < R$ 109 |
| 2 | R$ 109 ≤ income < R$ 218 |
| 3 | R$ 218 ≤ income < R$ 477 |
| 4 | R$ 477 ≤ income < R$ 999,999 |

R$ 477 corresponds to half of the 2018 minimum wage used as the reference for this analysis.

---

# Results

## 1. Age Distribution by Sex and Race/Color

| Race/Color | Sex | Mean | Median | Std. Dev. |
|---|---|---:|---:|---:|
| Branca | Homem | 27.59 | 20.00 | 22.12 |
| Branca | Mulher | 31.29 | 29.00 | 21.45 |
| Preta | Homem | 31.71 | 28.00 | 21.01 |
| Preta | Mulher | 34.76 | 34.00 | 19.09 |
| Amarela | Homem | 27.20 | 20.00 | 21.96 |
| Amarela | Mulher | 30.93 | 29.00 | 20.48 |
| Parda | Homem | 25.58 | 19.00 | 20.04 |
| Parda | Mulher | 28.59 | 26.00 | 19.26 |
| Indígena | Homem | 20.87 | 16.00 | 17.02 |
| Indígena | Mulher | 23.19 | 20.00 | 16.95 |

### Result

Women have higher mean and median ages than men in every race/color group. Black women have the highest mean age (`34.76`), and Indigenous men have the lowest (`20.87`). Standard deviations range from `16.95` to `22.12`, indicating substantial age dispersion within all groups.

---

## 2. Employment-Income Classification Among Individuals Aged 18–65

| Current classification | Percentage |
|---|---:|
| Yes | 93.69% |
| No | 6.31% |

### Methodological note

The current implementation does **not directly identify formal and informal employment**. It classifies records as `No` when annual gross income is non-zero and employment income is zero; all other records are classified as `Yes`.

Therefore, the percentages above should not be interpreted as a valid estimate of formal versus informal employment. This analysis requires a variable or rule that directly represents employment formality before the result can answer the original research question.

---

## 3. Annual Gross Income by Educational Category

Income statistics are grouped by previously attended educational category and whether the corresponding course was completed.

| Education | Completed | Mean | Median | Std. Dev. |
|---|---|---:|---:|---:|
| Creche | Yes | 3,292.17 | 1,820.00 | 3,729.92 |
| Creche | No | 1,405.66 | 900.00 | 1,653.52 |
| Pré-escola | Yes | 2,846.55 | 1,300.00 | 3,722.66 |
| Pré-escola | No | 2,154.97 | 1,000.00 | 2,964.04 |
| Alfabetização | Yes | 2,461.25 | 1,200.00 | 3,356.18 |
| Alfabetização | No | 2,115.81 | 1,200.00 | 3,110.43 |
| Fundamental I | Yes | 4,850.94 | 2,500.00 | 5,716.49 |
| Fundamental I | No | 3,574.90 | 1,800.00 | 4,709.73 |
| Fundamental II | Yes | 5,427.11 | 3,012.00 | 6,003.69 |
| Fundamental II | No | 4,560.32 | 2,400.00 | 5,353.12 |
| Fundamental 9 anos | Yes | 4,107.99 | 2,000.00 | 5,156.41 |
| Fundamental 9 anos | No | 3,863.26 | 1,800.00 | 5,148.66 |
| Fundamental Especial | Yes | 5,433.12 | 2,640.00 | 6,682.64 |
| Fundamental Especial | No | 4,175.99 | 2,000.00 | 5,379.35 |
| Ensino Médio | Yes | 6,739.31 | 4,400.00 | 6,989.25 |
| Ensino Médio | No | 5,039.32 | 2,800.00 | 5,699.39 |
| Médio Especial | Yes | 6,570.74 | 3,600.00 | 7,509.66 |
| Médio Especial | No | 5,106.39 | 2,400.00 | 6,168.80 |
| EJA Fundamental I | Yes | 3,106.75 | 1,455.00 | 4,122.45 |
| EJA Fundamental I | No | 2,622.58 | 1,200.00 | 3,656.59 |
| EJA Fundamental II | Yes | 3,807.57 | 2,000.00 | 4,555.03 |
| EJA Fundamental II | No | 3,417.36 | 1,800.00 | 4,530.67 |
| EJA Médio | Yes | 5,426.70 | 3,600.00 | 5,603.10 |
| EJA Médio | No | 4,914.21 | 2,880.00 | 5,368.28 |
| Superior | Yes | 10,251.42 | 10,307.00 | 8,891.10 |
| Superior | No | 9,326.86 | 9,000.00 | 8,427.37 |
| Alfabetização Adultos | Yes | 2,952.17 | 1,200.00 | 4,449.89 |
| Alfabetização Adultos | No | 2,154.75 | 1,020.00 | 3,187.98 |
| Nenhum | Yes | 4,287.55 | 2,400.00 | 4,981.06 |
| Nenhum | No | 2,940.84 | 1,800.00 | 3,351.01 |

### Result

The `Superior` category has the highest mean and median annual gross income. For every educational category shown, the mean income is higher among records marked as completed than among those marked as not completed. The large standard deviations indicate substantial within-group income dispersion.

---

## 4. Paid Work by Age Group

Paid work is defined as employment income greater than zero.

| Age group | Works | Percentage |
|---|---|---:|
| Criança | Yes | 2.02% |
| Criança | No | 97.98% |
| Adolescente | Yes | 3.60% |
| Adolescente | No | 96.40% |
| Jovem | Yes | 32.62% |
| Jovem | No | 67.38% |
| Adulto | Yes | 48.16% |
| Adulto | No | 51.84% |
| Idoso | Yes | 10.85% |
| Idoso | No | 89.15% |

### Result

Adults have the highest proportion of records with employment income (`48.16%`), followed by young adults (`32.62%`). The corresponding proportions are `10.85%` among older adults, `3.60%` among adolescents, and `2.02%` among children.

---

## 5. People with Disabilities by Family Income per Capita

| Family income per capita | PCD |
|---|---:|
| R$ 0 ≤ income < R$ 109 | 1.97% |
| R$ 109 ≤ income < R$ 218 | 2.85% |
| R$ 218 ≤ income < R$ 477 | 3.19% |
| R$ 477 ≤ income < R$ 999,999 | 3.75% |

### Result

The observed proportion of people with disabilities increases across the four income groups, from `1.97%` in the lowest group to `3.75%` in the highest. This is a descriptive association and does not establish causality.

---

## Implementation

- `spark_map()` maps coded categorical values to readable labels using Spark expressions.
- `spark_bucketizer()` applies Spark ML `Bucketizer` and maps bucket indexes to category labels.
- Spark Window functions calculate group-relative percentages without additional aggregation joins.
- `labels.json` centralizes categorical mappings and interval definitions.

## Methodological Limitations

- Age is approximated from birth year; exact birthdays are not considered.
- Records with calculated ages outside `0–130` are excluded.
- Missing values are excluded according to the variables required by each analysis.
- The current formal/informal employment classification is not a direct measure of employment formality and should be revised before drawing conclusions about formal work.
- The education analysis uses annual gross income (`VL_RENDA_BRUTA_12_MESES_MEMB`), not employment income.
- The education variable represents the previously attended course and its completion status; it should not automatically be interpreted as the individual's highest completed educational level without confirmation from the dataset documentation.
- In the PCD analysis, records with missing disability status are removed before family size is calculated. Consequently, the estimated family size and per-capita income may be affected when disability information is missing.
- Results describe the analyzed Cadastro Único records and should not be generalized to the Brazilian population without an appropriate sampling design and weighting procedure.

## Potential Extensions

- Add visualizations for the reported analyses.
- Define an explicit Spark schema instead of using `inferSchema=True`.
- Validate categorical codes and interval boundaries against the official data dictionary.
- Refine missing-data treatment.
- Integrate municipal indicators using the IBGE municipality code.
- Export processed results to CSV or Parquet.
- Add automated tests for helper functions and category mappings.