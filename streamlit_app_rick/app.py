import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import plotly.express as px
from datetime import timedelta
warnings.filterwarnings('ignore')

# Ignore warnings
warnings.filterwarnings('ignore')

# Configure Streamlit app settings
st.set_page_config(layout="wide",
                   page_title="Campaign Analysis",
                   page_icon="https://cdn.iconscout.com/icon/premium/png-512-thumb/marketing-analysis-3141395-2615916.png?f=webp&w=512"
                   )

# Hide the default "Made with Streamlit" footer
hide_default_format = """
       <style>
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Custom CSS to add an image to the title
custom_css = """
<style>
.title-container {
    display: flex;
    align-items: center;
}

.title-text {
    margin-left: 20px;
}
</style>
"""

# Use the custom CSS to style the title
st.markdown(custom_css, unsafe_allow_html=True)

# Create a title container with an image and text
st.markdown('<div class="title-container"><img src="https://cdn.iconscout.com/icon/premium/png-512-thumb/marketing-analysis-3141395-2615916.png?f=webp&w=512" alt="Image" width="100"/><h1 class="title-text">Campaign Analytics</h1></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Campaign Stats", "Page 3", "Page 4"])

@st.cache_data
def read_data(filepath):
    df = pd.read_csv(filepath)
    df['ACTIVITY_DATE'] = pd.to_datetime(df['ACTIVITY_DATE'], format="%Y-%m-%d")
    return df

@st.cache_data
def max_date(dataframe):
    return dataframe['ACTIVITY_DATE'].max()

@st.cache_data
def roll_back_days(most_recent_date, days_to_roll_back):
    # Calculate the rolled-back date
    rolled_back_date = most_recent_date - timedelta(days=days_to_roll_back)

    return rolled_back_date

def main():
    df = read_data("data_for_dash_full.csv")
    most_recent_date = max_date(df)
    with tab1:
        timelines = st.radio(label="Select a Time Window", options=["7 Days", "14 Days", "Lifetime"], horizontal=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if timelines == "7 Days":
                end_date = st.text_input(
                    "Start Date",
                    label_visibility="visible",
                    disabled=True,
                    placeholder=str(most_recent_date).split(' ')[0],
                )
                starting = roll_back_days(most_recent_date, 7)
                start_date = st.text_input(
                    "End Date",
                    label_visibility="visible",
                    disabled=True,
                    placeholder=str(starting).split(' ')[0],
                )
            elif timelines == "14 Days":
                end_date = st.text_input(
                    "Start Date",
                    label_visibility="visible",
                    disabled=True,
                    placeholder=str(most_recent_date).split(' ')[0],
                )
                
                starting = roll_back_days(most_recent_date, 14)
                start_date = st.text_input(
                    "End Date",
                    label_visibility="visible",
                    disabled=True,
                    placeholder=str(starting).split(' ')[0],
                )

            else:
                end_date = st.text_input(
                    "Start Date",
                    label_visibility="visible",
                    disabled=True,
                    placeholder=str(most_recent_date).split(' ')[0],
                )
                starting = df['ACTIVITY_DATE'].min()
                start_date = st.text_input(
                    "End Date",
                    label_visibility="visible",
                    disabled=True,
                    placeholder=str(starting).split(' ')[0],
                )
        df = df.loc[(df['ACTIVITY_DATE'] >= starting) & (df['ACTIVITY_DATE'] <= most_recent_date)]
        with col2:
            media_buyer = st.selectbox(
                'Select a media buyer',
                df["MEDIA_BUYER"].unique().tolist()
                )
            campaign = st.selectbox(
                'Select a campaign',
                df["CAMPAIGN"].unique().tolist()
                )
        df = df.loc[df['MEDIA_BUYER'] == media_buyer]
        df = df.loc[df['CAMPAIGN'] == campaign]
        with col3:
            active_days = st.number_input('Active within (days)', min_value=1, step=1)
    st.dataframe(df)

    # daily_return = st.button(":grey[DAILY_RETURN]", use_container_width=True, type='primary')
    # total_return = st.button(":grey[TOTAL_RETURN]", use_container_width=True, type='primary')
    # daily_profit = st.button(":grey[DAILY_PROFIT]", use_container_width=True, type='primary')
    # total_profit = st.button(":grey[TOTAL_PROFIT]", use_container_width=True, type='primary')
    # spend_revenue = st.button(":grey[SPEND_REVENUE]", use_container_width=True, type='primary')
    # arrivals = st.button(":grey[SPEND_PER_ARRIVAL, REVENUE_PER_ARRIVAL, PROFIT_PER_ARRIVAL]", use_container_width=True, type='primary')
    # acceptance_rate = st.button(":grey[ACCEPTANCE_RATE]", use_container_width=True, type='primary')


    
if __name__ == "__main__":
    main()