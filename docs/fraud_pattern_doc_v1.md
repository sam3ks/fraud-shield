# Fraud Detection Patterns
## Features Used for Fraud Detection
### Anomaly-Based Features:
- **AvgTransactionAmt_24Hrs_E9** - The average amount of transactions in the last 24 hours.
- **TransactionRatio_E7** - The ratio of the current transaction amount compared to past transactions.
- **MedianTransactionAmount_E8** - The median transaction amount for a user.
- **AvgTransactionInterval_E5** - The average time gap between transactions.
- **TransactionVelocity_E10** - Number of transactions happening within a short time.
- **TimingAnomaly_E11** - Transactions occurring at unusual times.
- **RegionAnomaly_E12** - Transactions happening in unexpected locations.

### Email-Based Features:
- **Sender_email** - The email address used in a transaction.
- **CardNumber** - The card number linked to the transaction.

### Timing-Based Features:
- **HourWithinSlot_E3** - The time slot in which a transaction occurs.

### Location-Based Features:
- **Order_Region** - The region where the transaction is happening.
- **TransactionDT** - The timestamp of the transaction.

---

## Fraud Detection Patterns and Their Working
### 1. Amount Anomaly-Based Fraud Detection
#### How It Works:
1. The system checks for unusual spending behavior using multiple indicators like transaction amount, frequency, and time gaps.
2. It calculates how many fraud indicators are triggered for a transaction.
3. If **3 or more indicators** are found, along with a major transaction amount variation (**TransactionAmountVariance_E6**), the transaction is marked as fraudulent.
4. This helps identify transactions that stand out significantly from a user's usual pattern.

#### Example:
- A user usually spends **₹2,000 per day**, but suddenly, there are **3 transactions of ₹50,000 each** within an hour. Since multiple anomaly indicators are triggered, the transaction gets flagged.

---

### 2. Sender Email Fraud Detection
#### How It Works:
1. New domain or new email during the second transaction 
2. Along with "Amount_Variance" and "Transaction_Velocity" 
shiuld be '1'.


#### Example:
- A card was previously used with emails (A, B, C). Now, a transaction comes from email **D**. Since multiple emails were already associated with the card, the system flags this as a potential fraud attempt.

---

### 3. Transaction Velocity Detection
#### How It Works:
1. "Amount_Variance" , "Timing_Anomely" and "Device_Mismatch"
  should be equal to '1'.

#### Example:
- If a user makes **7 transactions in 30 minutes**, which is much higher than their usual pattern, the transaction is flagged as potential fraud.

---

### 4. Timing Anomaly Detection
#### How It Works:
1. The system analyzes when a user usually makes transactions based on **HourWithinSlot_E3**.
2. If a transaction happens at a time that is very rare for that user (less than **20% of their past transactions** in that time slot), it gets flagged.
3. This helps in detecting fraud where transactions occur at odd hours.
4. Along with "Amount_Variance" should be '1'. 

#### Example:
- A user mostly makes transactions between **10 AM - 6 PM**, but suddenly a transaction happens at **3 AM**. The system flags it as suspicious since it is unusual for this user.

---

### 5. Region Anomaly Detection
#### How It Works:
1. The system tracks where the transactions are happening using **Order_Region**.
2. It calculates the distance and time difference between two consecutive transactions.
3. If the required speed to travel between two transactions exceeds **30 km/h**, the transaction is flagged as suspicious.
4. This helps detect fraud where transactions occur in locations that are too far apart to be realistic.
5. "Timing_Anomely" , "Email_Flag_Fraud" should be '1' and the transaction must be consistent 

#### Example:
- A user makes a transaction in **Bangalore at 10:00 AM** and another in **Mumbai at 10:30 AM**. Since it is impossible to travel that far in 30 minutes, the system flags it as fraud.

---
### 6. Flagging Cards Used by Multiple Users Suspicously
### **Pattern Explanation:**
In a legitimate scenario, a credit or debit card is typically used by a single user or few other users close to the single user. However, fraudulent activities often involve the use of stolen or shared card information across multiple accounts and also involves a high volume of transactions in a short period, aiming to exploit the card before detection and cancellation.. To detect such cases, we:

- **Group transactions by CardNumber** and count the number of unique users (User_IDs) associated with each card.
- **Flag any card used by more than one user** as potentially fraudulent.
- **Apply a fraud flag (CardFraudFlag = 1)** to transactions involving such cards.

- Same CardNumber has been used by more then 1 user 
- If multiple Transaction has been occured by another user  within an hour and  the Amount average of the Card has been crossed then these is suspicious   
---

### 7. High-Risk Region and Large Transaction Detection

#### How It Works:

1. The system checks if the **Order_Region** belongs to a predefined list of **high-risk regions**.

2. It then verifies if the transaction amount exceeds a certain **threshold (₹10,000)**.

3. If both conditions are met and the original fraud probability is **50% or lower**, the fraud probability is slightly increased to a range between **26% and 50%**.

4. This ensures transactions in high-risk areas with large amounts get additional scrutiny.
 
#### Example:

- A user makes a transaction of **₹15,000 in Bangalore**, which is a high-risk region.

- The initial fraud probability was **40%**.

- Since the amount is above the threshold, the fraud probability is adjusted within the **26%-50%** range for further analysis.

---
### 8. **Business Email Compromise (BEC) Fraud Detection**

## **Overview**
Business Email Compromise (BEC) fraud is a sophisticated scam where attackers impersonate executives, vendors, or trusted entities to trick employees into transferring funds to fraudulent accounts. These attacks often bypass traditional security measures since they rely on social engineering rather than malware.

### **How Attackers Execute BEC Fraud**
1. **Domain Spoofing** - Attackers use a domain that closely resembles a legitimate company email.
2. **Suspicious Domains** - Fraudsters register domains with minor spelling variations (e.g. '@mailinator.com', '@guerrillamail.com', @tempmail.com, @10minutemail.com).
3. **Compromised Email Accounts** - Hackers gain access to a real business email and use it to request fraudulent transactions.
4. **Urgency & Confidentiality** - Attackers pressure employees by creating urgent requests to bypass verification.
---

### 9. Inactivity Followed by Large Transaction Detection
#### How It Works:
1. The system tracks the number of days since a user’s last transaction (**DaysSinceLastTransac_D2**).
2. If a user has been inactive for **more than 90 days**, the transaction is flagged under **InActivity_gap_E14**.
3. After detecting inactivity, the system checks if the transaction amount is more than **3 times the user’s average transaction amount**.
4. If both conditions are met, the transaction is flagged under **HighAmount_PostInactivity_E15**.
5. This helps identify fraudsters who stay inactive for a long time and suddenly make large transactions.
 
#### Example:
- A user has not made any transactions for **120 days**.
- Their average transaction amount is **₹5,000**, but suddenly, they make a **₹20,000** transaction.
- Since this is **more than 3 times** their usual spending after a long inactivity period, it is flagged for further investigation. 

---
### 10. Frequent Email Domain Changes Detection
#### How It Works:
1. The system tracks changes in **email domains** used by a user within a **30-day period**.
2. For each transaction, it retrieves all email domains used by the user in the last 30 days.
3. If a user has used **more than 4 different email domains** in this period, the transaction is flagged under **EmailDomainChanges_30D**.
4. This helps detect fraudsters who frequently change email domains to bypass security measures.
 
#### Example:
- A user makes multiple transactions over a month using different email domains:  
  **abc@gmail.com, xyz@yahoo.com, pqr@outlook.com, mno@rediffmail.com, jkl@protonmail.com**.
- Since the user has changed **more than 4 email domains within 30 days**, the system flags this activity as suspicious.

---

### 11. Late-Night Testing Pattern Detection
#### How It Works:
1. Fraudsters often test stolen cards by making **small transactions late at night** (between **12 AM - 5 AM**) before attempting **larger purchases**.
2. The system tracks transactions occurring during this late-night window using **TransactionTimeSlot_E2**.
3. If a **small transaction** (less than **25% of the user's average spending**) is followed by a **large transaction within 24 hours**, the pattern is flagged.
4. This helps detect fraudulent activities where fraudsters check if a card is active before making significant purchases.
 
#### Example:
- A user usually spends **₹5,000 per transaction**.
- At **2:30 AM**, a small transaction of **₹1,00** is made.
- The same user makes a **₹30,000 transaction** at **11:00 AM** on the same day.
- Since a small transaction was followed by a large one within 24 hours, the system flags this as a **Late-Night Testing Pattern**.

---
### 12. Detecting Unauthorized Transactions
 
Unauthorized transactions using stolen credit cards can be effectively detected by analyzing multiple features, including:
 
- **TransactionVelocity**: Measures the rate at which transactions occur over a specified period. A sudden spike in transaction velocity often indicates fraudulent activity.
- **M6 (Device Mismatch)**: Flags inconsistencies between the user’s current device and previous devices used for legitimate transactions.
- **M8 (Region Mismatch)**: Identifies mismatches between the user’s current region and their usual transaction regions, suggesting potential fraud.

---
### 13. Multiple Transactions with Changing Delivery Regions 

This fraud pattern occurs when a **single user account** makes **multiple transactions** within a **short time frame**, frequently changing the **delivery region** for each order. This behavior is highly suspicious as legitimate users usually have a consistent delivery address or a limited set of locations they use regularly. 

1. **Stolen Payment Methods** – The user might be testing **stolen credit/debit cards** by placing orders to different regions.  
2. **Reselling Fraud** – Fraudsters could be purchasing goods to **resell in different locations**, often using fake or synthetic identities.  
3. **Promotion Abuse** – They may be exploiting **regional discounts or offers** by changing locations to avail multiple benefits.  
4. **Account Takeover (ATO)** – A hacker may be testing the compromised account across various locations.  
5. **Delivery Scam** – Fraudsters could be rerouting deliveries to **untraceable drop locations** for theft.  

---
### 14. **Synthetic Identity Fraud Detection**

## **Overview**
Synthetic identity fraud involves creating fake identities by combining real and fabricated information. This detection method assigns fraud scores based on various behavioral and transactional patterns.

## **Fraud Detection Patterns**
Each fraud pattern contributes to an overall fraud score. The higher the score, the higher the likelihood of fraudulent activity.

### **Pattern 1: Email Fraud Flag**
- If an email is flagged as fraudulent, a fraud score of **25** is assigned.
```python
fraud_score_email = df['EmailFraudFlag'].iloc[-1] * 25
```

### **Pattern 2: Transaction Velocity**
- If the transaction velocity (number of transactions in a short time) exceeds **5**, a fraud score of **20** is assigned.
```python
fraud_score_velocity = (1 if df['TransactionVelocity_E10'].iloc[-1] > 5 else 0) * 20
```

### **Pattern 3: Region and Device Mismatch/Anomaly**
- Region and device inconsistencies contribute to the fraud score:
  - **Region Anomaly:** +15 points
  - **Device Mismatch:** +5 points
  - **Region Mismatch:** +5 points
```python
fraud_score_region_device = (
    df['RegionAnomaly_E12'].iloc[-1] * 15 +
    df['DeviceMismatch_M6'].iloc[-1] * 5 +
    df['RegionMismatch_M8'].iloc[-1] * 5
)
```

### **Pattern 4: Transaction Amount Variance and Timing Anomaly**
- **High variance in transaction amount (>10,000):** +10 points
- **Timing anomaly detected:** +20 points
```python
fraud_score_amount_timing = (
    (1 if df['TransactionAmountVariance_E6'].iloc[-1] > 10000 else 0) * 10 +
    df['TimingAnomaly_E11'].iloc[-1] * 20
)
```

### **Pattern 5: Device Matching and Region Mismatch Conditional**
- If **Transaction Ratio = 1** and **Region Mismatch = 1**, assign **10 points**
- If **Device Matching = 0**, assign **5 points**
```python
fraud_score_device_region_conditional = (
    (10 if df['TransactionRatio_E7'].iloc[-1] == 1 and df['RegionMismatch_M8'].iloc[-1] == 1 else 0) +
    (5 if df['DeviceMatching_M4'].iloc[-1] == 0 else 0)
)
```

### **Pattern 6: Device Mismatch, Timing Conditional, and Other Conditionals**
- If **Device Mismatch = 1** and **Timing Anomaly = 1**, assign **15 points**
- If **Hourly Transaction Count > 3**, assign **10 points**
- If **Same Card Days Difference < 0.01**, assign **15 points**
```python
fraud_score_device_timing_other_conditionals = (
    (15 if df['DeviceMismatch_M6'].iloc[-1] == 1 and df['TimingAnomaly_E11'].iloc[-1] == 1 else 0) +
    (10 if df['HourlyTransactionCount_E13'].iloc[-1] > 3 else 0) +
    (15 if float(df['SameCardDaysDiff_D3'].iloc[-1]) < 0.01 else 0)
)
```
---
### 14. Multiple Users with the Same Phone and Card Detection
#### How It Works:
1. The system tracks how many times a unique combination of **Phone Number and Card Number** has been used.
2. A **CountOfUsers** variable is maintained, which increases every time the same phone number and card number combination appears in transactions.
3. If the same **Phone Number and Card Number** combination appears **for the 3rd time**, the system checks for unusual spending behavior using **TransactionAmountVariance_E6**.
4. If both conditions are met (**CountOfUsers = 3** and **TransactionAmountVariance_E6 = 1**), the transaction is flagged as fraudulent.
5. This helps detect cases where fraudsters use the same card and phone number for multiple suspicious transactions.
 
#### Example:
- A phone number (**+91 8904324835**) and card number (**2569 6352 4856 9713**) are used for a transaction the first time → **Not flagged**.
- The same phone and card combination is used again → **Still not flagged**.
- The combination appears a **third time**, and the transaction shows **high variance in spending behavior** → **Flagged as fraud**.
- If the same combination appears a **fourth time** but without spending anomalies, it is **not flagged**.
---
### 15. Enhanced Fraud Detection with Additional Parameters

### How It Works:
The system enhances fraud detection by incorporating additional behavioral and contextual checks alongside the existing Phone Number and Card Number tracking mechanism. The following parameters are evaluated to identify suspicious activity:

- **Device Variation**: Tracks if a different device is used for the transaction, including cases where the `DeviceInfo` has never appeared in prior transactions.
- **Region Discrepancy**: Compares the transaction region with the user's usual ordering region(s) to detect deviations.
- **Transaction Frequency**: Monitors for multiple transactions occurring in a short burst of time, exceeding the user's typical transaction rate.
- **Transaction Amount**: Flags transactions where the `TransactionAmt` exceeds the user's usual spending pattern.
- **Unusual Timing**: Identifies transactions performed at times outside the user's normal activity hours.

A fraudster attempting to execute multiple high-value transactions in a short time frame, from a different region and device, during unusual hours, triggers these checks. If the combination of Phone Number and Card Number reaches the third occurrence (CountOfUsers = 3) and any of these additional conditions are met, the system flags the transaction as fraudulent, even if `TransactionAmountVariance_E6` does not indicate variance.

### Example:
1. A phone number (+91 8904324835) and card number (2569 6352 4856 9713) are used for the first time from a known device and region → Not flagged.
2. The same combination is used again from a new device in a different region, with a high **TransactionAmt** in a short burst → Still not flagged (CountOfUsers = 2).
3. The combination appears a third time, from an unrecognized device, in an unusual region, with multiple high-amount transactions in quick succession during odd hours → Flagged as fraud.
4. A fourth transaction occurs with the same combination, but from a known device, region, and timing, with no anomalies → Not flagged.
---
### 16. Multiple Users with the Same Phone and Card Detection

### How It Works:
The system tracks how many times a unique combination of Phone Number and Card Number has been used. A CountOfUsers variable is maintained, which increments each time the same phone number and card number combination appears in transactions. Additional fraud detection criteria are evaluated when this combination is used repeatedly, focusing on unusual behavior patterns.

The system flags a transaction as fraudulent if:
- The same Phone Number and Card Number combination appears for the 3rd time (CountOfUsers = 3).
- Unusual spending behavior is detected via TransactionAmountVariance_E6 = 1.

Additionally, the following conditions enhance fraud detection:
- **Device Variation**: The transaction originates from a different device, or the DeviceInfo is new and has never appeared before.
- **Region Anomaly**: The transaction occurs in a region different from the user’s usual ordering region(s).
- **Transaction Amount**: The TransactionAmt exceeds the user’s typical spending amount.
- **Multiple New Merchants**: The UniqueMerchants count increases rapidly in a short time, with transactions involving multiple merchants never or rarely used by the user before.
- **Unusual Timing**: Transactions are executed at atypical times compared to the user’s normal activity.

If both core conditions (CountOfUsers = 3 and TransactionAmountVariance_E6 = 1) are met, alongside any of the additional indicators, the transaction is flagged as fraudulent. This approach identifies fraudsters making multiple high-value transactions from new devices, regions, and merchants at unusual times.

### Example:
1. A phone number (+91 8904324835) and card number (2569 6352 4856 9713) are used for a transaction from a known device and region → Not flagged.
2. The same combination is used again, with a slightly higher TransactionAmt but from the same region → Still not flagged.
3. The combination appears a third time, from a new device, in a different region, at an unusual time (e.g., 3 AM), with a high TransactionAmt and multiple new merchants (UniqueMerchants spikes) → Flagged as fraud.
4. The same combination appears a fourth time, from the same new device but with normal spending behavior and no new merchants → Not flagged.
---
### 17. Excessive Transaction Amount for Streaming Services Detection

### How It Works:
The system monitors transactions where the product category is "Services" and the merchant is a streaming service provider. In India, the highest streaming service subscription cost (e.g., Netflix) is approximately ₹8,000. Transactions exceeding this amount are considered suspicious, as an individual cannot reasonably purchase multiple subscriptions simultaneously under one transaction. If the transaction amount exceeds ₹8,000 for a streaming service merchant, it is flagged as fraudulent.

- A list of recognized streaming services is maintained for validation.
- The system checks the `Productcd` (product category), merchant name, and `TransactionAmt` (transaction amount).
- If `Productcd` is "Services," the merchant is in the streaming services list, and the `TransactionAmt` exceeds ₹8,000, the transaction is flagged as fraud.

### Streaming Services List:

streaming_services = ["Netflix", "Amazon Prime", "Hotstar", "Spotify", "Zee5", "JioSaavn", "ALT Balaji", "Sony LIV"]



---

These fraud detection patterns make the system smarter in identifying suspicious activities based on user behavior, spending patterns, location, and time of transactions. This ensures improved security and prevents fraudulent transactions effectively.
