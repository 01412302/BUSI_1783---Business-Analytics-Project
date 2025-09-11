# Data Dictionary — Steam Monetization Dissertation

This document describes the variables contained in the dataset `all_reviews.csv`, which was collected from Steam’s public *appreviews* API.  
The dataset includes metadata and user-generated review text for nine monetisation-heavy games (see Methodology section of the dissertation).

---

## 🔹 Dataset Overview
- **Source:** Steam public appreviews API  
- **Collection period:** 2025 (up to 4,000 reviews per game)  
- **Sample size:** 35,874 reviews across 9 games  
- **Unit of analysis:** One row = one unique Steam review  
- **Ethics:** SteamIDs anonymised; only a sample subset uploaded to GitHub (`all_reviews_sample.csv`).  

---

## 🔹 Variables

| Column Name | Type | Description |
|-------------|------|-------------|
| `platform` | string | Data source platform (`steam`) |
| `appid` | int | Steam application ID for the game |
| `app_name` | string | Name of the game reviewed |
| `monetization_model` | string | Notes on the primary monetisation strategy for the game (e.g., cosmetics, battle pass, expansions) |
| `recommendation_id` | string | Unique identifier for the review |
| `language` | string | Language of the review text |
| `review_text` | string | Raw review text provided by the user |
| `text_clean` | string | Cleaned version of the review text (lowercased, special characters removed) |
| `timestamp_created` | datetime | ISO timestamp when the review was created |
| `timestamp_updated` | datetime | ISO timestamp when the review was last updated |
| `voted_up` | boolean | Whether the user recommended the game (thumbs up) |
| `votes_up` | int | Number of “helpful” votes the review received |
| `votes_funny` | int | Number of “funny” votes the review received |
| `weighted_vote_score` | float | Normalised helpfulness score from Steam |
| `steam_purchase` | boolean | Whether the review came from a verified Steam purchase |
| `received_for_free` | boolean | Whether the reviewer received the game for free |
| `written_during_early_access` | boolean | Whether the review was written during early access |
| `author_steamid` | string | Reviewer SteamID (anonymised or excluded for ethics compliance) |
| `author_num_games_owned` | int | Number of games owned by the reviewer |
| `author_num_reviews` | int | Number of reviews the author has written |
| `author_playtime_forever_m` | int | Total playtime across the game (in minutes) |
| `author_playtime_last_two_weeks_m` | int | Playtime in the last two weeks (minutes) |
| `author_playtime_at_review_m` | int | Playtime recorded at the time of writing the review (minutes) |
| `author_playtime_forever_h` | float | Total playtime converted to hours |
| `author_playtime_last_two_weeks_h` | float | Playtime in last two weeks converted to hours |
| `author_playtime_at_review_h` | float | Playtime at review time converted to hours |
| `author_last_played` | int | Timestamp of the author’s last played session (epoch seconds) |
| `sentiment` | float | Sentiment score (VADER compound: -1 = negative, +1 = positive) |
| `monetization_flag` | boolean | Flag indicating whether review mentions monetisation (loot boxes, microtransactions, battle pass, etc.) |

---

## 🔹 Notes
- All times are converted to **UTC ISO 8601** format where applicable.  
- Playtime variables are provided in both minutes (raw from Steam) and hours (derived).  
- Sentiment values generated using **VADER sentiment analysis**.  
- `monetization_flag` created via regex keyword matching (loot box, pay-to-win, skins, etc.).  
- Only `all_reviews_sample.csv` is uploaded for reproducibility. The full dataset was used for analysis but cannot be redistributed.  

---

## 🔹 Citation
If using this dataset structure, please cite the dissertation and Steam as the original data source:  
- Steamworks API: https://partner.steamgames.com/doc/store/getreviews
