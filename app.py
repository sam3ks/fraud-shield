import os
import sys
import pickle
import subprocess
import streamlit as st
import plotly.graph_objects as go
from fastapi.responses import FileResponse
def install_and_run():
    # Function to install missing packages
    def install_package(package_name):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}")  
    required_packages = [
        "xgboost", "uvicorn", "nest_asyncio", "fastapi", "pydantic", "sqlalchemy", "geopy","scikit-learn"]
    for package in required_packages:
        install_package(package)
import xgboost
import uvicorn
import nest_asyncio
import shap
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.preprocessing import LabelEncoder
 
nest_asyncio.apply()
app = FastAPI()
path="src/models/xgb_fraud_model.pkl"
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 
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
    DaysSinceLastTransac_D2 = Column(Float)
    SameCardDaysDiff_D3 = Column(Float)
    SameAddressDaysDiff_D4 = Column(Float)
    SameReceiverEmailDaysDiff_D10 = Column(Float)
    SameDeviceTypeDaysDiff_D11 = Column(Float)
    TransactionCount_C1 = Column(Integer)
    UniqueMerchants_C4 = Column(Integer)
    SameBRegionCount_C5 = Column(Integer)
    SameDeviceCount_C6 = Column(Integer)
    UniqueBRegion_C11 = Column(Integer)
    DeviceMatching_M4 = Column(Integer)
    DeviceMismatch_M6 = Column(Integer)
    RegionMismatch_M8 = Column(Integer)
    TransactionConsistency_M9 = Column(Integer)
    EmailFraudFlag = Column(Integer)
    AmountAnomaly= Column(Integer)
    EmailDomainChanges_30D = Column(Integer, default=0)
    LateNightPattern = Column(Integer)
    UnauthorizedTransactionFlag = Column(Integer)
    InActivity_gap_E14=Column(Integer)
    HighAmount_PostInactivity_E15=Column(Integer)
    ProductCD_Amount_Anomaly=Column(Integer)
    Delivery_Regions_Anomaly=Column(Integer)
    isFraud = Column(Integer)
 
Base.metadata.create_all(bind=engine)
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
 
@app.get("/download-db")
def download_db():
    return FileResponse("test.db", media_type="application/octet-stream", filename="test.db")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
bengaluru_regions = {
        'Bagalkot': (16.1805, 75.6961), 'Ballari': (15.1394, 76.9214), 'Belagavi': (15.8497, 74.4977),
        'Bangalore': (12.9716, 77.5946), 'Mumbai': (17.9106, 77.5199), 'Delhi': (11.9236, 76.9456),
        'Chikkaballapur': (13.4353, 77.7315), 'Chikkamagaluru': (13.3161, 75.7720), 'Chitradurga': (14.2296, 76.3985),
        'Dakshina Kannada': (12.8703, 74.8806), 'Davanagere': (14.4644, 75.9212), 'Dharwad': (15.4589, 75.0078),
        'Gadag': (15.4298, 75.6341), 'Hassan': (13.0057, 76.1023), 'Haveri': (14.7957, 75.3998),
        'Kalaburagi': (17.3297, 76.8376), 'Kodagu': (12.4218, 75.7400), 'Kolar': (13.1367, 78.1292),
        'Koppal': (15.3459, 76.1548), 'Mandya': (12.5223, 76.8954), 'Mysuru': (12.2958, 76.6394),
        'Raichur': (16.2076, 77.3561), 'Ramanagara': (12.7111, 77.2800), 'Shivamogga': (13.9299, 75.5681),
        'Tumakuru': (13.3409, 77.1010), 'Udupi': (13.3415, 74.7401), 'Uttara Kannada': (14.9980, 74.5070),
        'Vijayapura': (16.8302, 75.7100), 'Yadgir': (16.7625, 77.1376) }
 
# def calculate_engineered_features(transaction_data: dict, db: Session):
#     df = pd.DataFrame([transaction_data])
#     if isinstance(df['TransactionDT'].iloc[0], str):
#         df['TransactionDT'] = pd.to_datetime(df['TransactionDT'])
#     historical_transactions = pd.read_sql(f"SELECT * FROM transactions WHERE User_ID = {transaction_data['User_ID']}", db.bind)

#     if not historical_transactions.empty:
#         historical_transactions['TransactionDT'] = pd.to_datetime(historical_transactions['TransactionDT'])
#         combined_df = pd.concat([historical_transactions, df], ignore_index=True)
#         combined_df = combined_df.sort_values(by=['User_ID', 'TransactionDT']).reset_index(drop=True)
#         df = combined_df
def calculate_engineered_features(transaction_data: dict, db: Session):
    df = pd.DataFrame([transaction_data])
    if isinstance(df['TransactionDT'].iloc[0], str):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'])
    historical_transactions = pd.read_sql(f"SELECT * FROM transactions WHERE User_ID = {transaction_data['User_ID']}", db.bind)
    if not historical_transactions.empty:
        historical_transactions['TransactionDT'] = pd.to_datetime(historical_transactions['TransactionDT'])
        common_cols = historical_transactions.columns.intersection(df.columns)
        historical_transactions = historical_transactions[common_cols]
        combined_df = pd.concat([historical_transactions, df], ignore_index=True)
        combined_df = combined_df.sort_values(by=['User_ID', 'TransactionDT']).reset_index(drop=True)
        
        df = combined_df
    
    
    #Distance
    def calculate_distance(db, transaction_data, df, bengaluru_regions):
        last_transaction = db.execute(
            text("SELECT Order_Region FROM transactions WHERE User_ID = :user_id ORDER BY TransactionDT DESC LIMIT 1"),
            {"user_id": transaction_data['User_ID']}
        ).fetchone()
        
        last_order_region = last_transaction[0] if last_transaction else None
        
        if last_order_region and last_order_region in bengaluru_regions:
            df['Distance'] = df['Order_Region'].apply(lambda region: (
                0 if region == last_order_region else  # If same, return 0
                np.round(geodesic(bengaluru_regions.get(last_order_region), bengaluru_regions.get(region)).km, 2)
                if region in bengaluru_regions else 0  # Default distance if region not in database
            ))
        else:
            df['Distance'] = 0  # Default for new users
        
        return df
 
    #E2        
    def assign_time_slot(transaction_dt):
        hour = transaction_dt.hour
        if 10 <= hour < 14:
            return 0
        elif 14 <= hour < 18:
            return 1
        elif 18 <= hour < 22:
            return 2
        elif hour >= 22 or hour < 2:
            return 3
        elif 2 <= hour < 6:
            return 4
        elif 6 <= hour < 10:
            return 5
        else:
            return 29
    df['TransactionTimeSlot_E2'] = df['TransactionDT'].apply(assign_time_slot)
 
    #E3
    def assign_hour_within_slot(transaction_dt):
        hour = transaction_dt.hour
        if 10 <= hour < 14:
            return hour - 10
        elif 14 <= hour < 18:
            return hour - 14
        elif 18 <= hour < 22:
            return hour - 18
        elif hour >= 22:
            return hour - 22
        elif hour < 2:
            return hour + 2
        elif 2 <= hour < 6:
            return hour - 2
        else:
            return hour - 6
    df['HourWithinSlot_E3'] = df['TransactionDT'].apply(assign_hour_within_slot)
 
    #E4
    df['TransactionWeekday_E4'] = df['TransactionDT'].dt.weekday
 
    #E5
    def calculate_transaction_intervals(df):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'], errors='coerce')
        df = df.sort_values(by=['User_ID', 'TransactionDT'])
        df['TimeDiff'] = df.groupby('User_ID')['TransactionDT'].diff()
        df['TimeDiff'] = df['TimeDiff'].dt.total_seconds() / 3600  
        df['TimeDiff'] = df['TimeDiff'].fillna(0)
        df['AvgTimeDiff_E5'] = df.groupby('User_ID')['TimeDiff'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean())
        df['PrevAvgTimeDiff_E5'] = df.groupby('User_ID')['AvgTimeDiff_E5'].transform(lambda x: x.shift(1))
        df['PrevAvgTimeDiff_E5'] = df['PrevAvgTimeDiff_E5'].fillna(0)
        df['AvgTransactionInterval_E5'] = df.apply(
            lambda row: 1 if row['PrevAvgTimeDiff_E5'] > 0 and
                            row['AvgTimeDiff_E5'] < max(0.5 * row['PrevAvgTimeDiff_E5'], 0.1)
                            else 0, axis=1)
        return df
    
 
    # E6 - TransactionAmountVariance_E6
    def detect_transaction_variance(df):
        df['RollingMean_TransactionAmt'] = df.groupby('User_ID')['TransactionAmt'].transform(lambda x: x.rolling(window=6, min_periods=1).mean())
        df['RollingMean_TransactionAmt'] = df['RollingMean_TransactionAmt'].replace(0, np.nan)
        df['TransactionAmountVariance_E6'] = df.apply(lambda row: 1 if pd.notnull(row['RollingMean_TransactionAmt']) and
                        (row['TransactionAmt'] > 3 * row['RollingMean_TransactionAmt'] or
                            row['TransactionAmt'] < row['RollingMean_TransactionAmt'] / 3) else 0, axis=1)
        return df
    df = detect_transaction_variance(df)
    
 
    # E7 - TransactionRatio_E7
    def calculate_transaction_ratio(df):
        df['UserMeanTransaction'] = df.groupby('User_ID')['TransactionAmt'].transform('mean')
        df['UserMeanTransaction'] = df['UserMeanTransaction'].replace(0, np.nan)
        def compute_ratio(row):
            if pd.notnull(row['UserMeanTransaction']):
                return row['TransactionAmt'] / row['UserMeanTransaction']
            return 0
        df['TransactionRatio_E7'] = df.apply(compute_ratio, axis=1)
        df['TransactionRatio_E7'] = ((df['TransactionRatio_E7'] > 2.5)|(df['TransactionRatio_E7'] < 2.5)).astype(int)
        df = df.drop(columns=['UserMeanTransaction'])
        return df
    
    # E8 - MedianTransactionAmount_E8
    def detect_anomalous_transactions(df):
        df['RollingMedian_TransactionAmt'] = df.groupby('User_ID')['TransactionAmt'].transform(lambda x: x.rolling(window=6, min_periods=1).median())
        df['RollingMedian_TransactionAmt'] = df['RollingMedian_TransactionAmt'].replace(0, np.nan)
        df['MedianTransactionAmount_E8'] = df.apply(
            lambda row: 1 if pd.notnull(row['RollingMedian_TransactionAmt']) and (row['TransactionAmt'] > 3 * row['RollingMedian_TransactionAmt'] or
                            row['TransactionAmt'] < row['RollingMedian_TransactionAmt'] / 3)
                        else 0,axis=1)
        df = df.drop(columns=['RollingMedian_TransactionAmt'])
        return df
    
 
    # E9 - AvgTransactionAmt_24Hrs_E9
    def detect_unusual_transaction_amounts(df):
        df = df.sort_values(by=['User_ID', 'TransactionDT']).reset_index(drop=True)
        df['AvgTransactionAmt_6Txns'] = df.groupby('User_ID')['TransactionAmt'].transform(lambda x: x.rolling(window=6, min_periods=1).mean())
        df['PrevAvgTransactionAmt_6Txns'] = df.groupby('User_ID')['AvgTransactionAmt_6Txns'].transform(lambda x: x.shift(1))
        df['AvgTransactionAmt_24Hrs_E9'] = df.apply(
            lambda row: 1 if pd.notnull(row['PrevAvgTransactionAmt_6Txns']) and row['PrevAvgTransactionAmt_6Txns'] > 0 and
                        ((row['AvgTransactionAmt_6Txns'] >= 2 * row['PrevAvgTransactionAmt_6Txns']) or
                            (row['AvgTransactionAmt_6Txns'] <= 0.5 * row['PrevAvgTransactionAmt_6Txns']))
                        else 0,axis=1)
        df = df.drop(columns=['AvgTransactionAmt_6Txns', 'PrevAvgTransactionAmt_6Txns'])
        return df
    
 
    # E10
    def calculate_transaction_velocity(df):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'], errors='coerce')
        df = df.sort_values(by=['User_ID', 'TransactionDT'])
        df['TransactionVelocity'] = df.apply(lambda row: (
            df[(df['User_ID'] == row['User_ID']) &
            (df['TransactionDT'] > row['TransactionDT'] - pd.Timedelta(hours=1)) &
            (df['TransactionDT'] <= row['TransactionDT'])].shape[0]), axis=1)
        df['TransactionVelocityE'] = (df['TransactionVelocity'] >= 6).astype(int)
        df['TransactionVelocity_E10'] = ((df['TransactionVelocityE'] == 1) &
                            (df['TransactionAmountVariance_E6'] == 1)).astype(int)
        return df
    df = calculate_transaction_velocity(df)
 
    # E11
    def timing_anomaly(group):
        if len(group) <= 1:
            return pd.Series([0] * len(group), index=group.index)
        hour_counts = group['TransactionTimeSlot_E2'].value_counts(normalize=True)
        threshold = 0.21
        anomaly_flags = []
        for idx, row in group.iterrows():
            current_slot = row['TransactionTimeSlot_E2']
            is_rare = hour_counts.get(current_slot, 0) < threshold
            prev_slot = current_slot - 1
            next_slot = current_slot + 1
            anomaly_flags.append(1 if is_rare or not(prev_slot or next_slot) else 0)
        return pd.Series(anomaly_flags, index=group.index)
    df['TimingAnomaly_E11'] = 0
    for user_id, group in df.groupby('User_ID'):
        df.loc[group.index, 'TimingAnomaly_E11'] = timing_anomaly(group)
    df['TimingAnomaly_E11'] = df['TimingAnomaly_E11'].astype(int)
    df['TimingAnomaly_E11'] = ((df['TimingAnomaly_E11'] == 1) & (df['TransactionAmountVariance_E6'] == 1)).astype(int)
 
    
    #E12
    def detect_region_anomalies(df):
        speed_threshold = 50
        required_cols = {'User_ID', 'TransactionDT', 'Order_Region', 'TimingAnomaly_E11', 'EmailFraudFlag', 'TransactionConsistency_M9'}
        if not required_cols.issubset(df.columns):
            # Add missing columns with default values
            for col in required_cols - set(df.columns):
                df[col] = 0
        df = df.copy()
        df['Coordinates'] = df['Order_Region'].map(bengaluru_regions)
        
        def region_anomaly(user_group):
            if len(user_group) <= 1:
                return pd.Series(0, index=user_group.index, name='RegionAnomaly_E12')
            
            # Sort and compute intermediate values without modifying the DataFrame
            sorted_group = user_group.sort_values(by='TransactionDT')
            coords = sorted_group['Coordinates']
            times = sorted_group['TransactionDT']
            prev_coords = coords.shift(1)
            prev_times = times.shift(1)
            
            distances = [
                geodesic(curr, prev).km if pd.notna(curr) and pd.notna(prev) else 0
                for curr, prev in zip(coords, prev_coords)
            ]
            time_diffs = (times - prev_times).dt.total_seconds() / 3600
            speeds = [
                dist / time if pd.notna(time) and time > 0 else 0
                for dist, time in zip(distances, time_diffs)
            ]
            
            # Return a single Series
            return pd.Series([int(speed > speed_threshold) for speed in speeds], 
                            index=sorted_group.index, 
                            name='RegionAnomaly_E12')
        
        # Use agg instead of apply to ensure Series output, or use apply with explicit reindex
        anomaly_series = df.groupby('User_ID', group_keys=False).apply(region_anomaly)
        if isinstance(anomaly_series, pd.DataFrame):
            # If apply returns a DataFrame, extract the single column
            anomaly_series = anomaly_series.iloc[:, 0]
        df['RegionAnomaly_E12'] = anomaly_series.reindex(df.index, fill_value=0).astype(int)
        
        # Apply additional conditions
        df['RegionAnomaly_E12'] = ((df['RegionAnomaly_E12'] == 1) &
                                ((df['TimingAnomaly_E11'] == 1) |
                                    (df['EmailFraudFlag'] == 1) |
                                    (df['TransactionConsistency_M9'] == 0))).astype(int)
        return df
 
 
    def detect_card_fraud(df):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'])
        card_user_count = df.groupby('CardNumber')['User_ID'].nunique()
        fraudulent_cards = set(card_user_count[card_user_count > 1].index)
        df['CardFraudFlag'] = df['CardNumber'].apply(lambda x: 1 if x in fraudulent_cards else 0)
        
        df_fraud_cards = df[df['CardNumber'].isin(fraudulent_cards)].copy()
        df_fraud_cards['TransactionHour'] = df_fraud_cards['TransactionDT'].dt.floor('H')
        card_hourly_count = df_fraud_cards.groupby(['CardNumber', 'TransactionHour']).size()
        high_freq_cards = set(card_hourly_count[card_hourly_count >= 5].index.get_level_values(0))
        df['HourlyTransactionCount_E13'] = df['CardNumber'].apply(lambda x: 1 if x in high_freq_cards else 0)
        return df
    
 
    #D columns
    
    def calculate_days_diff(group, column_name):
        group = group.sort_values(by='TransactionDT')
        group['TimeDiff'] = group['TransactionDT'].diff()
        group[column_name] = group['TimeDiff'].dt.total_seconds().div(86400).fillna(0)
        return group.drop(columns=['TimeDiff'])

    # Apply it
    df = df.groupby('User_ID').apply(calculate_days_diff, 'DaysSinceLastTransac_D2').reset_index(drop=True)
 
    #C1
    def calculate_transaction_count_c1(df):
        return df.groupby(['CardNumber', 'Order_Region'])['TransactionID'].transform('count').fillna(1).astype(int)
    
 
    #C4
    def calculate_unique_merchants_c4(df):
        return df.groupby('CardNumber')['Merchant'].transform('nunique').fillna(1).astype(int)
   
    #C5
    def calculate_same_region_count_c5(df):
        return df.groupby(['User_ID', 'User_Region'])['TransactionID'].transform('count').fillna(1).astype(int)
    
    #C6
    def calculate_same_device_count_c6(df):
        return df.groupby(['User_ID', 'DeviceType'])['TransactionID'].transform('count').fillna(1).astype(int)
    
    #C11
    def calculate_unique_region_c11(df):
        return df.groupby('User_ID')['User_Region'].transform('nunique').fillna(1).astype(int)
    
 
    def M_features(df):
        df = df.sort_values(by=['User_ID', 'TransactionDT'])
        user_common_device_dict = df.groupby('User_ID')['DeviceType'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None).to_dict()
        df['DeviceMatching_M4'] = df.apply(
            lambda row: 1 if user_common_device_dict.get(row['User_ID']) == row['DeviceType'] else 0,
            axis=1
        )
        df['PrevDevice'] = df.groupby('User_ID')['DeviceType'].shift(1)
        df['DeviceMismatch_M6'] = df.apply(
            lambda row: 1 if pd.notna(row['PrevDevice']) and row['DeviceType'] != row['PrevDevice'] else 0,
            axis=1
        )
        df.drop(columns=['PrevDevice'], inplace=True)
        df['RegionMismatch_M8'] = df.apply(
            lambda row: 1 if pd.notna(row['Order_Region']) and pd.notna(row['User_Region']) and row['Order_Region'] != row['User_Region'] else 0,
            axis=1
        )
        df['TransactionConsistency_M9'] = (
            df['DeviceMatching_M4'] +
            (1 - df['DeviceMismatch_M6']) +
            (1 - df['RegionMismatch_M8']) +
            df.apply(
                lambda row: 1 if pd.notna(row['TransactionAmt']) and pd.notna(row['MedianTransactionAmount_E8']) and row['TransactionAmt'] <= row['MedianTransactionAmount_E8'] * 1.5 else 0,
                axis=1
            )
        ).astype(int)
        return df
    
    # EmailFraudFlag
    def flag_email_fraud(df):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'], errors='coerce')
        df = df.sort_values(by=['User_ID', 'TransactionDT'])
        df['EmailFraudFlag'] = 0
        user_email_history = {}
        for idx, row in df.iterrows():
            user_id = row['User_ID']
            email = row['Sender_email']
            email_domain = email.split('@')[-1]
            transaction_time = row['TransactionDT']
            if user_id not in user_email_history:
                user_email_history[user_id] = []
            past_transactions = user_email_history[user_id]
            is_new_email = email not in [t[0] for t in past_transactions]
            is_new_domain = email_domain not in [t[1] for t in past_transactions]
            if len(past_transactions) >= 1:
                last_transaction_time = past_transactions[-1][2]
                within_one_hour = (transaction_time - last_transaction_time) <= pd.Timedelta(hours=1)
                if within_one_hour and (is_new_email or is_new_domain):
                    if row['TransactionAmountVariance_E6'] == 1 or row['TransactionVelocity_E10'] == 1:
                        df.at[idx, 'EmailFraudFlag'] = 1
            user_email_history[user_id].append((email, email_domain, transaction_time))
        return df
    df = flag_email_fraud(df)
    
 
   #Amount Anomaly
    def add_anomaly_features(df):  
        anomaly_cols = ['AvgTransactionAmt_24Hrs_E9', 'TransactionRatio_E7','MedianTransactionAmount_E8', 'AvgTransactionInterval_E5','TransactionVelocity_E10','TimingAnomaly_E11', 'RegionAnomaly_E12']
        for col in anomaly_cols:
            if col not in df.columns:
                df[col] = 0  
        df['AnomalyCount'] = df[anomaly_cols].sum(axis=1)
        df['AmountAnomaly'] = (
            ((df['AnomalyCount'] >= 3) & (df['TransactionAmountVariance_E6'] == 1))).astype(int)
        df.drop(columns=['AnomalyCount'], inplace=True)
        return df
    
 
    # Suhas's Email Domain code 4 email domain in 1 month
 
    def get_email_domain(email):
        try:
            return email.split('@')[1].lower() if email and '@' in email else ''
        except (IndexError, AttributeError):
            return ''
    
    df['EmailDomain'] = df['Sender_email'].apply(get_email_domain)

    def calculate_email_domain_changes(df):
        domain_flags = {}
        for idx, row in df.iterrows():
            user_id = row['User_ID']
            current_time = row['TransactionDT']
            time_cutoff = current_time - pd.Timedelta(days=30)
            user_transactions = df[
                (df['User_ID'] == user_id) &
                (df['TransactionDT'] <= current_time) &  # Include current transaction
                (df['TransactionDT'] > time_cutoff)
            ]
            unique_domains = user_transactions['EmailDomain'].dropna().nunique()
            domain_flags[idx] = 1 if unique_domains > 4 else 0
        return pd.Series(domain_flags).reindex(df.index).fillna(0).astype(int)
    
 
    # Pattern 11
    def detect_late_night_testing(df):
        df['LateNightPattern'] = df.apply(lambda row: 1 if row['TransactionTimeSlot_E2'] in [3, 4] and row['TransactionAmountVariance_E6'] == 1 else 0, axis=1)
        return df
 
    # Pattern 12
    def detect_unauthorized_transactions(df):
        df['UnauthorizedTransactionFlag'] = df.apply(lambda row: 1 if row['TransactionVelocity'] == 1 and row['DeviceMismatch_M6'] == 1 and row['RegionMismatch_M8'] == 1 else 0, axis=1)
        return df
    
    # Pattern 13
    def detect_delivery_regions_anomaly(df):
        required_cols = {'User_ID', 'TransactionDT', 'Receiver_Region'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

        df = df.copy()

        # Convert TransactionDT to datetime and drop NaT values
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'], errors='coerce')
        df = df.dropna(subset=['TransactionDT'])  # Drop rows with NaT

        # Sort by User_ID and TransactionDT
        df = df.sort_values(by=['User_ID', 'TransactionDT'])

        # Convert Receiver_Region to category codes, handling NaNs
        df['Receiver_Region'] = df['Receiver_Region'].fillna("Unknown")  # Replace NaN with "Unknown"
        df['Receiver_Region_Code'] = df['Receiver_Region'].astype('category').cat.codes

        def check_anomaly(user_group):
            if len(user_group) == 0:
                return pd.Series([], index=user_group.index, dtype='Int64', name='Delivery_Regions_Anomaly')

            # Sort within group
            sorted_group = user_group.sort_values('TransactionDT')

            # Rolling window of 1 hour
            rolling_result = (
                sorted_group.set_index('TransactionDT')
                .rolling('1h', min_periods=1)['Receiver_Region_Code']
                .apply(lambda x: x.nunique(), raw=False)
            )

            # Ensure proper type conversion, replacing NaN with 0
            return (rolling_result > 3).astype('Int64').fillna(0)

        # Apply group-wise function
        anomaly_series = df.groupby('User_ID', group_keys=False).apply(check_anomaly)

        # Handle cases where apply() returns a DataFrame instead of Series
        if isinstance(anomaly_series, pd.DataFrame):
            anomaly_series = anomaly_series.iloc[:, 0]

        # Align results with the original DataFrame
        df['Delivery_Regions_Anomaly'] = anomaly_series.reindex(df.index, fill_value=0).astype('Int64')

        return df


 
    #Pattern 17
    def assign_productcd_amount(df):
        services_list = ["Netflix", "Amazon Prime", "Hotstar", "Spotify", "Zee5", "JioSaavn","ALT Balaji", "Sony LIV", "Audible"]
        df["ProductCD_Amount_Anomaly"] = df.apply(lambda row: 1 if row["ProductCD"] in services_list and row["TransactionAmt"] > 8000 else 0, axis=1)
        return df
    
    def detect_inactivity_and_large_transactions(df):
        df['TransactionDT'] = pd.to_datetime(df['TransactionDT'], errors='coerce')
        df = df.sort_values(by=['User_ID', 'TransactionDT'])
        df['DaysSinceLastTransac_D2'] = df.groupby('User_ID')['TransactionDT'].diff().dt.total_seconds() / (24 * 3600)
        user_avg_transaction = df.groupby('User_ID')['TransactionAmt'].transform('mean')
        df['InActivity_gap_E14'] = ((df['DaysSinceLastTransac_D2'] > 90) |
                                    (df['DaysSinceLastTransac_D2'].isna())).astype(int)
        df['HighAmount_PostInactivity_E15'] = ((df['InActivity_gap_E14'] == 1) &(df['TransactionAmt'] > 3 * user_avg_transaction)).astype(int)
        return df
 
    df = calculate_distance(db, transaction_data, df, bengaluru_regions)    
    df = calculate_transaction_intervals(df)
    df = calculate_transaction_ratio(df)
    df = detect_anomalous_transactions(df)
    df = detect_unusual_transaction_amounts(df)
    # df = calculate_transaction_velocity(df)
    df = M_features(df)
    df = detect_region_anomalies(df)
    df = detect_card_fraud(df)
    df = df.groupby('User_ID').apply(calculate_days_diff, 'DaysSinceLastTransac_D2').reset_index(drop=True)
    df = df.groupby('CardNumber').apply(calculate_days_diff, 'SameCardDaysDiff_D3').reset_index(drop=True)
    df = df.groupby(['User_Region', 'Order_Region']).apply(calculate_days_diff, 'SameAddressDaysDiff_D4').reset_index(drop=True)
    df = df.groupby('Merchant_email').apply(calculate_days_diff, 'SameReceiverEmailDaysDiff_D10').reset_index(drop=True)
    df = df.groupby('DeviceType').apply(calculate_days_diff, 'SameDeviceTypeDaysDiff_D11').reset_index(drop=True)
    df['TransactionCount_C1'] = calculate_transaction_count_c1(df)
    df['UniqueMerchants_C4'] = calculate_unique_merchants_c4(df)
    df['SameBRegionCount_C5'] = calculate_same_region_count_c5(df)
    df['SameDeviceCount_C6'] = calculate_same_device_count_c6(df)
    df['UniqueBRegion_C11'] = calculate_unique_region_c11(df)
    df = add_anomaly_features(df)
    df['EmailDomainChanges_30D'] = calculate_email_domain_changes(df)
    df = detect_late_night_testing(df)
    df = detect_unauthorized_transactions(df)
    df = detect_delivery_regions_anomaly(df)
    df = assign_productcd_amount(df)
    df = detect_inactivity_and_large_transactions(df)
 
    columns_to_round = ['DaysSinceLastTransac_D2','SameCardDaysDiff_D3','SameAddressDaysDiff_D4','SameReceiverEmailDaysDiff_D10','SameDeviceTypeDaysDiff_D11']
    df[columns_to_round] = df[columns_to_round].round(2)
 
    #SYNTHETIC IDENTITY FRAUD DETECTION
    # Pattern 1: Email Fraud Flag
    fraud_score_email = df['EmailFraudFlag'].iloc[-1] * 25
 
    # Pattern 2: Transaction Velocity
    fraud_score_velocity = (1 if df['TransactionVelocity_E10'].iloc[-1] > 5 else 0) * 20
 
    # Pattern 3: Region and Device Mismatch/Anomaly
    fraud_score_region_device = (
    df['RegionAnomaly_E12'].iloc[-1] * 15 +
    df['DeviceMismatch_M6'].iloc[-1] * 5 +
    df['RegionMismatch_M8'].iloc[-1] * 5)
 
    # Pattern 4: Transaction Amount Variance and Timing Anomaly
    fraud_score_amount_timing = (
    (1 if df['TransactionAmountVariance_E6'].iloc[-1] > 10000 else 0) * 10 +
    df['TimingAnomaly_E11'].iloc[-1] * 20)
 
    # Pattern 5: Device Matching and Region Mismatch Conditional
    fraud_score_device_region_conditional = (
    (10 if df['TransactionRatio_E7'].iloc[-1] == 1 and df['RegionMismatch_M8'].iloc[-1] == 1 else 0) +
    (5 if df['DeviceMatching_M4'].iloc[-1] == 0 else 0)
    )
 
    # Pattern 6: Device Mismatch and Timing Conditional, and other conditionals
    fraud_score_device_timing_other_conditionals = (
    (15 if df['DeviceMismatch_M6'].iloc[-1] == 1 and df['TimingAnomaly_E11'].iloc[-1] == 1 else 0) +
    (10 if df['HourlyTransactionCount_E13'].iloc[-1] > 3 else 0) +
    (15 if float(df['SameCardDaysDiff_D3'].iloc[-1]) < 0.01 else 0)
    )
    
    fraud_score = (
        fraud_score_email +
        fraud_score_velocity +
        fraud_score_region_device +
        fraud_score_amount_timing +
        fraud_score_device_region_conditional +
        fraud_score_device_timing_other_conditionals
    )
 
    #return result
    latest_transaction = df.iloc[-1]


    # Check for NaN values in the latest transaction
    print(f"\nChecking latest transaction for TransactionID: {transaction_data['TransactionID']}")
    print("Full row data:")
    print(latest_transaction.to_dict())  # Print the entire row for context
    
    # Identify columns with NaN
    nan_columns = {col: val for col, val in latest_transaction.items() if pd.isna(val)}
    if nan_columns:
        print("\nColumns with NaN values:")
        for col, val in nan_columns.items():
            print(f"{col}: {val}")
    else:
        print("\nNo NaN values found in the latest transaction.")

    # Your fraud score calculations (unchanged)
    fraud_score_email = latest_transaction['EmailFraudFlag'] * 25
    fraud_score_velocity = (1 if latest_transaction['TransactionVelocity_E10'] > 5 else 0) * 20
    fraud_score_region_device = (
        latest_transaction['RegionAnomaly_E12'] * 15 +
        latest_transaction['DeviceMismatch_M6'] * 5 +
        latest_transaction['RegionMismatch_M8'] * 5
    )
    fraud_score_amount_timing = (
        (1 if latest_transaction['TransactionAmountVariance_E6'] > 10000 else 0) * 10 +
        latest_transaction['TimingAnomaly_E11'] * 20
    )
    fraud_score_device_region_conditional = (
        (10 if latest_transaction['TransactionRatio_E7'] == 1 and latest_transaction['RegionMismatch_M8'] == 1 else 0) +
        (5 if latest_transaction['DeviceMatching_M4'] == 0 else 0)
    )
    fraud_score_device_timing_other_conditionals = (
        (15 if latest_transaction['DeviceMismatch_M6'] == 1 and latest_transaction['TimingAnomaly_E11'] == 1 else 0) +
        (10 if latest_transaction['HourlyTransactionCount_E13'] > 3 else 0) +
        (15 if float(latest_transaction['SameCardDaysDiff_D3']) < 0.01 else 0)
    )
    fraud_score = (
        fraud_score_email + fraud_score_velocity + fraud_score_region_device +
        fraud_score_amount_timing + fraud_score_device_region_conditional +
        fraud_score_device_timing_other_conditionals
    )

    # Construct result with NaN handling
    def safe_int(value, default=0):
        return int(value) if pd.notna(value) else default

    def safe_float(value, default=0.0):
        return float(value) if pd.notna(value) else default
    result = {
        'Distance': float(latest_transaction['Distance']),
        'TransactionTimeSlot_E2': int(latest_transaction['TransactionTimeSlot_E2']),
        'HourWithinSlot_E3': int(latest_transaction['HourWithinSlot_E3']),
        'TransactionWeekday_E4': int(latest_transaction['TransactionWeekday_E4']),
        'AvgTransactionInterval_E5': float(latest_transaction['AvgTransactionInterval_E5']),
        'TransactionAmountVariance_E6': float(latest_transaction['TransactionAmountVariance_E6']),
        'TransactionRatio_E7': float(latest_transaction['TransactionRatio_E7']),
        'MedianTransactionAmount_E8': float(latest_transaction['MedianTransactionAmount_E8']),
        'AvgTransactionAmt_24Hrs_E9': float(latest_transaction['AvgTransactionAmt_24Hrs_E9']),
        'TransactionVelocity_E10': int(latest_transaction['TransactionVelocity_E10']),
        'TimingAnomaly_E11': int(latest_transaction['TimingAnomaly_E11']),
        'RegionAnomaly_E12': int(latest_transaction['RegionAnomaly_E12']),
        'HourlyTransactionCount_E13': int(latest_transaction['HourlyTransactionCount_E13']),
        'DaysSinceLastTransac_D2': float(latest_transaction['DaysSinceLastTransac_D2']),
        'SameCardDaysDiff_D3': float(latest_transaction['SameCardDaysDiff_D3']),
        'SameAddressDaysDiff_D4': float(latest_transaction['SameAddressDaysDiff_D4']),
        'SameReceiverEmailDaysDiff_D10': float(latest_transaction['SameReceiverEmailDaysDiff_D10']),
        'SameDeviceTypeDaysDiff_D11': float(latest_transaction['SameDeviceTypeDaysDiff_D11']),
        'TransactionCount_C1': int(latest_transaction['TransactionCount_C1']),
        'UniqueMerchants_C4': int(latest_transaction['UniqueMerchants_C4']),
        'SameBRegionCount_C5': int(latest_transaction['SameBRegionCount_C5']),
        'SameDeviceCount_C6': int(latest_transaction['SameDeviceCount_C6']),
        'UniqueBRegion_C11': int(latest_transaction['UniqueBRegion_C11']),
        'DeviceMatching_M4': int(latest_transaction['DeviceMatching_M4']),
        'DeviceMismatch_M6': int(latest_transaction['DeviceMismatch_M6']),
        'RegionMismatch_M8': int(latest_transaction['RegionMismatch_M8']),
        'TransactionConsistency_M9': int(latest_transaction['TransactionConsistency_M9']),
        'EmailFraudFlag': int(latest_transaction['EmailFraudFlag']),
        'AmountAnomaly': int(latest_transaction['AmountAnomaly']),
        'UnauthorizedTransactionFlag': int(latest_transaction['UnauthorizedTransactionFlag']),
        'LateNightPattern': int(latest_transaction['LateNightPattern']),
        'EmailDomainChanges_30D': int(latest_transaction['EmailDomainChanges_30D']),
        # 'FraudConfidenceScore':float(fraud_score),
        'InActivity_gap_E14': int(latest_transaction['InActivity_gap_E14']),
        'HighAmount_PostInactivity_E15': int(latest_transaction['HighAmount_PostInactivity_E15']),
        'ProductCD_Amount_Anomaly': int(latest_transaction['ProductCD_Amount_Anomaly']),
        'Delivery_Regions_Anomaly': int(latest_transaction['Delivery_Regions_Anomaly'])
        }
    return result

 
@app.post("/transaction_fraud_check")
async def check_transaction_fraud(transaction: TransactionIn, db: Session = Depends(get_db)):
    try:
        transaction_data = transaction.model_dump()
        engineered_features = calculate_engineered_features(transaction_data, db)
        #fraud_confidence_score = engineered_features["FraudConfidenceScore"]
        transaction_data.update(engineered_features)
        db_transaction = Transaction(**transaction_data)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        transaction_dict = {col.name: getattr(db_transaction, col.name) for col in Transaction.__table__.columns}
        transaction_df = pd.DataFrame([transaction_dict])
        with open(path, "rb") as model_file:
            model = pickle.load(model_file)
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
                "Senderemail": "Sender_Email",
                "Merchantemail": "Merchant_Email",
                "Devicetype": "DeviceType",
                "Deviceinfo": "DeviceInfo",}
        transaction_df.rename(columns=column_mapping, inplace=True)
        categorical_cols = transaction_df.select_dtypes(include=['object']).columns
        all_transactions = pd.read_sql("SELECT * FROM transactions", db.bind)
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            all_transactions[col] = le.fit_transform(all_transactions[col])
            transaction_df[col] = le.transform(transaction_df[col])
            label_encoders[col] = le
        for col in expected_features:
            if col not in transaction_df.columns:
                transaction_df[col] = 0
        transaction_df = transaction_df[expected_features]
        prediction = model.predict(transaction_df)[0]
        prediction_proba = model.predict_proba(transaction_df)[0]
        fraud_probability = prediction_proba[1]
        prediction = 1.00 if fraud_probability > 0.5 else 0.00
        db_transaction.isFraud = int(prediction)
        db.commit()
        if prediction == 1.00:
            explainer = shap.Explainer(model)
            shap_values = explainer(transaction_df)
            shap_values_instance = shap_values[0].values
            feature_names = transaction_df.columns
            shap_df = pd.DataFrame({
                'Feature': feature_names,
                'SHAP Value': shap_values_instance})
            shap_df['Absolute SHAP Value'] = shap_df['SHAP Value'].abs()
            total_abs_shap = shap_df['Absolute SHAP Value'].sum()
            shap_df['Percentage Contribution'] = (shap_df['Absolute SHAP Value'] / total_abs_shap) * 100
            shap_df['Percentage Contribution'] = shap_df['Percentage Contribution'].map(lambda x: f"{x:.2f}")
            shap_df = shap_df.sort_values(by='Percentage Contribution', ascending=False)
            top_features = shap_df[['Feature', 'Percentage Contribution']].to_dict(orient="records")
            return {
                "status": "success",
                "transaction_stored": True,
                "transaction_id": transaction.TransactionID,
                "Distance": engineered_features.get("Distance", 0.0),
                "fraud_detection": {
                    "is_fraud": bool(prediction),
                    "fraud_probability": (round(float(fraud_probability),5)),},
                "transaction_details": {
                    "Transaction": transaction.TransactionID,
                    "Amount": transaction.TransactionAmt,
                    "Datetime": transaction.TransactionDT,
                    "Merchant": transaction.Merchant,
                    "Region": transaction.Order_Region},
                "Top_features": top_features}
        else:
            explainer = shap.Explainer(model)
            shap_values = explainer(transaction_df)
            shap_values_instance = shap_values[0].values
            feature_names = transaction_df.columns
            shap_df = pd.DataFrame({
                'Feature': feature_names,
                'SHAP Value': shap_values_instance})
            shap_df['Absolute SHAP Value'] = shap_df['SHAP Value'].abs()
            total_abs_shap = shap_df['Absolute SHAP Value'].sum()
            shap_df['Percentage Contribution'] = (shap_df['Absolute SHAP Value'] / total_abs_shap) * 100
            shap_df['Percentage Contribution'] = shap_df['Percentage Contribution'].map(lambda x: f"{x:.2f}")
 
            shap_df = shap_df.sort_values(by='Percentage Contribution', ascending=False)
            top_features = shap_df[['Feature', 'Percentage Contribution']].to_dict(orient="records")
            return{
                "status": "success",
                "transaction_stored": True,
                "transaction_id": transaction.TransactionID,
                "Distance": engineered_features.get("Distance", 0.0),
                "fraud_detection": {
                    "is_fraud": bool(prediction),
                    "fraud_probability": (round(float(fraud_probability),5)),},
                "transaction_details": {
                    "Transaction": transaction.TransactionID,
                    "Amount": transaction.TransactionAmt,
                    "Datetime": transaction.TransactionDT,
                    "Merchant": transaction.Merchant,
                    "Region": transaction.Order_Region},
                "Top_features": top_features}
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)