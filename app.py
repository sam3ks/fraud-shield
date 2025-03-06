import shap
import pickle
from geopy.distance import geodesic
import uvicorn
import nest_asyncio
from datetime import datetime
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Apply nest_asyncio to avoid event loop issues in Jupyter Notebook
nest_asyncio.apply()

# Initialize FastAPI app
app = FastAPI()

# Path to the pre-trained fraud detection model
MODEL_PATH = "src/models/xgb_fraud_model.pkl"

# Load the XGBoost model
try:
    with open(MODEL_PATH, "rb") as model_file:
        model = pickle.load(model_file)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except FileNotFoundError:
    print(f"❌ ERROR: Model file not found at {MODEL_PATH}. Ensure the file exists.")
    model = None

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Transaction Model with updated data types
class Transaction(Base):
    __tablename__ = "transactions"
    TransactionID = Column(Integer, primary_key=True, index=True, unique=True)
    TransactionAmt = Column(Float)
    TransactionDT = Column(String)
    ProductCD = Column(String)
    User_ID = Column(Integer)
    Merchant = Column(String)
    CardNumber = Column(String)
    BINNumber = Column(String)
    CardNetwork = Column(String)
    CardTier = Column(String)
    CardType = Column(String)
    PhoneNumbers = Column(String)
    User_Region = Column(String)
    Order_Region = Column(String)
    Receiver_Region = Column(String)
    Distance = Column(Float)
    Sender_email = Column(String)
    Merchant_email = Column(String)
    DeviceType = Column(String)
    DeviceInfo = Column(String)
    # E Series Features
    TransactionTimeSlot_E2 = Column(Integer)
    HourWithinSlot_E3 = Column(Integer)
    TransactionWeekday_E4 = Column(Integer)
    AvgTransactionInterval_E5 = Column(Float)
    TransactionAmountVariance_E6 = Column(Float)
    TransactionRatio_E7 = Column(Float)
    MedianTransactionAmount_E8 = Column(Float)
    AvgTransactionAmt_24Hrs_E9 = Column(Float)
    TransactionVelocity_E10 = Column(Integer)
    TimingAnomaly_E11 = Column(Integer)
    RegionAnomaly_E12 = Column(Integer)
    HourlyTransactionCount_E13 = Column(Integer)
    # D Series Features
    DaysSinceLastTransac_D2 = Column(Float)
    SameCardDaysDiff_D3 = Column(Float)
    SameAddressDaysDiff_D4 = Column(Float)
    SameReceiverEmailDaysDiff_D10 = Column(Float)
    SameDeviceTypeDaysDiff_D11 = Column(Float)
    # C Series Features
    TransactionCount_C1 = Column(Integer)
    UniqueMerchants_C4 = Column(Integer)
    SameBRegionCount_C5 = Column(Integer)
    SameDeviceCount_C6 = Column(Integer)
    UniqueBRegion_C11 = Column(Integer)
    # M Series Features
    DeviceMatching_M4 = Column(Integer)
    DeviceMismatch_M6 = Column(Integer)
    RegionMismatch_M8 = Column(Integer)
    TransactionConsistency_M9 = Column(Integer)
    # isFraud
    isFraud = Column(Integer)

# Create database tables
Base.metadata.create_all(bind=engine)

# Define request model
class TransactionIn(BaseModel):
    TransactionID: int
    TransactionAmt: float
    TransactionDT: str
    ProductCD: str
    User_ID: int
    Merchant: str
    CardNumber: str
    BINNumber: str
    CardNetwork: str
    CardTier: str
    CardType: str
    PhoneNumbers: str
    User_Region: str
    Order_Region: str
    Receiver_Region: str
    Sender_email: str
    Merchant_email: str
    DeviceType: str
    DeviceInfo: str

# Helper function for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bengaluru_regions = {
    'Koramangala': (12.9288, 77.6228), 'Jayanagar': (12.9333, 77.5833), 'Whitefield': (12.9764, 77.7513),
    'Indiranagar': (12.9701, 77.6402), 'Malleshwaram': (13.0034, 77.5723), 'Hebbal': (13.0312, 77.5924),
    'Hennur': (13.0245, 77.6247), 'Sarjapur Road': (12.9121, 77.6774), 'Bannerghatta Road': (12.8786, 77.5900),
    'Electronic City': (12.8543, 77.6780), 'Kalyan Nagar': (13.0272, 77.6463), 'BTM Layout': (12.9341, 77.5910),
    'Vijayanagar': (12.9557, 77.5500), 'Bellandur': (12.9336, 77.6543), 'Kengeri': (12.9202, 77.4856),
    'Yelahanka': (13.1008, 77.5963), 'Rajajinagar': (12.9917, 77.5568), 'Marathahalli': (12.9561, 77.7017),
    'HSR Layout': (12.9121, 77.6446), 'Nagawara': (13.0452, 77.6226), 'Devanahalli': (13.2485, 77.7132),
    'Attibele': (12.7762, 77.7672), 'Nelamangala': (13.0982, 77.3935), 'Hoskote': (13.0707, 77.7850),
    'Anekal': (12.7110, 77.6956)
}

def calculate_engineered_features(transaction_data: dict, db: Session):
    # Convert single transaction to DataFrame
    df = pd.DataFrame([transaction_data])
    # Convert TransactionDT to datetime if it's not already
    if isinstance(df['TransactionDT'].iloc[0], str):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'])

    # Get historical transactions for the user
    historical_transactions = pd.read_sql(f"SELECT * FROM transactions WHERE User_ID = {transaction_data['User_ID']}", db.bind)
    if not historical_transactions.empty:
        historical_transactions['TransactionDT'] = pd.to_datetime(historical_transactions['TransactionDT'])
        df = pd.concat([historical_transactions, df]).reset_index(drop=True)

    # Calculate Distance
    df['Distance'] = df.apply(lambda row: (
        np.round(np.random.uniform(0.1, 2), 2) if row["Order_Region"] == row["Receiver_Region"]
        else np.round(geodesic(bengaluru_regions.get(row["Order_Region"], (0, 0)),
                              bengaluru_regions.get(row["Receiver_Region"], (0, 0))).km, 2)
        if bengaluru_regions.get(row["Order_Region"]) and bengaluru_regions.get(row["Receiver_Region"]) else np.nan
    ), axis=1)

    # E features
    df['TransactionTimeSlot_E2'] = df['TransactionDT'].apply(lambda x: (
        0 if 10 <= x.hour < 14 else
        1 if 14 <= x.hour < 18 else
        2 if 18 <= x.hour < 22 else
        3 if x.hour >= 22 or x.hour < 2 else
        4 if 2 <= x.hour < 6 else 5
    ))
    df['HourWithinSlot_E3'] = df['TransactionDT'].apply(lambda x: (
        x.hour - 10 if 10 <= x.hour < 14 else
        x.hour - 14 if 14 <= x.hour < 18 else
        x.hour - 18 if 18 <= x.hour < 22 else
        (x.hour - 22) if x.hour >= 22 else (x.hour + 2) if x.hour < 2 else
        x.hour - 2 if 2 <= x.hour < 6 else
        x.hour - 6
    ))
    df['TransactionWeekday_E4'] = df['TransactionDT'].dt.weekday
    df['AvgTransactionInterval_E5'] = df.groupby('User_ID')['TransactionDT'].diff().dt.total_seconds() / 3600
    df['TransactionAmountVariance_E6'] = df.groupby('User_ID')['TransactionAmt'].transform(lambda x: x.std() if len(x) > 1 else 0)
    user_avg = df.groupby('User_ID')['TransactionAmt'].transform('mean')
    df['TransactionRatio_E7'] = df['TransactionAmt'] / user_avg.replace(0, np.nan)
    df['MedianTransactionAmount_E8'] = df.groupby('User_ID')['TransactionAmt'].transform('median')
    window_24h = df.groupby('User_ID', group_keys=False).apply(
        lambda x: x[x['TransactionDT'] >= x['TransactionDT'].max() - pd.Timedelta(hours=24)]).reset_index(drop=True)
    df['AvgTransactionAmt_24Hrs_E9'] = df['User_ID'].map(window_24h.groupby('User_ID')['TransactionAmt'].mean())
    df['TransactionVelocity_E10'] = window_24h.groupby('User_ID')['TransactionID'].transform('count')
    user_hour_freq = df.groupby(['User_ID', 'HourWithinSlot_E3']).size().reset_index(name='count')
    df['TimingAnomaly_E11'] = df.apply(
        lambda row: 1 if row['HourWithinSlot_E3'] not in user_hour_freq[user_hour_freq['User_ID'] == row['User_ID']]['HourWithinSlot_E3'].values else 0, axis=1
    )
    user_region_freq = df.groupby(['User_ID', 'Order_Region']).size().reset_index(name='count')
    df['RegionAnomaly_E12'] = df.apply(
        lambda row: 1 if row['Order_Region'] not in user_region_freq[user_region_freq['User_ID'] == row['User_ID']]['Order_Region'].values else 0, axis=1
    )
    df['HourlyTransactionCount_E13'] = df.groupby(['User_ID', 'HourWithinSlot_E3'])['TransactionID'].transform('count')
    df['DaysSinceLastTransac_D2'] = df.groupby('User_ID')['TransactionDT'].diff().dt.total_seconds() / 86400
    df['SameCardDaysDiff_D3'] = df.groupby('CardNumber')['TransactionDT'].diff().dt.total_seconds() / 86400
    df['SameAddressDaysDiff_D4'] = df.groupby(['User_Region', 'Order_Region'])['TransactionDT'].diff().dt.total_seconds() / 86400
    df['SameReceiverEmailDaysDiff_D10'] = df.groupby('Merchant_email')['TransactionDT'].diff().dt.total_seconds() / 86400
    df['SameDeviceTypeDaysDiff_D11'] = df.groupby('DeviceType')['TransactionDT'].diff().dt.total_seconds() / 86400
    # C series features
    df['TransactionCount_C1'] = df.groupby(['CardNumber', 'Order_Region'])['TransactionID'].transform('count')
    df['UniqueMerchants_C4'] = df.groupby('CardNumber')['Merchant'].transform('nunique')
    df['SameBRegionCount_C5'] = df.groupby(['User_ID', 'User_Region'])['TransactionID'].transform('count')
    df['SameDeviceCount_C6'] = df.groupby(['User_ID', 'DeviceType'])['TransactionID'].transform('count')
    df['UniqueBRegion_C11'] = df.groupby('User_ID')['User_Region'].transform('nunique')
    # M series features
    user_common_device = df.groupby('User_ID')['DeviceType'].agg(lambda x: x.mode().iloc[0] if not x.empty else None)
    df['DeviceMatching_M4'] = df.apply(
        lambda row: 1 if row['DeviceType'] == user_common_device.get(row['User_ID']) else 0, axis=1)
    df['PrevDevice'] = df.groupby('User_ID')['DeviceType'].shift(1)
    df['DeviceMismatch_M6'] = (df['DeviceType'] != df['PrevDevice']).astype(int)
    df['RegionMismatch_M8'] = (df['Order_Region'] != df['User_Region']).astype(int)
    df['TransactionConsistency_M9'] = df.apply(
        lambda row: sum([
            row['DeviceMatching_M4'],
            1 - row['DeviceMismatch_M6'],
            1 - row['RegionMismatch_M8'],
            1 if row['TransactionAmt'] <= row['MedianTransactionAmount_E8'] * 1.5 else 0
        ]), axis=1
    )

    # Replace NaN and inf with defaults
    df = df.replace([np.inf, -np.inf], np.nan).fillna(0)

    # Return features for the current transaction
    result = {
        'Distance': float(df.iloc[-1]['Distance']),
        'TransactionTimeSlot_E2': int(df.iloc[-1]['TransactionTimeSlot_E2']),
        'HourWithinSlot_E3': int(df.iloc[-1]['HourWithinSlot_E3']),
        'TransactionWeekday_E4': int(df.iloc[-1]['TransactionWeekday_E4']),
        'AvgTransactionInterval_E5': float(df.iloc[-1]['AvgTransactionInterval_E5']),
        'TransactionAmountVariance_E6': float(df.iloc[-1]['TransactionAmountVariance_E6']),
        'TransactionRatio_E7': float(df.iloc[-1]['TransactionRatio_E7']),
        'MedianTransactionAmount_E8': float(df.iloc[-1]['MedianTransactionAmount_E8']),
        'AvgTransactionAmt_24Hrs_E9': float(df.iloc[-1]['AvgTransactionAmt_24Hrs_E9']),
        'TransactionVelocity_E10': int(df.iloc[-1]['TransactionVelocity_E10']),
        'TimingAnomaly_E11': int(df.iloc[-1]['TimingAnomaly_E11']),
        'RegionAnomaly_E12': int(df.iloc[-1]['RegionAnomaly_E12']),
        'HourlyTransactionCount_E13': int(df.iloc[-1]['HourlyTransactionCount_E13']),
        'DaysSinceLastTransac_D2': float(df.iloc[-1]['DaysSinceLastTransac_D2']),
        'SameCardDaysDiff_D3': float(df.iloc[-1]['SameCardDaysDiff_D3']),
        'SameAddressDaysDiff_D4': float(df.iloc[-1]['SameAddressDaysDiff_D4']),
        'SameReceiverEmailDaysDiff_D10': float(df.iloc[-1]['SameReceiverEmailDaysDiff_D10']),
        'SameDeviceTypeDaysDiff_D11': float(df.iloc[-1]['SameDeviceTypeDaysDiff_D11']),
        'TransactionCount_C1': int(df.iloc[-1]['TransactionCount_C1']),
        'UniqueMerchants_C4': int(df.iloc[-1]['UniqueMerchants_C4']),
        'SameBRegionCount_C5': int(df.iloc[-1]['SameBRegionCount_C5']),
        'SameDeviceCount_C6': int(df.iloc[-1]['SameDeviceCount_C6']),
        'UniqueBRegion_C11': int(df.iloc[-1]['UniqueBRegion_C11']),
        'DeviceMatching_M4': int(df.iloc[-1]['DeviceMatching_M4']),
        'DeviceMismatch_M6': int(df.iloc[-1]['DeviceMismatch_M6']),
        'RegionMismatch_M8': int(df.iloc[-1]['RegionMismatch_M8']),
        'TransactionConsistency_M9': int(df.iloc[-1]['TransactionConsistency_M9'])
    }
    return result

@app.post("/transaction_fraud_check")
async def check_transaction_fraud(transaction: TransactionIn, db: Session = Depends(get_db)):
    try:
        # Step 1: Store transaction and get engineered features
        transaction_data = transaction.model_dump()
        engineered_features = calculate_engineered_features(transaction_data, db)
        transaction_data.update(engineered_features)

        # Store transaction
        db_transaction = Transaction(**transaction_data)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        # Step 2: Prepare data for prediction
        transaction_dict = {col.name: getattr(db_transaction, col.name) for col in Transaction.__table__.columns}
        transaction_df = pd.DataFrame([transaction_dict])

        # Load model
        with open(path, "rb") as model_file:
            model = pickle.load(model_file)

        # Get expected features
        expected_features = model.feature_names_in_
        column_mapping = {
            "Cardnumber": "CardNumber",
            "UserID": "User_ID",
            "BINnumber": "BINNumber",
            "Cardnetwork": "CardNetwork",
            "Cardtier": "CardTier",
            "Cardtype": "CardType",
            "Phonenumbers": "PhoneNumbers",
            "Userregion": "User_Region",
            "Orderregion": "Order_Region",
            "Receiverregion": "Receiver_Region",
            "Senderemail": "Sender_email",
            "Merchantemail": "Merchant_email",
            "Devicetype": "DeviceType",
            "Deviceinfo": "DeviceInfo",
        }
        transaction_df.rename(columns=column_mapping, inplace=True)

        # Handle categorical columns
        categorical_cols = transaction_df.select_dtypes(include=['object']).columns
        all_transactions = pd.read_sql("SELECT * FROM transactions", db.bind)

        # Replace None or 'None' with 'Unknown' and ensure all values are strings
        transaction_df[categorical_cols] = transaction_df[categorical_cols].fillna('Unknown').replace('None', 'Unknown').astype(str)
        all_transactions[categorical_cols] = all_transactions[categorical_cols].fillna('Unknown').replace('None', 'Unknown').astype(str)

        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            # Fit on all unique values from both historical and new data
            combined_values = pd.concat([all_transactions[col], transaction_df[col]]).unique()
            le.fit(combined_values)
            all_transactions[col] = le.transform(all_transactions[col])
            transaction_df[col] = le.transform(transaction_df[col])
            label_encoders[col] = le

        # Ensure all features exist
        for col in expected_features:
            if col not in transaction_df.columns:
                transaction_df[col] = 0

        transaction_df = transaction_df[expected_features]

        # Replace NaN/inf in DataFrame before prediction
        transaction_df = transaction_df.replace([np.inf, -np.inf], np.nan).fillna(0)

        # Make prediction
        prediction = model.predict(transaction_df)[0]
        prediction_proba = model.predict_proba(transaction_df)[0]

        # Handle different output formats of predict_proba
        fraud_probability = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba

        # Apply fraud threshold
        prediction = 1.0 if fraud_probability > 0.01 else 0.0

        # Update the isFraud value in the database
        db_transaction.isFraud = int(prediction)
        db.commit()

        if prediction == 1.0:  # Only explain fraud transactions
            # Initialize SHAP explainer
            explainer = shap.Explainer(model)
            shap_values = explainer(transaction_df)

            # Extract SHAP values for the first instance
            shap_values_instance = shap_values[0].values
            feature_names = transaction_df.columns

            # Create a DataFrame with feature names and their corresponding SHAP values
            shap_df = pd.DataFrame({
                'Feature': feature_names,
                'SHAP Value': shap_values_instance
            })

            # Calculate absolute SHAP values
            shap_df['Absolute SHAP Value'] = shap_df['SHAP Value'].abs()
            total_abs_shap = shap_df['Absolute SHAP Value'].sum()
            shap_df['Percentage Contribution'] = (shap_df['Absolute SHAP Value'] / total_abs_shap) * 100
            shap_df['Percentage Contribution'] = shap_df['Percentage Contribution'].round(2)

            shap_df = shap_df.sort_values(by='Percentage Contribution', ascending=False)
            top_features = shap_df[['Feature', 'Percentage Contribution']].to_dict(orient="records")

            response = {
                "status": "success",
                "transaction_stored": True,
                "transaction_id": transaction.TransactionID,
                "Distance": engineered_features["Distance"],
                "fraud_detection": {
                    "is_fraud": bool(prediction),
                    "fraud_probability": round(float(fraud_probability), 5),
                },
                "transaction_details": {
                    "Transaction": transaction.TransactionID,
                    "Amount": transaction.TransactionAmt,
                    "Datetime": transaction.TransactionDT,
                    "Merchant": transaction.Merchant,
                    "Region": transaction.Order_Region
                },
                "Top_features": top_features
            }
        else:
            response = {
                "status": "success",
                "transaction_id": transaction.TransactionID,
                "is_fraud": False,
                "message": "Transaction is not fraudulent, no SHAP analysis needed."
            }

        # Ensure all floats in response are JSON-compliant
        def clean_floats(obj):
            if isinstance(obj, dict):
                return {k: clean_floats(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_floats(item) for item in obj]
            elif isinstance(obj, float):
                return 0.0 if pd.isna(obj) or not np.isfinite(obj) else obj
            return obj

        return clean_floats(response)

    except Exception as e:
        db.rollback()  # Rollback transaction if error occurs
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
