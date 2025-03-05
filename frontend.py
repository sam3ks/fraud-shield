import streamlit as st
import re
import time
from datetime import datetime
import requests
import plotly.graph_objects as go
import pandas as pd
import json
import plotly.express as px

def mask_card_number(card_number):
    """Masks all but the last 4 digits of the card number."""
    if card_number and len(card_number) > 4:
        return "XXXX XXXX XXXX " + card_number[-4:]
    return "XXXX XXXX XXXX"

def fraud_meter(result):
        fraud_probability = result["fraud_detection"]["fraud_probability"]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fraud_probability,
            title={'text': "Fraud Probability", 'font': {'size': 20}},
            gauge={'axis': {'range': [None, 1]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 0.2], 'color': "green"},
                    {'range': [0.2, 0.4], 'color': "#90EE90"},
                    {'range': [0.4, 0.6], 'color': "yellow"},
                    {'range': [0.6, 0.8], 'color': "orange"},
                    {'range': [0.8, 1], 'color': "red"}],
                'threshold': {'line': {'color': "red", 'width': 2}, 'value': fraud_probability}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

def display_top_features(result):
        import plotly.graph_objects as go
        import plotly.express as px
        import pandas as pd
        import streamlit as st

        try:
            # Get top features from result
            top_features = top_features = result['Top_features']
            if not top_features:
                st.info("No feature importance data available for this transaction.")
                return

            # Convert to DataFrame
            features_df = pd.DataFrame(top_features)
            if 'Feature' not in features_df.columns or 'Percentage Contribution' not in features_df.columns:
                st.warning("Unexpected feature importance format.")
                st.write(top_features)
                return

            # Convert percentage contribution to float
            try:
                features_df['Percentage Contribution'] = pd.to_numeric(features_df['Percentage Contribution'], errors='coerce')
            except Exception:
                try:
                    features_df['Percentage Contribution'] = pd.to_numeric(
                        features_df['Percentage Contribution'].astype(str).str.rstrip('%'), errors='coerce'
                )
                except Exception as e:
                    st.warning(f"Could not convert percentage contributions to numbers: {str(e)}")

            # Calculate cumulative contribution
            features_df = features_df.sort_values(by="Percentage Contribution", ascending=False)
            features_df['Cumulative Percentage'] = features_df['Percentage Contribution'].cumsum()

            # Separate top features and group others
            top_features = features_df[features_df['Cumulative Percentage'] <= 90]
            others = features_df[features_df['Cumulative Percentage'] > 90]
            if not others.empty:
                others_row = pd.DataFrame([{
                    'Feature': 'Others',
                    'Percentage Contribution': others['Percentage Contribution'].sum(),
                    'Cumulative Percentage': 100
                }])
                top_features = pd.concat([top_features, others_row], ignore_index=True)

            feature_explanations = {
                "TransactionAmt": "Fraudsters often attempt high-value transactions to maximize their profit before detection.",
                "TransactionDT": "Suspicious transactions may occur at unusual hours, revealing fraudulent patterns.",
                "ProductCD": "Certain product categories are more prone to fraud, like high-value electronics or gift cards.",
                "User_ID": "Multiple User_IDs linked to the same card or region can indicate identity theft.",
                "Merchant": "Transactions with high-risk merchants or unfamiliar vendors may signal fraud.",
                "CardNumber": "Unusual or rarely used card numbers are a red flag for fraudulent activity.",
                "BINNumber": "BIN anomalies suggest cards from suspicious or blacklisted banks.",
                "CardNetwork": "Fraudulent transactions may use lesser-known or compromised card networks.",
                "CardTier": "High-tier cards (Platinum, Gold) are often targeted for their high credit limits.",
                "CardType": "Credit cards are more susceptible to fraud than debit cards due to higher limits.",
                "PhoneNumbers": "Multiple phone numbers linked to a single user can suggest account takeovers.",
                "User_Region": "Transactions from unexpected regions could indicate a compromised account.",
                "Order_Region": "A mismatch between user and order regions is a sign of potential fraud.",
                "Receiver_Region": "Unusual receiver regions may reveal cross-district fraud.",
                "Distance": "Large distances between billing and transaction locations can raise suspicion.",
                "Sender_email": "New or uncommon email domains may be tied to fraudulent activity.",
                "Merchant_email": "Merchants with unverified or mismatched emails are a risk factor.",
                "DeviceType": "Device changes (mobile vs. desktop) can indicate unauthorized access.",
                "DeviceInfo": "Using unknown or outdated devices might signal a fraud attempt.",
            }

            # Create a custom hover template for better explanations
            hover_template = """
                <b>%{label}</b><br>
                🚀 Contribution to Fraud Risk: %{value:.2f}%<br>
                📊 Reason: """ + "%{customdata[0]}" + """<br>
                🏷️ Feature: %{label}
            """

            # Add explanations to the dataframe for custom hover text
            top_features['Explanation'] = top_features['Feature'].map(feature_explanations)

            # Create Sunburst chart
            fig = px.sunburst(
                top_features,
                path=['Feature'],
                values='Percentage Contribution',
                title="Key Factors in Fraud Detection Decision",
                color='Percentage Contribution',
                color_continuous_scale='Oranges',
                custom_data=['Explanation']
            )

            # Update the hover template and text formatting
            fig.update_traces(
            textinfo='label+percent entry',
            insidetextfont=dict(color='black'),
            hovertemplate=hover_template
            )

            # Add a collapsible container for the chart and explanation
            with st.expander("🔍 View Risk Factor Analysis", expanded=False):
                st.markdown("### Analysis of Risk Factors")
                st.write("The sunburst chart below visualizes key factors influencing the fraud detection decision:")
                st.plotly_chart(fig, use_container_width=True)

            # # Display chart and explanation
            # st.markdown("### Analysis of Risk Factors")
            # st.write("The sunburst chart below visualizes key factors influencing the fraud detection decision:")
            # st.plotly_chart(fig, use_container_width=True)

            # # Top feature descriptions
            # st.subheader("Top Risk Indicators")
            # for i, feature in enumerate(top_features.itertuples(), start=1):
            #     if feature.Feature != 'Others':
            #         st.markdown(f"**{i}. {feature.Feature}** - {feature._2:.1f}% contribution")

        except Exception as e:
            st.error(f"Error displaying feature importance: {str(e)}")


def transaction_page():
    # Set page configuration
    st.set_page_config(page_title="Transaction Entry", page_icon='👤',layout="wide")

    # Custom header with e-commerce style
    st.markdown("""
    <div class="main-header">
    <div>
    <h1 class="header-title">Fraud Shield 🛡️</h1>
    <p class="header-subtitle">Analyze transaction risk with AI-powered detection 🔍💻</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Load CSS from file
    def load_css(file_path):
        with open(file_path, "r") as f:
            return f"<style>{f.read()}</style>"

    # Apply CSS
    st.markdown(load_css("styles.css"), unsafe_allow_html=True)
    
    # Initialize session state
    if 'sidebar_open' not in st.session_state:
        st.session_state.sidebar_open = False

    if "transaction_dt" not in st.session_state:
        st.session_state.transaction_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "Retail"
    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = "Books"
    if 'transaction_amount' not in st.session_state:
        st.session_state.transaction_amount = 1500.00
    if 'selected_merchant' not in st.session_state:
        st.session_state.selected_merchant = "Flipkart"
    if 'merchant_email' not in st.session_state:
        st.session_state.merchant_email = "retail@flipkart.com"
    if 'sender_email' not in st.session_state:
        st.session_state.sender_email = "abcd@gmail.com"


    # Function to validate email format
    def validate_email(email):
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    # Function to validate card number
    def validate_card_number(card_number):
        return bool(isinstance(card_number, (int, str)) and str(card_number).isdigit() and len(str(card_number)) == 16)

    # Function to validate BIN number
    def validate_bin_number(bin_number):
        return bool(isinstance(bin_number, (int, str)) and str(bin_number).isdigit() and len(str(bin_number)) == 6)

    # Function to extract BIN number from card number
    def extract_bin(card_number):
        if validate_card_number(card_number):
            return str(card_number)[:6]
        return ""

    # Function to send data to backend
    def send_to_backend(transaction_data):
        try:
            response = requests.post("http://127.0.0.1:8000/transaction_fraud_check", json=transaction_data)
            response.raise_for_status()
            result = response.json()
            return True, result
        except requests.exceptions.RequestException as e:
            return False, f"Error: {str(e)}"

    # Default amounts for each product category
    default_amounts = {
        "Wallet": 2500.00,
        "Consumable": 300.00,
        "Retail": 1200.00,
        "Household": 800.00,
        "Services": 499.00,
        "Miscellaneous": 650.00
    }

    # Product categories with corresponding products
    product_categories = {
        "Retail": [ "Books","Shoes", "Smartphone", "Jewelry", "Beauty Products"],
        "Wallet": ["PhonePe Wallet", "Paytm Wallet", "Google Pay Wallet", "Amazon Pay Wallet"],
        "Consumable": ["Cleaning Products", "Personal Care Products", "Health Supplements", "Fruits and Vegetables", "Medicines"],
        "Household": ["Refrigerator", "Utensils", "Lamp", "Furniture", "Toys", "Pet Supplies"],
        "Services": ["Streaming Subscription", "Online Course", "Cloud Storage"],
        "Miscellaneous": ["Sports Equipment", "In-Game Purchases"]
    }

    product_to_category = {product: category for category, products in product_categories.items() for product in products}

    merchant_options = {
        "Wallet": ["Flipkart", "Amazon", "Google Play", "BigBasket", "Uber", "Zomato", "Swiggy Instamart"],
        "Consumable": ["BigBasket", "Blinkit", "DMart", "JioMart", "Swiggy Instamart", "Zepto", "Nature’s Basket", "MilkBasket"],
        "Retail": ["Flipkart", "Amazon", "Reliance Digital", "Croma", "Tata Cliq", "Myntra", "Nykaa", "Ajio", "Meesho", "Snapdeal"],
        "Household": ["IKEA", "Urban Ladder", "PepperFry", "Wakefit", "Home Centre", "Nilkamal", "Durian", "Godrej Interio", "Hometown"],
        "Services": ["Netflix", "Amazon Prime", "Hotstar", "Spotify", "Zee5", "JioSaavn", "Unacademy", "Byju's", "ALT Balaji", "Sony LIV", "Audable", "Coursera", "Udemy", "Skillshare"],
        "Miscellaneous": ["Dream11", "RummyCircle", "PokerBaazi", "MPL", "Decathlon", "FirstCry", "Tata 1mg", "1x BET", "Betway", "Lottoland", "WinZO", "Nazara Games", "Netmeds", "Practo", "PharmEasy"]
    }
    product_images = {
                            "PhonePe Wallet": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSnyOoxY1k_Hj78I_Vb6S9sP4qV4cL5HkRzsa_7s5_ScOF5FSnIYXSWSwDXOE3xR6KHEu0&usqp=CAU",
                            "Paytm Wallet": "data:image/png;base64,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",
                            "Google Pay Wallet": "data:image/png;base64,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",
                            "Amazon Pay Wallet": "data:image/png;base64,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",
                            
                            "Cleaning Products": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6iK2qXEY8-uvS4atd3hAG2vuYcoKyGzpRGw&s",
                            "Personal Care Products": "data:image/jpeg;base64,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",
                            "Health Supplements": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcYsLq_97zIlevQD4d29Rf2GXkKGxQF14szA&s",
                            "Fruits and Vegetables": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMQERUTExEVExUTFxIVFhcWFREVFhUWFRgWFxcYFhgYHSggGBooHBYXITEiJSorLi4uFyAzODM4NygtLisBCgoKDg0OGxAQGy8lICUtLS0tLy0tLS0tLy0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAOEA4QMBEQACEQEDEQH/xAAcAAEAAgMBAQEAAAAAAAAAAAAABAUCAwYHAQj/xAA+EAACAQIDBQUDCwMEAwEAAAABAgADEQQhMQUSQVFhBhMicYEykaEHFCNCUmKxwdHh8DNy8RWCosKSstJT/8QAGgEBAAIDAQAAAAAAAAAAAAAAAAIEAQMFBv/EADURAAIBAgQEBAUDBAIDAAAAAAABAgMRBBIhMQUTQVEiMmGhcbHR4fAUgZEjUmLBFfEGM0L/2gAMAwEAAhEDEQA/APcYAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgHwsBx1gXPsAg7S2tSw273r7u+bDInzOWgFxn1kJ1Ix3NVStCnbM9ycJM2iAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAeefKBim+cooJHdorLbgxJNx1yX3Tn4qTzpHG4hUfNSXQ7TYWO+cYenU4sPF/cMm+IMu0554pnToVOZTUjz3tlje9xTi/hp2pj09r/kT7pz8RPNP4HHxtTPVa7aHf9nK/eYWixzO4oPUr4T+Ev0neCZ18NLNSi/QmtiUDhC6h2BIW43iBqQJO6vY25le3U2zJIQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEA4vt7ia1J6TU6jotmHhYgbwIOdtcjx5GU8VKUWmmcziE6kHFxdiZ2V7TjEfRVbCqNDoKgHLk3T3dJ0K+fR7mzCYvmeGW/wAznu362xd+dND8WH5SvivOUuIL+r+xZdgtpBKVdG0pjvR5WO9/6j3zZhZ2i121N/D6toST6anF1KhYljqxJPmTcyk3d3OW3d3Z6JsHaSUNnLUYg7gbIEXLFm3V6E3E6VOahRTZ26FRU8MpPojmuz2JfEbRp1HN2LOTyACNkOQGkq0pOdVNlDDzlUxKk/U9ME6R3RAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQCq7TbN+c4d0A8Q8Sf3LoPUXHrNVaGeNiviaXNpuPXoeU03KkEEqVIIIyII/OcpOzueeTad0XXaHaAxVOjWyDqGpVR1FmUjofEfQjhN9aedKXXZlvE1edGM+uzOU7NbebvK6E/wBZGVc8gu8pItz3VPvMzJZI6dVY2OGSm8vVWJWLrd2jP9kE+vD4zRFXdilCOaSRRdmKjGpUzNmG82erA+Ekc/E3vMsVrKKRcxK8Gh6d2AoAPUruQq013d4kAXbM5nkB/wApLCx1cmT4fBJub2Wh2+B2jSr37qor7psbHSXYzjLys6kKsJ+V3JUkbBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQDxXtJtWmmPxFJ0NLdqGzaqd4BgT9m97+s5telLM2jkYjDxc21ofGW381ldM58ouLszhsJUNMrUGtN1v+Nv8AiR6y9JXVjqHRdp6lqYUfXYW8hn+krUFrcqUYWqP0NfZykFavbQFVHoX/AEmaz2J4h+AtMbtJaSAO5tclUzOfEhefWQipS0RVhGc9Ft7Hf/JfVp1cK1VCbtUKsCLFSgFh1ya/+6X8PDLE7GCpcuDvuzs5YLogCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIB5J8suxAK1HFDJan0NU8AwBNNj6XB/sE01V1RVxEdcxynZ/HkXw9TIrfcv01T9P8SjWh/8AaKFannjdFRUpWaunK7D0cW+DGbk9EzZF3SZJxeJ7xqAvklNWb0ALfBPjIwjlv8SMY2bfcx2dtQUaT2F6jtfppqfUnKJ080l2MVKedpdCP82q1qq0wGqVqjAbvG50XpzPADyM2xXRG2EekT9Cdj9gjAYSnQB3mF2qMPrVGzYjpwHQCWYqysdCEMsbF1JExAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQCt7R7HTG4aph3yFRbA/ZYZqw8mAMxJXViMoqSsz87bVovRc06gKV6LbjjPPd9lgfK2fEFTKmWzsc9pxdmalrtUZmCli67rboJzyzy8piyirBRvsR33k9oFbi3iBBt6zKs9g01ubsJVVLvqwyQcifrHy/Ew1fQw9T2H5Luxxwq/OsQv09UeFW1pIczfk7ceQsOcsQjbUuUaeXVnoM2G8QBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQDVXrBBc/5mjEYiFGOaRKMXJ2RzG0djYfFVxWqYem1QKFBYb2QzFwciepE89Xx9Ws7LRen1LH6emvE1dm/EVUw6XchFGWWl+QAlRRb3LFODm8sEasGzVwWqUwtNh4UcXZh9pr5AdJO2XYlVhFeHd9exGwnZTB0sQuIXDIGXMAXCA8GCeyGHDL42luhjqlN+LVe5Slhabd0rM7CjVDC4noKNaFWOaDNMouLszObTAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIAgCAIBrr1QiljoJrq1I04uctkSjFydkUi1DVLMegA4Acp5SvWniJuT/YvuKppRRB2rjO53QPFUuCqLclxxvbQWub8wJrhHU20qef4dzVgdm9/avXYVCRdEGdNAeXMzY32JTq5P6cNO76skYjH/ADUfS3KfVbVr67jczyb38y3IQpc1+Hf81JmFqs6BmXcJF90m5HK/W0izXKKi7J3N9KoUO8NOI5ib8PiJUJ5lt1RrnFTVi1RgRccZ6iE1JKS6lNqxlJGBANL4pA4Quoci4UsAxGlwNTpMOSW7IucU7X1N0ySEAQBAEAQBAEAQBAEAQBAEAQBAEAQCl23iLkIOGZ8+H86zgcWxF5KkumrL2Ep6Zmc9T2hUBahSG9UufET4VTKzNxJF7W6TlpdWX5Uo+eW3+y02Zs8UrkktUb2nb2j06DpMptlerUz6LbsR8RiRgyWOdFySANUqZkgD7LfA9DJ7kow5+i8y90YYXZ7V277ED+ykc1QH7XNv5ysbtsZlVUFkp/u+5sqF8JmAalAajV6Q6X9pOmojcilGtptL2f0Zv2btH5wWKr9GvhDHVm42HAW585hojVpcqye5c7Pe3hPmPznX4VW0dJ/FFKsuqJ07JoEA4T5T8A+7SxKC/dbyVP7WIIJ6Agj/AHCV8RBSVzk8Upysqkem5F7NdsO7oVTVYuKVN6iXPiugv3d+uVpoo1XC8ZfsT4biHVfLb+B0vYXaWIxWDSviQgaoWZd0Ffo/qkgk65kdCJbpOTjdnXqJKVkdBNhrEAQBAEAQBAEAQBAEAQDRi8WlFd+o4RbgXJsLk2HxmHJJXZGc4wV5OxnRrq43lYMDxUgj3iFJPYypJ6o2TJk+M1hc8M5iTSV2FqcdtBnqE7p3S5N2+yOg4nhPG1KnMqOcup26UYwST6GP+k7tJWpeF0JKsdWJ1DniD+kwpN6vYw615tT1T/NDbT7QJ3d2UiqDuGlq5fkBy6zYkQeFlmsnpvfpY+4TZzVG73EAM5BCpqlNTw6tzMXtsJ1VFZKe3fqzJajYXI3ahwOZal0biU68OMzuYcVV283z+5Crs2PfdW64dT4m0NQjgOn+eUzsbYpYdXfm+RKrbFCnfw7dy4sMs0a3Bl/OYT7mtYi+lRXXuadlbcqmoN+ldVYo1SkGdS2XuFic8+E3UZ8qpGfr7Ga+Ghl0eu9nudqJ6k44gGLqCCCAQciDmCOsBq55h8oexMJSwtZ8MbVfAO7ptvKbuobw52sCTYEaShWnR2TVzRQwdGFZVI6fI9A2JXpdzTp03U92iLug5gKoGmvCWaVanNWi7m9u7LGbgIAgCAIAgCAIAgCAIAgFR2s2ecTg61JRdit1HNkIdR6lbesjOOaLRXxdLm0ZRR5X2f25UoPdWIYajg4HAic15qbzRPP4bEzpy0Oj7edq6xXCUcGxSriiGytcZhFS9sgXJufucryzOs5Rjk6nrMLlqRzvY7jFlkw9mbebdVWa1t5sgxtwvmZHHzyYeX8fySoLNURQNe2Ws8odUwfallFOkveVGHs/Zz1c/VmxRfXYjybvNLRfmxo/0Z/6gqn5xrvfU0tuW+zbKSjPW3Ql+oXlt4ff4/EnbP2wGJp1h3VVdVOQIHFTxEnY01KDSzQ1T/NSHVdscxVSVw6nxMMjVI4L92Z2NqSoK71l8iScG+HO9h/EnGiTl502PsnocjMXvua88amlTfv9SJtDapxG7Qohld795vAqaaj2gRz/AJxmUramynQVK9Spqlt6l1hMGtKmEUWVRbz5k9eMhLUrSqOcsz3LnCPdFPT8Mp6jCTz0Yy9CjNWk0bpZIHI9q9qEsaSmyjJrfWPEeQnF4hiW3y4vTqa27uxR4bDbwudJy0jDJAw+6QyEqwzBB4ySbi7x3C0O12PjO+oo51Is39wNj+E9LhqvNpqRtJs3gQBAEAQBAEAQBAEAibR2jSw679WoEHC+p6ADMnykZTjFXZto0KlaWWmrs4/E/KfhlYhKNZwPreBQfK7X99poeKj2OpDgldq8pJfnwOc2niNnY5zUp1WwVZjciol6bNzJQkIevwvIOdOfocfHf+L1m89Pf0+mjI2xNyltfDmvXoslGi7h1qK1LMVLWY2zu17c5CnFQnq9BgsJiKVF0pxea+38HRdpvlCo/wBOghq2Ny5JRMr+zcXbzsBNeNy14ZE+p3cFwmovHUdvTdlNh+2feeFkNK/11O/YdAQM/f5TkzwWXVO50Hw9rVO/sdPs5VVBVw/0gPti9y+etzo4vx105Wqu97SObWTzZKmnb0+xbU9oU2Q1ARYak5bttQ19D0mb67alR0pp5SmrUDtAg23KK33WsN+oeYvov88p3yluMv06tvL2X3NmHxj4O1OuL0hYJVUZAcA4Gn81jfUhKnGt4ob9voTto7VVE+jKuxHhAItnoSeUjmS3NdLDylLxaI500qXd3YO9YneNQMEO8eRzy9IVRXLlTnLyJW7EvZG3aoslZSRe3eZXHLeA1HWbJqnbwyOV/Xc7ypWXpqdnst708jfM/r+c7fCpXoW7NmmurTJZM6LNJ5tjHLEseJJPqbzytR5m2V4PUYfE7osRlIJmxonA3kiJd9j610deTEj1/wAfGdfhdTwyj+5sidDOqSEAQBAEAQBAEAQCJtTHrh6T1X0QXtxJ0AHUmw9ZGclFXZtoUZVqipx3Z4xt7alTEM1Wo12OQHBQfqryE5cpucrs9vh8PDD08kF9/ic/MG03YajvHoNZCpLKgiS2BQm9res0KrIykk721NyUgugkXJvcGNbDhuh5zMZtAsOzW2mwz3Nyh8NReduI+8NfhI1qakrFbF4VYiH+S2Z1h2dUxJNVgtO+6VpkGz20NW3T+c6OZR0ONzY0vAtfX6FzgNqKfo6g7p1HstYCw4qdGWEVKlFrxR1RUbR2wazFEypjXm/nyHSYk7It0MPl8Ut/kRJqLRki3NphuyMEhaYHCanJkbkvA4x6Juhy4qfZPpwPUS1hcbUw7vHbsaK1CFVeLfudTSx61KLOOCtccVIF7GeqpYmFai6kf+jh1qUqUssjg2GU889ignqRprLBKo4rdW1sxpMpmLFl2axfduCTkSQ3kbZ++WcHW5VVN7PQyjt56UmIAgCAIAgCAIAgHHfKZXIoU0H16lz1CqfzIPpKuLfgSO1wOCddyfRHl20PZHn+RlBHqWV8kRJuz9D5iV626MolzSBAEAww+FepUYIjPcA+EE28+U2OSUU2QlWhT1m0vieobAqP3CJVQoyKoubG4GXDjloZQnFNs8ripU+a5U3dNlb2srrdKYAJ9okgEjhYH+aCRStsb8Gm7yKnAjU+UhMvEmQBuw/GQmRZvmsiIBktdkVgpsHG63Ufz8TLOGryptpbPRlTG0ObSdt1sQarWHnLUmebgrsjyBuNlKkW0hIwS6VEpmDfmP06zNhc63YG0BUXdJuVGR5r+o0ncwGJ5kckt18iaZbzpGRAEAQBAEAQBAOO+U2gTh6bj6lSx6BlP5ge+VcWvCmdrgc0q8o91/s8vx48HkR+koI9SyukiJJwNSzW5/jNVWN1cyifKxkQYOm7KbPpVEZ3QMQ26L5gCwOmnGaasmnocLi2Kq05xhB2VjqcPRVRZQFA0AAA9wmnfc4Mpym7yd2bt2ZsRMK1IMLMoYdRBKM5Rd0yoxOyhTBancrqRqR5cxNc1fVHUw+MzeGe5CmsvmdJrGRkrowyVNRAQBAK+tr5S+ndJnmasMlSS9Wa5kgT8CfD6ySIskTJgYWsaVQMvE39eI8iLyVObpzU10JJnc0agZQw0IBHrPUQkpRUl1NhnJAQBAEAQBAEAg7b2eMTQqUj9dcjyYZqfeBIVI5otG/DVnRqxqLozxTE0T4kIswupB4MMrH1E5NrM93GSlHMtimkjAgEuhi+De/9ZpnS6ozcmyuDuOyybuHXmxZj7yPwAlar5jyHFKjlipLtZFxeaygZrUmUzNzYDJGTBhbMTDMFPtPDhSGGjfAzVJdTsYOu5xyvdFfVfdBPKRSuy4T8Qndsy33gts8he4vpJToJS3NdOWdJ9zUKh5a31y06yPI9SdkZ0rt7K3tr0HMnQCZWHb2ZGTjHci1KVyTfj5ibkrKxQqcPVSblm31tY+vg2UXIyOh1B9RlJOLRqXDoN2z+ww53T6TCZJ8K/wAvYnYY77ItwN8kcytuYk4u7sap8NypvNt6Glam8m9a2ZI/2n9pgoVqXLnludnsQ/QJ/u/9jPQ4Ft0ImFsT5cMiAIAgCAIAgCAeb/KHsbu6gxCjw1cn6OBkfUD3jrKGJp2eZHp+C4vPDky3W3w+x53i6e6x65j1lZHaZpmQIBaUGuoPSU5q0mZO07MV70AOKFh7zvD8ZWqLU8jxim4Yly7q5fK15pOcncygyZI1plMGZYTNzJA2j/TPmD8bfnNcti1gnaqimdbgjmJrR2y3w+DOIRKgYC6hWuLneXI/EfGXlTc/EijzlSbi110N1TBUaAu5LHgOfkJl04xV2YVarVdo6FdisW1TIAKozCjIevMzVKV9Ohap0VDV6vv+bH1Kd6DNydfwI/7SSXgv6mHK1ZL0Z8wuKKN4Tui2YPiBIH5n3SMZOOxmpSzLxK7LOjToYgezuNxtl+xm1ZJ+jKsnVove6MMRg+43qxa+6ptkB4iN1dOpjl5PE2Y5/MSp2K6lT3UVBmTZQObHL8TIKLei3OLWnzKrl3Z3mEo92iryAHrx+M9RRp8uCj2BumwCAIAgCAIAgCARtpYJK9JqTi6uLHpyI6g2PpIyipKzNlGrKlNTjujxTb2yno1GpP7SHI8GHAjoRYzlSi4Ssz3OHrRr01Uj1/LFCRBsOi7LbCpYoHvHqKQ274Cgy3QRqp43letVlBpI43EeIVMNVjGKVmup06djsPTGdWrbq1P/AOJWlVbdyk+N1l0Xv9SbsrY1OkSabVSGFjvFN020I8IN9feZCTvuU8Vjp4pJTS06osAgAv4rW4WPvEg4opKy1M6ZVtGv6zGRGU0zXUazhRpa/XjMSikYcvFYzkCRA221qJtzX8Zkt4L/ANy/coUxZ4i8i4HbLLYu1AjMl91amhNrI+l/I8ZvozcdGVcRSzWl2+R9rlgx37lwbknO/pxEjK99TfBRcfDsamtfnx0tnymCavYt8NSvhX6kt7rfpN0VemylUlbEIqWAtcDQC9yNc9Ok0l1Np2Zsw6sXtTvfh+8yld2RGbSjeZIx9SpiGWlTBqBD4mUZM466WHMyxkqVPDDU49eoqcWlvL2X3Og2FsPuj3lQ71ThxCeXM9Z18JguV4p6v5HOSsXk6BkQBAEAQBAEAQBAIVbFG9hl1gg5djju3WzjUQVxm1PJuqHj6H4Eypiqd1mR3OB4vJUdGT0lt8fuef18MG6Hn+so3PVNXLHss5o1SpI3alhfkw9n8SPdNGIjmjddDjcawjq0c8d4/Lqd5hcMG8TG/wDOMpHlIQvqyZUbdBPIE+6ZNr0RqwTXQdMvdCIwd4mjGYTVhbmRw8x1ghOHVGihcZyD1Ix01JCsx0F/QzKpSlsmTzMwr4J6yMulxq1wJYo4OpUeit6s2UK3LqKTKs9mq/3P/I/pNv8Axtf0/k63/JUfU34fss59uooH3QWPxtNsOFTfnkap8UivJH+SZiMA1MAEGtTGhFu9Qf8AcdNZjEYCUNY6r3X1I0MapPfK/Z/Qhigrn6OorEZbrWVh0KtOfkd7fn8F9Vkl4lb1WpfbPoFaIVhmQb+t5YpxtGzKNaeao5IoWwqp/UqovQHfc9AFlfltaNl94i+sU37Im4XBs4sqtRpn2mP9WoOQH1B8Z0MPgZT1lovd/Q52IxkV1u/ZfUuaNJUUKoAUZACdqEFBWjscmc3N5pbm5KzDQyRi7J2Gr73mJk2J3N0GRAEAQBAEAQBAI9bChsxkYIuNyLVwZsQQGByPG4PMGYaMLNF3RytXsTS7ze3nVNdyw9wY8Pj1lZ4WN79DtR47XVPK4q/csKvZzCsu73KjkVuG/wDLU+t5sdCm1axSjxTFKWbPf0e38HxdmvSA3HL213rXPnawJ905mI4e1rT19PoVJ1c03KKtfotjXXxN1KspUkWnOlGUdGrB1LqxhhMRugixYk5AeUjFN6JEYTsiVSwj1Dep4V+yJ0cPgJSd6mi7dTDk5blgKajRR7hOsqUFskYM5sMCAIAgCAacRhKdT20VvMAn3zXOjCfmSZshWqQ8raIv+i4f/wDIe9re680/oqH9pu/W1/7iTh8HTp+xTVfIAH36zdCjTh5YpGqdapPzNs3zYajNaTHQGDNmbkwZOpt8ZkllJdKkFGUEkrGcGRAEAQBAEAQBAEAQBAMDSU8B7hBixgcMvL8YGVGJwannMNJ7mMqMfmK8CR7oSS2GVHz5l974TJjKfPmX3vh+8DKPmX3vh+8DKPmX3vh+8DKPmX3vh+8DKBgvvfD94GU+jBDmYM5TIYJeZ+EDKjIYReR98DKjIYdR9UQZsjYFA0AEGT7AEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQBAEAQD/9k=",
                            
                            
                            "Shoes": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEPtSTOGA7x11GfR0KNbVh_3x7Ki-EEAIBew&s",
                            "Smartphone": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRSPcrMyFSLXvBm8zHnfAeP0nOOWxIEuqXolg&s",
                            "Jewelry": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTgPQMhiipHUtkMOZaxlXjbZPXp5Fv_7XS6-A&s",
                            "Beauty Products": "https://thumbs.dreamstime.com/b/cherry-scented-shampoo-line-icon-personal-hygiene-products-natural-korean-cosmetics-skin-care-ointments-balms-vector-color-cherry-293696101.jpg",
                            "Books": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTy0rC9zlMib-WH5siW7pLDTTPR4AidxDpKWw&s",
                            
                            "Refrigerator": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShInzS4TVgKqJV45P2FvbxA-mjg3PWIfBR8A&s",
                            "Utensils": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdFma2TFfEProAEfDtmaQbFG-36GxNgHQ8Bg&s",
                            "Lamp": "https://classroomclipart.com/images/gallery/Animations/Objects/desk-lamp-animation.gif",
                            "Furniture": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQezE24HS7q5FBDdajQ3Yu0CSTF_RqmeQfstg&s",
                            
                            "Streaming Subscription": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5xCPw5q9UXYErxcE9UPrwCb4AmaPjvutqvw&s",
                            "Online Course": "data:image/png;base64,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",
                            "Cloud Storage": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQLCT6hZL8QQiNgFaYYwHnx1q_iv8GGrt8kYA&s",
                            
                            "Sports Equipment": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQep3BOqNzrmxXN8tUq6nYQEn4zdNHVm54hZg&s",
                            "Toys": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2CQXi6x5QtW5XrCKgcnKAYRQBecfahGlZ1g&s",
                            "In-Game Purchases": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS95xOhn_KxkQaLk9yg_AjrPP4xvScloeYIBw&s",
                            "Medicines": "data:image/png;base64,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",
                            "Pet Supplies": "data:image/png;base64,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"
                            }

    # Tooltips
    card_number_tooltip = "Enter a 16-digit card number."
    email_tooltip = "Enter a valid email address."
    phone_number_tooltip = "Phone number should start with +91 followed by a 10-digit number."
    date_time_tooltip = "Enter the Date & Time in the format YY:MM:DD 00:00"


    # Create merchant email mapping
    def get_merchant_email(category, merchant):
        if merchant:
            return f"{category.lower()}@{merchant.lower().replace(' ', '')}.com"
        return ""

    # UI Layout: Top bar with profile icon
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Transaction Entry Form")
    with col2:
        if st.button("👤", key="profile_button"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            time.sleep(0.2)

    # Sidebar Logic
    if st.session_state.sidebar_open:
        with st.sidebar:
            st.sidebar.markdown("<h2 style='color:#6c63ff;'>Profile Information 👤</h2>", unsafe_allow_html=True)

            # with st.expander("**Transaction Hour**", expanded=True):
            #     transaction_dt = st.text_input("Transaction Date & Time", value=st.session_state.transaction_dt, help=date_time_tooltip)

            with st.expander("⌛ **Transaction Date & Time**", expanded=True):
                # Use date_input for selecting day, month, and year via a calendar
                transaction_date = st.date_input(
                    "Transaction Date",
                    value=datetime.now(),
                    min_value=datetime(2020, 1, 1),
                    max_value=datetime(2030, 12, 31),
                    help="Select the date of the transaction using the calendar."
                )
                
                # Use text_input for manually entering the time
                transaction_time = st.text_input(
                    "Transaction Time (HH:MM:SS)",
                    value=datetime.now().strftime("%H:%M:%S"),  # Default to current time
                    max_chars=8,  # Limit to "HH:MM:SS" length
                    help="Enter the time in HH:MM:SS format (e.g., 14:30:00)"
                )
                
                # Validate and combine date and time
                time_pattern = re.compile(r"^\d{2}:\d{2}:\d{2}$")  # Regex for HH:MM:SS
                if time_pattern.match(transaction_time):
                    try:
                        # Combine date and time into a datetime object and format it
                        transaction_dt = datetime.strptime(
                            f"{transaction_date} {transaction_time}", "%Y-%m-%d %H:%M:%S"
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.transaction_dt = transaction_dt
                        # st.write(f"Transaction Time: {transaction_dt}")
                    except ValueError:
                        st.error("Invalid time format! Please enter a valid time (e.g., 14:30:00).")
                        transaction_dt = st.session_state.transaction_dt  # Keep previous valid value
                else:
                    st.error("Time must be in HH:MM:SS format (e.g., 14:30:00).")
                    transaction_dt = st.session_state.transaction_dt  # Keep previous valid value
    

            with st.expander("💳 **Card Details**", expanded=True):
                # if "card_number" not in st.session_state:
                #     st.session_state.card_number = ""   

                if "masked_input" not in st.session_state:
                    st.session_state.masked_input = ""        

                # Text input (password type) without the eye icon
                card_number = st.text_input("Enter Card Number", placeholder="Enter Card Number", value="9874569832541458")

                # # Only store numeric values (prevent masking errors)
                # if user_input.isdigit():
                #     st.session_state.card_number = user_input
                #     st.session_state.masked_input = mask_card_number(user_input)
                
                # card_number = st.session_state.card_number
                bin_number  =card_number[:6] if len(card_number) >= 6 else "" 

            with st.expander("📋 **Card Specifications**", expanded=True):
                card_network = st.radio("Card Network", ["Visa", "Mastercard", "American Express", "Rupay"], horizontal=True)
                card_tier = st.radio("Card Tier", ["Silver", "Gold","Black" ,"Platinum"], horizontal=True)
                card_type = st.radio("Card Type", ["Debit", "Credit", "Prepaid"], horizontal=True)

            with st.expander("📞 **Contact & Region**", expanded=True):
                user_id = st.text_input("User ID", placeholder="Enter a valid User ID",value="1234")
                if user_id:
                    if not user_id.isdigit() or len(user_id) > 6 or len(user_id) < 1:
                        if not user_id.isdigit():
                            st.error("User ID must contain only digits")
                        if len(user_id) > 6:
                            st.error("User ID must be at most 6 digits")
                        if len(user_id) < 1:
                            st.error("User ID must be at least 1 digit")

                phone_number = st.text_input("Phone Number", placeholder="+91 XXXXXXXXXX", help=phone_number_tooltip,value="+91 1234567891")
                if phone_number and not re.match(r'^\+91\s\d{10}$', phone_number):
                    st.error("Phone number must be in the format: +91 XXXXXXXXXX")

                region = [
                    "Bengaluru Urban","Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural",  "Bidar",
                    "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada",
                    "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar",
                    "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru",
                    "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"
                ]
                user_region = st.selectbox("User Region", region)
                sender_email = st.text_input(
                    "Sender Email",
                    value=st.session_state.sender_email,
                    placeholder="Enter sender's email",
                    help=email_tooltip,
                    key="sender_email_input"
                )
                if sender_email != st.session_state.sender_email:
                    st.session_state.sender_email = sender_email
                if sender_email and not validate_email(sender_email):
                    st.error("Please enter a valid email address")

            with st.expander("📲 **Device Information**", expanded=True):
                device_info_to_type = {
                    "Windows": "Desktop",
                    "Linux":"Desktop",
                    "MacOS": "Desktop",
                    "iOS Device": "Mobile",
                    "Android": "Mobile",
                    "Samsung": "Mobile",
                    "Redmi": "Mobile",
                    "Realme": "Mobile",
                    "Oppo": "Mobile",
                    "Vivo": "Mobile",
                    "Motorola": "Mobile",
                    "Pixel": "Mobile",
                    "Poco": "Mobile",
                    "Huawei": "Mobile"
                }
                device_info = st.selectbox("Device Info", list(device_info_to_type.keys()))
                device_type = device_info_to_type.get(device_info, "Unknown")
                # st.markdown(f"**Device Type:** :blue[{device_type}]")

                merchant_email = st.text_input(
                    "Merchant Email",
                    value=st.session_state.merchant_email,
                    help=email_tooltip,
                    key="merchant_email_input"
                )
                if merchant_email != st.session_state.merchant_email:
                    st.session_state.merchant_email = merchant_email

    # Main Content: Transaction Entry Form
    with st.expander("🛒 **Product Category & Merchant Details**", expanded=True):
        st.subheader("Select your product")
        all_products = [product for category_products in product_categories.values() for product in category_products]
        selected_product = st.selectbox(
                                        "Products",
                                        all_products,
                                        index=all_products.index(st.session_state.selected_product)
                                    )
        st.image(product_images[selected_product], width=100) 
        
        if selected_product != st.session_state.selected_product:
            st.session_state.selected_product = selected_product
            
            st.session_state.selected_category = product_to_category[selected_product]
            st.session_state.transaction_amount = default_amounts[st.session_state.selected_category]

            merchants = merchant_options.get(st.session_state.selected_category, [])
            st.session_state.selected_merchant = merchants[0] if merchants else None
            st.session_state.merchant_email = get_merchant_email(st.session_state.selected_category, st.session_state.selected_merchant)

        category = st.session_state.selected_category
        merchants = merchant_options.get(category, [])
        selected_merchant = st.selectbox(
            "Merchant",
            merchants,
            index=merchants.index(st.session_state.selected_merchant) if st.session_state.selected_merchant in merchants else 0
        )
        if selected_merchant != st.session_state.selected_merchant:
            st.session_state.selected_merchant = selected_merchant
            st.session_state.merchant_email = get_merchant_email(category, selected_merchant)

    with st.expander("💵 **Transaction Details**", expanded=True):
        col1 = st.columns(1)[0]
        with col1:
            transaction_amt = st.number_input(
                "Transaction Amount (₹)",
                min_value=0.01,
                max_value=5000000.0,
                value=st.session_state.transaction_amount,
                format="%.2f"
            )

    with st.expander("🌎 **Order & Receiver Details**", expanded=True):
        regions = [
            "Bengaluru Urban","Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural",  "Bidar",
            "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", "Dakshina Kannada",
            "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar",
            "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru",
            "Udupi", "Uttara Kannada", "Vijayapura", "Yadgir"
        ]
        col1, col2 = st.columns(2)
        with col1:
            order_region = st.selectbox("Where are you ordering from?", regions)
        with col2:
            receiver_region = st.selectbox("Deliver To ", regions)

    # Submit Button
    st.divider()
    if st.button("**Submit Transaction**", use_container_width=True, key="submit_transaction_2"):
        errors = []
        if not transaction_dt.strip():
            errors.append("Transaction Date & Time is required!")
        if transaction_amt <= 0:
            errors.append("Transaction Amount must be greater than 0!")
        if not st.session_state.selected_category:
            errors.append("Product Category is required!")
        if not selected_merchant:
            errors.append("Merchant is required!")
        if not order_region:
            errors.append("Order Region is required!")
        if not receiver_region:
            errors.append("Receiver Region is required!")
        if not user_region:
            errors.append("User Region is required!")
        if not st.session_state.merchant_email.strip():
            errors.append("Merchant Email is required!")
        if not card_number:
            errors.append("Card Number is required!")
        if not bin_number:
            errors.append("BIN Number is required!")
        if not phone_number:
            errors.append("Phone number is required!")
        if not st.session_state.sender_email:
            errors.append("Sender Email is required!")
        if not user_id:
            errors.append("User ID is required!")
        if not validate_card_number(card_number):
            errors.append("Invalid Card Number!")
        if not validate_bin_number(bin_number):
            errors.append("Invalid BIN Number!")
        if not validate_email(st.session_state.sender_email):
            errors.append("Invalid Sender Email format!")
        if not validate_email(st.session_state.merchant_email):
            errors.append("Invalid Merchant Email format!")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Generate transaction_id using current timestamp (Unix epoch in milliseconds)
            transaction_id = int(time.time() * 1000) # Unique integer based on milliseconds

            # Prepare transaction data
            transaction_data = {
                "TransactionID": transaction_id,
                "TransactionAmt": float(transaction_amt),
                "TransactionDT": transaction_dt,
                "ProductCD": st.session_state.selected_category,
                "User_ID": int(user_id),
                "Merchant": selected_merchant,
                "BINNumber": bin_number,
                "CardNumber": card_number,
                "CardNetwork": card_network,
                "CardTier": card_tier,
                "CardType": card_type,
                "PhoneNumbers": phone_number,
                "User_Region": user_region,
                "Order_Region": order_region,
                "Receiver_Region": receiver_region,
                "Sender_email": st.session_state.sender_email,
                "Merchant_email": st.session_state.merchant_email,
                "DeviceInfo": device_info,
                "DeviceType": device_info_to_type.get(device_info, "Unknown")
            }

            # Send data to backend
            success, result = send_to_backend(transaction_data)

            if success:
                st.session_state.transaction_result = result  # Store the result in session state
                fraud_probability = result["fraud_detection"]["fraud_probability"]
                    
                    # Determine the transaction status
                if  fraud_probability > 0.6:
                    st.session_state.otp_verified = True
                    st.session_state.transaction_verified = True
                    st.markdown(
                            """
                            <div style="background-color:#DFF2BF; padding: 15px; border-radius: 10px;">
                            <h3 style="color:#4F8A10;"> <b>Transaction is Legit!</b> </h3>
                            <p>Your transaction has been <b>successfully processed</b>. No further action is required.</p>
                            <h4>🎉 Thank you for using our service! Have a great day ahead! 😊</h4>
                            </div>
                            """, unsafe_allow_html=True
                        )
                    fraud_meter(st.session_state.transaction_result)
                    display_top_features(st.session_state.transaction_result) 
        
                elif fraud_probability <= 0.3:
                    st.markdown("""
                                        <div style="background-color:#FFF4CC; padding: 15px; border-radius: 10px;">
                                        <h3 style="color:#9F6000;">Transaction Suspicious!</h3>
                                        <p>Your transaction appears to be suspicious. An OTP has been sent to your registered mobile number for verification.</p>
                                        </div>
                                    """, unsafe_allow_html=True)

                        # if st.button("Go to OTP Verification"):
                    st.session_state.show_otp_page = True
                    st.rerun()
                else:
                    st.markdown(
                            """
                            <div style="background-color:#FFCCCC; padding: 15px; border-radius: 10px;">
                            <h3 style="color:#D8000C;"> <b>Transaction is Fraudulent!</b> </h3>
                            <p>Your transaction has been <b>flagged as potentially fraudulent</b> and is currently <b>on hold</b>.
                            Please contact our <b>customer support team</b> for further assistance and verification.</p>
                            </div>
                            """, unsafe_allow_html=True
                        )
                    fraud_meter(st.session_state.transaction_result)
                    display_top_features(st.session_state.transaction_result) 
            else:
                st.error(f"Failed to submit transaction: {result}")
                st.info("Please make sure your backend API is running at http://127.0.0.1:8000")    


        
def otp_page():
    st.title("OTP Verification Page")
    st.markdown("""
        <div style="background-color:#FFF4CC; padding: 15px; border-radius: 10px;">
        <h3 style="color:#9F6000;">⚠️ Transaction Suspicious! ⚠️</h3>
        <p>Your transaction appears to be suspicious. An OTP has been sent to your registered mobile number for verification.</p>
        <p><b>Please enter the OTP below to proceed:</b></p>
        </div>
    """, unsafe_allow_html=True)
    fraud_meter(st.session_state.transaction_result)
    display_top_features(st.session_state.transaction_result) 
    
    user_otp = st.text_input("Enter 6-digit OTP", max_chars=6, type="password", key="user_otp")
     
    
    if st.button("Verify OTP"):
        if user_otp == "123456":  # Replace with actual OTP logic
            st.session_state.otp_verified = True
            st.session_state.show_otp_page = False  # Return to main transaction page
            st.markdown("""
                            <div style="background-color:#DFF2BF; padding: 15px; border-radius: 10px;">
                                <h3 style="color:#4F8A10;"><b>OTP Verified Successfully</b></h3>
                                <p>Your OTP has been successfully verified, and the transaction has been <b>marked as legit</b>.</p>
                                <h4>🎉 Thank you for using our service! Have a great day ahead! 😊</h4>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Show Complete Transaction button after OTP verification
            if st.button("Complete Transaction"):
                st.session_state.show_otp_page = False  # Navigate back to the main page
                st.session_state.transaction_verified = True
                st.success("Transaction completed!")
        else:
            st.session_state.otp_verified = False
            st.error("Invalid OTP! Please try again.")
           

        
def main():
    if "otp" not in st.session_state:
        st.session_state.otp = "123456"  # Simulated OTP (Replace with real OTP generation)
    if "otp_verified" not in st.session_state:
        st.session_state.otp_verified = False
    if "transaction_result" not in st.session_state:
        st.session_state.transaction_result = None
    if "user_otp" not in st.session_state:
        st.session_state.user_otp = ""   
    if "transaction_verified" not in st.session_state:
        st.session_state.transaction_verified = False       
    if 'show_otp_page' not in st.session_state:
        st.session_state.show_otp_page = False  

    if st.session_state.show_otp_page:
        otp_page()  # Show OTP page if fraud probability is suspicious
    else:
        transaction_page()  # Show the transaction page



if __name__ == "__main__":
    main()
        
        
        

