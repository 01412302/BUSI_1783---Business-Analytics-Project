# Methodology Notes — Steam Monetization Dissertation

This document outlines the methodology used to collect, process, and analyse the Steam reviews dataset.  
It complements the dissertation **Methodology chapter** and provides technical notes for reproducibility.

---

## 🔹 Data Collection
- **Source:** Steam *appreviews* public API (no API key required).  
- **Games:** 9 monetisation-heavy titles (e.g., *Dota 2, Counter-Strike 2, Warframe, Apex Legends*).  
- **Volume:** Up to 4,000 reviews per game (~35,874 reviews total).  
- **Collection method:** Python script `scripts/steam_monetization_reviews_single_csv.py` using cursor-based pagination.  
- **Ethics:**  
  - Data collected via public API, in compliance with Steam ToS.  
  - SteamIDs removed/anonymised.  
  - Only a sample subset uploaded to GitHub for transparency (`data/all_reviews_sample.csv`).  

---

## 🔹 Data Preprocessing
Preprocessing performed in Python (`pandas`, `numpy`):  
- **Cleaning:** Removed HTML tags, newlines, special characters. Lowercased text for consistency.  
- **Deduplication:** Reviews with duplicate `recommendation_id` removed.  
- **Missing data:** Reviews without text excluded; missing playtime values replaced with `0`.  
- **Derived variables:**  
  - Converted playtime minutes → hours.  
  - `sentiment` column generated with VADER.  
  - `monetization_flag` created via regex keyword search (loot box, microtransaction, battle pass, skins, etc.).  

---

## 🔹 Analytical Techniques
Analysis conducted via the main pipeline (`scripts/analysis_pipeline.py`) and notebooks (`notebooks/`):

1. **Descriptive Statistics (EDA)**  
   - Review counts per game.  
   - Proportion of monetisation mentions.  
   - Distributions of playtime and sentiment.  

2. **Sentiment Analysis**  
   - VADER sentiment analyser used (compound score -1 to +1).  
   - Comparison between monetisation vs non-monetisation reviews.  
   - Histograms and bar charts per game.  

3. **Topic Modelling**  
   - TF-IDF vectorisation of review text.  
   - Latent Dirichlet Allocation (LDA) with 6 topics.  
   - Visual outputs: top keywords per topic (bar charts).  

4. **Clustering**  
   - Features: playtime (hours), sentiment, monetisation flag.  
   - K-Means clustering, k optimised via silhouette score.  
   - Segments identified: whales, fairness advocates, casuals, critical casuals, enthusiasts.  

5. **Predictive Modelling**  
   - Target: probability of negative review (`voted_up = 0`).  
   - Models: Logistic Regression, Random Forest Classifier.  
   - Evaluation: classification reports, confusion matrices, ROC curves, feature importance.  
   - Cross-validation: 5-fold stratified, scoring by Accuracy, F1, ROC AUC.  

---

## 🔹 Tools & Libraries
- **Python 3.10**  
- Libraries:  
  - `pandas`, `numpy` — data wrangling  
  - `matplotlib` — visualisation  
  - `vaderSentiment` — sentiment analysis  
  - `scikit-learn` — ML (TF-IDF, LDA, clustering, predictive models)  
  - `wordcloud` — word cloud visualisations  
- **Jupyter Notebook** for exploratory analysis and documentation.  

---

## 🔹 Reproducibility
- All scripts and notebooks are versioned in this repository.  
- Outputs (sample figures, tables, text summaries) are provided in `/outputs/`.  
- Full dataset not uploaded due to ethical restrictions, but sample provided.  
- Dependencies listed in `requirements.txt`.  

---

## 🔹 Limitations
- Dataset limited to Steam (PC) platform.  
- Reviews capture perceptions, not actual spending behaviour.  
- VADER sentiment analysis may misinterpret sarcasm or gaming-specific slang.  
- Data capped at ~4,000 reviews per game (API pagination limit).  

---

## 🔹 Citation
- Steamworks API: https://partner.steamgames.com/doc/store/getreviews  
- Please cite the MSc Dissertation if reusing code or methodology.  
