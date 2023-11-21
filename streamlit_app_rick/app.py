import streamlit as st
import pandas as pd
import warnings
import plotly.express as px
from datetime import timedelta, datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ignore warnings
warnings.filterwarnings('ignore')

# Configure Streamlit app settings
st.set_page_config(layout="wide",
                   page_title="Campaign Analytics",
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

Base = declarative_base()

# Define the Profile model
class Profile(Base):
    """
    SQLAlchemy model for the 'profiles' table.

    Attributes:
        id (int): Unique identifier for each profile.
        user_name (str): User name associated with the profile.
        profile_name (str): Name of the profile.
        settings (dict): JSON representation of profile settings.
        timestamp_UTC (datetime): Timestamp indicating when the profile was created (in UTC).

    Note:
        The 'timestamp_UTC' field is automatically populated with the current UTC time when a new profile is created.

    Example:
        To create a new profile instance:
        >>> profile = Profile(user_name='JohnDoe', profile_name='Default', settings={'option1': True, 'option2': 'value'})
    """

    __tablename__ = 'profiles'

    id = Column(Integer, unique=True, primary_key=True)
    user_name = Column(String)
    profile_name = Column(String)
    settings = Column(JSON)
    timestamp_UTC = Column(DateTime, default=datetime.utcnow)  # Default to the current UTC time

# Create an SQLAlchemy engine with a SQLite database file named 'user_presets.db' in the 'database' folder
engine = create_engine('sqlite:///database/user_presets.db')

# Create the database tables defined in the Base class (assuming Base is a declarative_base())
# and bind them to the engine
Base.metadata.create_all(bind=engine)

# Create a Session class bound to the engine
Session = sessionmaker(bind=engine)

tab1, tab2, tab3 = st.tabs(["Campaign Stats", "Page 3", "Page 4"])

@st.cache_data
def save_profile(user_name, profile_name, settings):
    """
    Save a user profile to the database.

    Args:
        user_name (str): User name associated with the profile.
        profile_name (str): Name of the profile.
        settings (dict): JSON representation of profile settings.

    Returns:
        None
    """
    # Create a new session
    session = Session()

    # Create a new profile instance with the provided parameters
    profile = Profile(
        user_name=user_name, 
        profile_name=profile_name, 
        settings=settings, 
        timestamp_UTC=datetime.utcnow()
        )

    # Add the profile to the session and commit the changes to the database
    session.add(profile)
    session.commit()

# @st.cache_data
def load_profile(user_name):
    """
    Load user profiles from the database for a specified user.

    Args:
        user_name (str): The user name for which profiles should be loaded.

    Returns:
        pd.DataFrame: A DataFrame containing profiles with columns 'user_name', 'profile_name', 'settings', and 'timestamp_UTC'.
    """
    # Create a new session
    session = Session()

    # Query the database to retrieve all profiles for the specified user
    profiles = session.query(Profile).filter_by(user_name=user_name).all()

    # Create a list of dictionaries containing 'user_name', 'profile_name', 'settings', and 'timestamp_UTC' for each profile
    profile_data = [
        {
            'user_name': user_name,
            'profile_name': profile.profile_name,
            'settings': profile.settings,
            'timestamp_UTC': profile.timestamp_UTC
        }
        for profile in profiles
    ]
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(profile_data)

    return df

@st.cache_data
def read_data(filepath):
    """
    Reads data from a CSV file and returns it as a DataFrame.

    Parameters:
    - file_path (str): The path to the CSV file.

    Returns:
    - pd.DataFrame: The loaded DataFrame.
    """
    df = pd.read_csv(filepath)
    df['ACTIVITY_DATE'] = pd.to_datetime(df['ACTIVITY_DATE'], format="%Y-%m-%d")
    # Return DatFrame with correct data type
    return df

@st.cache_data
def max_date(dataframe):
    """
    Finds and returns the maximum date in a DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing date information.

    Returns:
    - datetime: The maximum date.
    """
    # Return the most recent Date
    return dataframe['ACTIVITY_DATE'].max()

@st.cache_data
def roll_back_days(most_recent_date, days_to_roll_back):
    """
    Rolls back a given number of days from a provided date.

    Parameters:
    - most_recent_date (datetime): The most recent date.
    - days_to_roll_back (int): The number of days to roll back.

    Returns:
    - datetime: The rolled-back date.
    """
    # Calculate the rolled-back date
    rolled_back_date = most_recent_date - timedelta(days=days_to_roll_back)

    return rolled_back_date

def main():
    """
    Main function for interactive Streamlit dashboard.

    Reads data, allows user to select time window, media buyer, and campaign.
    Displays various metrics based on user selections using Plotly charts.
    """
    # Read csv data file
    df = read_data("data_for_dash_full.csv")

    # Create a copy of the df
    preset_df = df.copy()
    # Get the most recent date from the DataFrame using the max_date function
    most_recent_date = max_date(df)

    # Use Streamlit to create a radio button for selecting a time window
    # and three columns for organizing input elements
    with tab1:
        # Create a radio button to select a time window
        timelines = st.radio(label="Select a Time Window", options=["7 Days", "14 Days", "Lifetime"], horizontal=True)
        
        # Split the layout into three columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # If the selected time window is "7 Days"
            if timelines == "7 Days":
                # Create a text input for the start date
                end_date_main = st.date_input("Start Date", most_recent_date)
                
                # Calculate the starting date by rolling back 7 days from the most recent date
                starting = roll_back_days(most_recent_date, 7)
                
                # Create a text input for the end date
                start_date_main = st.date_input("End Date", starting)
                
            # If the selected time window is "14 Days"
            elif timelines == "14 Days":
                # Create a text input for the start date
                end_date_main = st.date_input("Start Date", most_recent_date)
                
                # Calculate the starting date by rolling back 14 days from the most recent date
                starting = roll_back_days(most_recent_date, 14)
                
                # Create a text input for the end date
                start_date_main = st.date_input("End Date", starting)

            # If the selected time window is "Lifetime"
            else:
                # Create a text input for the start date
                end_date_main = st.date_input("Start Date", most_recent_date)
                
                # Set the starting date as the minimum date in the DataFrame's 'ACTIVITY_DATE' column
                starting = df['ACTIVITY_DATE'].min()
                
                # Create a text input for the end date
                start_date_main = st.date_input("End Date", starting)

            # Filter the DataFrame to include only rows within the selected time window
            df = df.loc[(df['ACTIVITY_DATE'] >= starting) & (df['ACTIVITY_DATE'] <= most_recent_date)]

            # if end_date_main and start_date_main:
            #     df = df.loc[(df['ACTIVITY_DATE'] >= start_date_main) & (df['ACTIVITY_DATE'] <= end_date_main)]

        # Within the second column
        with col2:
            # Create a selectbox for choosing a media buyer
            media_buyer = st.selectbox(
                'Select a media buyer',
                df["MEDIA_BUYER"].unique().tolist()
            )
            
            # Filter the DataFrame to include only rows where 'MEDIA_BUYER' matches the selected media buyer
            df = df[df['MEDIA_BUYER'] == media_buyer]

        # Within the third column
        with col3:
            # Create a number input for specifying the number of active days
            active_days = st.number_input('Active within (days)', min_value=1, step=1, value=15)
        if active_days:
            with col2:
                end_date = datetime.today()
                start_date = roll_back_days(end_date,  active_days)
                df = df[df['ACTIVITY_DATE'].between(start_date, end_date)]
                campaign = st.selectbox(
                    'Select a campaign',
                    df['CAMPAIGN'].unique().tolist()
                )
                df = df[df['CAMPAIGN'] == campaign]
        else:
            with col2:
                # Create a selectbox for choosing a campaign
                campaign = st.selectbox(
                        'Select a campaign',
                        df["CAMPAIGN"].unique().tolist()
                    )
                df = df[df['CAMPAIGN'] == campaign]

        # Calculate the sum of daily return for each activity date
        daily_return = pd.DataFrame(df.groupby("ACTIVITY_DATE")["DAILY_RETURN"].sum())
        
        # Create a line chart using Plotly Express
        daily_return_fig = px.line(data_frame=daily_return,
            x=daily_return.index,
            y="DAILY_RETURN",
            title=f"Daily Return over the last {timelines}"
        )
        
        # Customize chart layout
        daily_return_fig.update_layout(xaxis_title="Time Period", yaxis_title="Daily Return", height=600, width=800)
        
        # Display the chart using Streamlit
        st.plotly_chart(daily_return_fig, use_container_width=True, theme=None)

        # Calculate the sum of total return for each activity date
        total_return = pd.DataFrame(df.groupby("ACTIVITY_DATE")["TOTAL_RETURN"].sum())

        # Create a line chart using Plotly Express
        total_return_fig = px.line(data_frame=total_return,
            x=total_return.index,
            y="TOTAL_RETURN",
            title=f"Total Return over the last {timelines}"
            )
        
        # Customize chart layout
        total_return_fig.update_layout(xaxis_title="Time Period", yaxis_title="Total Return",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(total_return_fig, use_container_width=True, theme=None)

        # Calculate the sum of daily profit for each activity date
        daily_profit = pd.DataFrame(df.groupby("ACTIVITY_DATE")["DAILY_PROFIT"].sum())

        # Create a line chart using Plotly Express
        daily_profit_fig = px.line(data_frame=daily_profit,
            x=daily_profit.index,
            y="DAILY_PROFIT",
            title=f"Daily Profit over the last {timelines}"
            )
        
        # Customize chart layout
        daily_profit_fig.update_layout(xaxis_title="Time Period", yaxis_title="Daily Profit",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(daily_profit_fig, use_container_width=True, theme=None)

        # Calculate the sum of total profit for each activity date
        total_profit = pd.DataFrame(df.groupby("ACTIVITY_DATE")["TOTAL_PROFIT"].sum())

        # Create a line chart using Plotly Express
        total_profit_fig = px.line(data_frame=total_profit,
            x=total_profit.index,
            y="TOTAL_PROFIT",
            title=f"Total Profit over the last {timelines}"
            )
        
        # Customize chart layout
        total_profit_fig.update_layout(xaxis_title="Time Period", yaxis_title="Total Profit",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(total_profit_fig, use_container_width=True, theme=None)

        # Calculate the sum of spend for each activity date
        df_spend = pd.DataFrame(df.groupby("ACTIVITY_DATE")["SPEND"].sum())

        # Calculate the sum of revenue for each activity date
        df_revenue = pd.DataFrame(df.groupby("ACTIVITY_DATE")["REVENUE"].sum())

        # Create a line chart using Plotly Express
        fig_spend = px.line(data_frame=df_spend,
            x=df_spend.index,
            y="SPEND",
            title=f"Spend over the last {timelines}"
            )
        
        # Customize chart layout
        fig_spend.update_layout(xaxis_title="Time Period", yaxis_title="Spend",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(fig_spend, use_container_width=True, theme=None)

        # Create a line chart using Plotly Express
        fig_revenue = px.line(data_frame=df_revenue,
            x=df_revenue.index,
            y="REVENUE",
            title=f"Revenue over the last {timelines}"
            )
        
        # Customize chart layout
        fig_revenue.update_layout(xaxis_title="Time Period", yaxis_title="Revenue",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(fig_revenue, use_container_width=True, theme=None)
        
        # Calculate the sum of spend per arrival for each activity date
        df_spend_arr = pd.DataFrame(df.groupby("ACTIVITY_DATE")["SPEND_PER_ARRIVAL"].sum())

        # Calculate the sum of revenue per arrival for each activity date
        df_revenue_arr = pd.DataFrame(df.groupby("ACTIVITY_DATE")["REVENUE_PER_ARRIVAL"].sum())

        # Calculate the sum of profit per arrival for each activity date
        df_profit_arr = pd.DataFrame(df.groupby("ACTIVITY_DATE")["PROFIT_PER_ARRIVAL"].sum())

        # Create a line chart using Plotly Express
        fig_spend_arr = px.line(data_frame=df_spend_arr,
            x=df_spend_arr.index,
            y="SPEND_PER_ARRIVAL",
            title=f"Spend Per Arrival over the last {timelines}"
            )
        
        # Customize chart layout
        fig_spend_arr.update_layout(xaxis_title="Time Period", yaxis_title="Spend Per Arrival",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(fig_spend_arr, use_container_width=True, theme=None)

        # Create a line chart using Plotly Express
        fig_revenue_arr = px.line(data_frame=df_revenue_arr,
            x=df_revenue_arr.index,
            y="REVENUE_PER_ARRIVAL",
            title=f"Revenue Per Arrival over the last {timelines}"
            )
        
        # Customize chart layout
        fig_revenue_arr.update_layout(xaxis_title="Time Period", yaxis_title="Revenue Per Arrival",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(fig_revenue_arr, use_container_width=True, theme=None)

        # Create a line chart using Plotly Express
        fig_profit_arr = px.line(data_frame=df_profit_arr,
            x=df_profit_arr.index,
            y="PROFIT_PER_ARRIVAL",
            title=f"Profit Per Arrival over the last {timelines}"
            )
        
        # Customize chart layout
        fig_profit_arr.update_layout(xaxis_title="Time Period", yaxis_title="Profit Per Arrival",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(fig_profit_arr, use_container_width=True, theme=None)

        # Calculate the sum of acceptance rate for each activity date
        acceptance_rate = pd.DataFrame(df.groupby("ACTIVITY_DATE")["ACCEPTANCE_RATE"].sum())

        # Create a line chart using Plotly Express
        acceptance_rate_fig = px.line(data_frame=acceptance_rate,
            x=acceptance_rate.index,
            y="ACCEPTANCE_RATE",
            title=f"Acceptance Rate over the last {timelines}"
            )
        
        # Customize chart layout
        acceptance_rate_fig.update_layout(xaxis_title="Time Period", yaxis_title="Acceptance Rate",height=600, width=800)

        # Display the chart using Streamlit
        st.plotly_chart(acceptance_rate_fig, use_container_width=True, theme=None)

        # Create sidebar with save settings and load presets - Indent every line of code after `with st.sidebar`
        # Display the Save Profile section in the sidebar
        with st.sidebar:
            # Display Current Settings
            st.header("Current Settings")
            st.info(f"Time window: {timelines}") 
            st.info(f"Start Date: {str(end_date_main).split(' ')[0].replace('-', '/')}") # Format for conformity with streamlit date input
            st.info(f"End Date: {str(start_date_main).split(' ')[0].replace('-', '/')}") # Format for conformity with streamlit date input
            st.info(f"Media buyer: {media_buyer}")
            st.info(f"Active within (days): {active_days}")
            st.info(f"Campaign: {campaign}")

            st.header("Save Current Settings")

            # Prompt for user name
            user_name = st.selectbox(
                'Select a user:',
                preset_df['MEDIA_BUYER'].unique().tolist()
            )

            # Prompt for profile name
            profile_name = st.text_input("Enter a new profile name:")

            # Create a settings dictionary
            settings = {
                "time_line": timelines,
                "start_date": str(end_date_main),
                "end_date": str(start_date_main),
                "media_buyer": media_buyer,
                "active_days": active_days,
                "campaign": campaign
            }

            # Save button to save the current settings
            save_preset = st.button("Save Settings")

            if save_preset:
                save_profile(user_name, profile_name, settings)
                st.success(f"Settings for {user_name} saved!")


            # Display Saved Settings
            st.header("Load Saved Settings")

            # Prompt for user to select
            user = st.selectbox(
                'User:',
                preset_df['MEDIA_BUYER'].unique().tolist()
            )
            if user:
                # Load profiles for the selected user
                settings_df = load_profile(user_name=user)

            # Prompt for profile name
            profile_df = settings_df[settings_df["user_name"]==user]
            settings_profile = st.selectbox(
                'Saved settings:',
                profile_df['profile_name'].tolist()
            )

            if settings_profile:
                # Retrieve saved settings for the selected profile
                saved_settings = settings_df[
                    (settings_df["user_name"]==user) & (settings_df["profile_name"]==settings_profile)
                ]['settings']
                result_dict = saved_settings.values[0]

            # Display saved settings
            st.info(f"Time window: {result_dict['time_line']}") 
            st.info(f"Start Date: {result_dict['start_date'].split(' ')[0].replace('-', '/')}") # Format for conformity with streamlit date input
            st.info(f"End Date: {result_dict['end_date'].split(' ')[0].replace('-', '/')}") # Format for conformity with streamlit date input
            st.info(f"Media buyer: {result_dict['media_buyer']}")
            st.info(f"Active within (days): {result_dict['active_days']}")
            st.info(f"Campaign: {result_dict['campaign']}")

if __name__ == "__main__":
    main()