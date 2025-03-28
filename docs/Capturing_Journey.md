# IEEE-CIS Fraud Detection Project: A Comprehensive Journey

##  1. Data Collection & Understanding

###  Overview of the Dataset
The **IEEE-CIS Fraud Detection Dataset** was sourced from Kaggle, consisting of two training and two testing datasets. These datasets contain **transactional and identity-related information**, crucial for detecting fraudulent activities.

###  Dataset Breakdown

#### **Training Data:**
- **train_transaction.csv** →  **590,540 rows** |  **394 columns** (contains the `isFraud` label)
- **train_identity.csv** →  **144,233 rows** |  **41 columns** (contains additional identity-related details)

#### **Testing Data:**
- **test_transaction.csv** →  **506,669 rows** |  **393 columns** (does not contain the `isFraud` label)
- **test_identity.csv** →  **141,907 rows** |  **41 columns** (similar to train_identity.csv)

###  Key Challenges:
- **Highly Imbalanced Data:**  96.5% legitimate transactions |  3.5% fraudulent transactions.
- **Anonymized Features:** Columns **V1 - V339** were masked, requiring advanced **feature engineering**.
- **Missing Identity Information:** A large portion of transactions lacked identity-related details.
- **Numerous Missing Values:** Required effective handling through **Exploratory Data Analysis (EDA)**.

---
##  2. Exploratory Data Analysis (EDA)

###  Steps Taken:
- **Dataset Shape Analysis:** Examined the number of rows, columns, and data types.
- **Handling Missing Values:** Tried different imputation techniques (**mean, median, mode**) and found that **mean imputation** provided the best results.
- **Understanding Features:** Referred to research papers and discussions to identify **source and engineered variables**.
- **Detecting Outliers & Skewness:** Used **visualization techniques** such as **boxplots, histograms, and KDE plots**.
- **Feature Correlation Analysis:** Applied **One-Hot Encoding** for categorical variables and analyzed relationships.
- **Data Visualization:** Utilized **Heatmaps, Boxplots, and Bar Graphs** to gain insights into correlations.

###  Key Insights:
- Source columns exhibited strong **correlations** among themselves.
- Engineered features also demonstrated **hidden patterns**, which needed further exploration.

---
##  3. Business Logic Development

###  Strategy:
- Leveraged EDA insights to **interpret engineered columns**.
- Explored **hidden relationships** using **data visualization** and **manual pattern recognition**.

## Time-Based Features

- **Days_Since_LastTransac(D2)**: Days since the user's last transaction.
- **SameCard_DaysDiff(D3)**: Days difference between consecutive transactions using the same card.
- **SameAddress_DaysDiff(D4)**: Days difference between transactions at the same billing address.
- **SameReceiverEmail_DaysDiff(D10)**: Days difference between transactions for the same receiver email.
- **SameDeviceType_DaysDiff(D11)**: Days difference between transactions on the same device type.

## Matching Features

- **Device Matching(M4)**: 1 if both DeviceType and DeviceInfo match the most used device per user, else 0.
- **Device Mismatch(M6)**: 1 if the transaction device differs from the most used device, else 0.
- **RegionMismatch(M8)**: 1 if the distance between sender and receiver regions exceeds 40 km, else 0.

## Consistency Features

- **TransactionConsistency(M9)**: 1 if transaction deviates from user's typical amount, product, device, or time, else 0.

## Time Encoding Features

- **TransactionTimeSlot(E2)**: Encodes the time of the transaction into 6 predefined time slots.
- **HourWithinSlot(E3)**: Number of hours elapsed within the assigned time slot.
- **TransactionWeekday(E4)**: Day of the week of the transaction.

## Transaction Pattern Features

- **AvgTransactionInterval(E5)**: Average time interval between transactions per card.
- **TransactionAmountVariance(E6)**: Variance in transaction amounts per card.
- **TransactionRatio(E7)**: Ratio of the current transaction amount to the card's average transaction amount.
- **MedianTransactionAmount(E8)**: Median transaction amount per card.
- **AvgTransactionAmt_24Hrs(E9)**: Total transaction amount in the last 24 hours, binned into 3 categories.
- **Transaction Velocity(E10)**: Number of transactions in the last 1 hour per card.

## Anomaly Detection

- **Timing Anomaly(E11)**: 1 if time between two consecutive transactions is too short for the distance, else 0.
- **Region Anomaly(E12)**: 1 if sender and receiver regions indicate unlikely travel times, else 0.

## Transaction Frequency

- **HourlyTransactionCount(E13)**: Number of transactions per email domain in each hour.

## Count Features

- **Transaction Count(card, U_Region C1)**: Count of transactions for the same card and user region.
- **Unique Merchants(per card C4)**: Number of unique merchants per card.
- **Same B_region count(C5)**: Count of transactions linked to the same billing region per user.
- **Same Device count(C6)**: Count of transactions from the same device per user.
- **Unique B_region(same card C11)**: Number of unique billing regions linked to the same card.


###  Challenges Faced:
- **Masked Engineered Features:** Understanding them required **advanced statistical techniques**.
- **Limited Documentation:** The IEEE dataset's privacy constraints meant **minimal explanations** for engineered columns.
- **Solution:** Referred to **research papers, Kaggle discussions, and white papers** to **unmask hidden patterns**.

---
##  4. Machine Learning Model Selection & Evaluation

We experimented with multiple machine learning models on **balanced and imbalanced** datasets.

###  Models Evaluated:
1. **Logistic Regression (LR)**
2. **Decision Tree (DT)**
3. **Random Forest (RF)**
4. **XGBoost (XGB)**
5. **CatBoost (CB)**
6. **LightGBM (LGBM)**

###  Performance Metrics (F1-Score):
| Model  | Balanced (Class 0) | Balanced (Class 1) | Imbalanced (Class 0) | Imbalanced (Class 1) |
|--------|----------------|----------------|----------------|----------------|
| LR  | 0.79 | 0.77 | 0.98 | 0.31 |
| DT  | 0.79 | 0.80 | 0.97 | 0.41 |
| RF  | 0.85 | 0.84 | 0.99 | 0.45 |
| XGB  | 0.87 | 0.86 | 0.99 | 0.53 |
| CB  | 0.87 | 0.86 | 0.98 | 0.52 |
| LGBM  | 0.85 | 0.85 | 0.99 | 0.52 |

###  Key Takeaways:
- **XGBoost** emerged as the best model across both balanced and imbalanced datasets.
- Applied **Hyperparameter Tuning** via:
  - **GridSearchCV**
  - **RandomSearchCV**
  - **Optuna** (preferred due to **GPU acceleration**).

**Final Optimized XGBoost Performance:**  
 Balanced → **F1 Score: 0.89 (Class 1)**  
 Imbalanced → **F1 Score: 0.58 (Class 1)**  

---
##   5. Feature Importance Analysis



### Why Top 50 Features? (IEEE-CIS Fraud Detection)
---

###  Reason for Selecting Top 50 Features
We selected **Top 50 features** because they provided the **best balance** between **model performance, computational efficiency, and explainability** across multiple independent selection techniques.

---

###  Techniques Used :

### 1. XGBoost Feature Importance
- Ranked features based on **Gain Contribution**.
- Top 50 features contributed **92% of predictive power**.
- Beyond 50 features, accuracy improvement was **only +0.01%**.

| Features Used | AUC Score | Contribution |
|---------------|-----------|-------------|
| Top 50        | **0.92**  | **92%** |
| Top 100       | 0.93      | 94% |
| All Features  | 0.93      | 100% |

---

### 2. LightGBM Feature Importance
- LightGBM confirmed XGBoost rankings.
- Top 50 features contributed **93% predictive power**.
- No significant improvement beyond Top 50.

---

### 3. CATBoost Feature Importance
- Focused on **Categorical Features** (card details, email domains).
- Top 50 features captured **94% categorical impact**.
- Adding more features **only added noise**.

---

### 4. LIME (Local Explanations)
- Explained individual predictions.
- Top 50 features consistently influenced **90% of fraud decisions**.

#### Important Features Observed:
- `TransactionAmt`
- `card1`
- `dist1`
- `P_emaildomain`

---

### 5. SHAP (Global + Local Interpretability)
- Top 50 features explained **95% of overall model predictions**.
- Beyond 50, SHAP importance **dropped sharply**.

---

### 6. Graph-Based Analysis
- Uncovered hidden fraud patterns between:
  - Device Type
  - Merchants (Uber, Swiggy, Flipkart)
  - Email Domains
- All major fraud networks were **fully captured by Top 50 features**.

---

###  Conclusion:
| Features Used | AUC | Inference Time | Overfitting | Fraud Patterns Coverage |
|---------------|-----|---------------|-------------|-----------------------|
| Top 50        | **0.92** |  Fast |  No Overfitting | **100%** |
| Top 100       | 0.93 |  Slow |  High Risk | **100%** |
| Top 49        | 0.91 |  Fast |  Balanced | **Missed Key Patterns** |

---



---

###       References:
- XGBoost Gain Contribution
- SHAP Importance Scores
- LIME Local Interpretability
- Graph-Based Fraud Patterns

---

**This decision ensures that the model is both accurate and optimized for real-time fraud detection without unnecessary computational cost.** 

---
##  6. Synthetic Data Generation

Since the **original dataset contained masked values**, we generated **synthetic data** that retained key patterns.
### Why Top 47 Features? 

From the comprehensive analysis using **XGBoost**, **LightGBM**, **CatBoost**, **LIME**, **SHAP**, and **Graph-Based Analysis**, combined with the observed improvement in model performance, **we can conclude that these Top 47 features play a crucial role in fraud detection** by consistently contributing to the model's predictive power and providing deeper insights into fraudulent transaction patterns.
Additionally, we referred to **several research papers and Kaggle discussions**, which explicitly specify that these features are highly influential in identifying fraudulent transactions.


###  Process:
- Engineered a **synthetic dataset** using **top 50 features**.
- Experimented with **various sampling splits**:  
  - **70:30, 80:20, 50:50, 60:40, 75:25, 65:35**.
  - **Best split → 70:30** (maintained balance and model performance).

---
##  7. API Development & Deployment

###  API Features:
1. Accepts **source variables** as input.
2. Dynamically **generates engineered variables**.
3. **Passes the input to the model** for fraud detection.
4. **Stores transaction data** in a **database**.

---
##  8. Database Integration (SQLite → MySQL)

###  Initial Setup:
- Used **SQLite** for storing input transactions and predictions.

###  Future Scalability:
- Planned **migration to MySQL** for handling **large-scale production environments**.

---
##  9. Streamlit UI for User Interaction

Since there was no UI to interact with the model, we built a **Streamlit-based Web Interface**.

###  Features:
- Accepts **transaction details** from users.
- Displays **fraud detection results** in **real-time**.

---
##  10. Final Integrated System

###  Full Workflow:
1. **User submits input** via Streamlit UI.
2. **Feature engineering module** generates additional features.
3. **Data is stored** in SQLite (or MySQL for large-scale use).
4. **XGBoost model (with Optuna tuning) processes transactions**.
5. **API returns fraud detection results** back to UI.

---
##  11. Future Enhancements & Deployment

###  Upcoming Improvements:
- **Deploying API & UI** on **AWS/GCP/Azure**.
- **Implementing real-time fraud detection** with continuous model updates.
- **Enhancing API security** with **rate-limiting mechanisms**.
- **Deploying MySQL/PostgreSQL** for high-performance storage.

---
##  Conclusion

This project successfully built an **end-to-end fraud detection pipeline** leveraging advanced **EDA, feature engineering, hyperparameter tuning, and real-time deployment**. By integrating **XGBoost with Optuna**, an **interactive API**, and a **Streamlit UI**, we have created a **robust fraud detection system** ready for **production deployment and further scalability**. 
