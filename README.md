# Fraud Detection System

This project implements a fraud detection system using a real-time dataset created by us. The model is optimized using **Optuna** for hyperparameter tuning and utilizes **XGBoost** as the primary machine learning algorithm. The dataset is preprocessed, synthetic data is generated, and the final model is evaluated for fraud classification. Additionally, we have integrated a **FastAPI**-based connection for deploying the fraud detection system, which stores the data using **SQLite3**.

---

## Prerequisites

- Python 3.8+
- SQLite3
- Postman

---

## Features

- **Data Preprocessing**: Handles missing values, feature engineering, and encoding. 
- **Synthetic Data Generation**: Creates additional fraud cases using advanced data synthesis techniques. 
- **Hyperparameter Optimization**: Utilizes Optuna for efficient hyperparameter tuning. 
- **Model Training**: Uses XGBoost, a robust and high-performance gradient boosting algorithm. 
- **Evaluation Metrics**: Includes AUC-ROC, precision, recall, and F1-score for fraud detection assessment. 
- **FastAPI Backend**: Handles data processing, predictions, and database interactions.
- **SQLite3 Database**: Stores transaction data and model predictions.

---

## Installation

### Create and Activate Virtual Environment

#### Windows

```sh
python -m venv venv
venv\Scripts\activate
```

#### Ubuntu

```sh
python3 -m venv venv
source venv/bin/activate
```

### Install Required Dependencies

Run the following command to install all dependencies from `requirements.txt`:

```sh
pip install -r requirements.txt
```

### Run FastAPI Server

```sh
uvicorn app:app --host 127.0.0.1 --port 8000
```

---

## Workflow

The flow is divided into **two parts**: Model Creation and Prediction. 

### Model Creation

- The code is present in `Model.py` and must be executed along with the dataset named `synthetic_dataset.csv`. 
- This code will return two files:
  - `label_encoders.pkl`
  - `XGB_Model.pkl`
- Store these files in the same directory as `A2.py` before running predictions.

### Prediction

- This script will use the generated `.pkl` files and provide the root link of the host.
- Use **Postman** to import a new collection and upload `data.json`, which contains predefined API request templates.

---

## API Endpoints

### 1️⃣ Store Transaction

- **Endpoint**: `/store_transaction`
- **Method**: `POST`
- **Description**: Stores a new transaction and calculates engineered features.

### 2️⃣ Get All Transactions

- **Endpoint**: `/get_transactions`
- **Method**: `GET`
- **Description**: Retrieves all stored transactions.

### 3️⃣ Transaction Fraud Check

- **Endpoint**: `/transaction_fraud_check`
- **Method**: `POST`
- **Description**: Processes a transaction and returns a fraud prediction.

### 4️⃣ Predict Fraud for Specific Transaction

- **Endpoint**: `/predict_fraud/{transaction_id}`
- **Method**: `GET`
- **Description**: Predicts fraud for a specific transaction ID.

---

## Example Usage

### Postman Examples

#### **Store Transaction / Transaction Fraud Check**

**Endpoint**: `POST /transaction_fraud_check` or `POST /store_transaction`

**Request Body**:

```json
{
    "TransactionID": 22946,
    "TransactionAmt": 1000.00,
    "TransactionDT": "2024-02-20T10:30:00",
    "ProductCD": "H",
    "User_ID": 54321,
    "Merchant": "Example Store",
    "CardNumber": "4111111111111111",
    "BINNumber": "411111",
    "CardNetwork": "Visa",
    "CardTier": "Platinum",
    "CardType": "Credit",
    "PhoneNumbers": "+1234567890",
    "User_Region": "NY",
    "Order_Region": "NY",
    "Receiver_Region": "NY",
    "Distance": 0.0,
    "Sender_email": "sender@example.com",
    "Merchant_email": "merchant@example.com",
    "DeviceType": "Mobile",
    "DeviceInfo": "iPhone 12"
}
```

**Example Response**:

```json
{
    "status": "success",
    "transaction_stored": true,
    "transaction_id": 22946,
    "fraud_detection": {
        "is_fraud": false,
        "fraud_probability": 0.123
    },
    "transaction_details": {
        "amount": 1000.00,
        "datetime": "2024-02-20T10:30:00",
        "merchant": "Example Store",
        "region": "NY"
    }
}
```

---

## Notes

- Ensure the ML model file `model.pkl` is present in the current directory.
- The API uses an **SQLite** database, which will be created automatically.
- All timestamps should be in **ISO format** (`YYYY-MM-DDTHH:MM:SS`).
- The **Postman collection** has been included in the file `data.json`.

---

## Evaluation Metrics

- **AUC-ROC** 
- **Precision** 
- **Recall** 
- **F1-score** 

---

## Results

The optimized **XGBoost** model significantly improves fraud detection accuracy while maintaining a **low false positive rate**. Detailed results and visualizations can be found in the output logs.

---
