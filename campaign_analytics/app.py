import streamlit as st
import pandas as pd
import warnings
import plotly.express as px
from datetime import datetime
from features.database import *
from features.leaderboard import *
from features.image_search import *
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

# Set application screens
tab1, tab2, tab3 = st.tabs(["Campaign Stats", "Leaderboard", "Image Search"])

# Set up Google Images Search API credentials
GCS_DEVELOPER_KEY = "YOUR_GOOGLE_CLOUD_API_KEY"
GCS_CX = "85e8759d62c1e48d5"

gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

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
    df = read_data("input_data/data_year2023.csv")

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

    with tab2:
        # Split the layout into three columns
        col4, col5, col6 = st.columns(3)
        
        # Create a radio button to select a time window
        with col4:
            leaderboard_timelines = st.radio(label="Select a Time Window", options=["weekly", "monthly", "yearly"], horizontal=True)
        
        # Create visualization options in the sidebar
        with st.sidebar:
            st.title("Visualize Leaderboard")
            col7, col8 = st.columns(2)
            
            # Visualization checkboxes
            with col7:
                pie_chart = st.checkbox("Pie chart")
                vertical_bar_chart = st.checkbox("Vertical Bar chart")
            with col8:
                line_chart = st.checkbox("Line chart")
                horizontal_bar_chart = st.checkbox("Horizontal Bar chart")

        # Read and preprocess data
        leaderboard_df = process_activity_date_columns(pd.read_csv("input_data/data_year2023.csv"))
        
        # Get end date from user input
        with col4:
            end_date_leaderboard = st.date_input("End date", leaderboard_df["ACTIVITY_DATE"].max())

        # Generate leaderboard based on selected time window
        leaderboard = generate_leaderboard(leaderboard_df, str(end_date_leaderboard), leaderboard_timelines)

        # Toggle to show/hide the leaderboard
        show_leaderboard = st.toggle('Show Leaderboard')
        
        # Display the leaderboard if toggled on
        if show_leaderboard:
            st.dataframe(leaderboard,
                        column_order=("RANKING", "NAME", "DOLLAR_AMOUNT", "PERCENTAGE"),
                        height=200,
                        use_container_width=False,
                        hide_index=True
                        )
        # Plotly Charts based on user selections
        if pie_chart:
            # Create a Pie Chart using the 'Percentage' column
            fig_pie_percentage = px.pie(leaderboard, names='NAME', values='DOLLAR_AMOUNT', title='Pie Chart (Percentage)')
            fig_pie_percentage.update_layout(height=600, width=800)
            st.plotly_chart(fig_pie_percentage, use_container_width=True, theme=None)

        if vertical_bar_chart:
            # Create a Vertical Bar Chart
            fig_vertical_bar = px.bar(leaderboard, x='NAME', y='DOLLAR_AMOUNT', title='Vertical Bar Chart')
            fig_vertical_bar.update_layout(xaxis_title="Name", yaxis_title="Amount [USD]",height=600, width=800)
            st.plotly_chart(fig_vertical_bar, use_container_width=True, theme=None)
        
        if horizontal_bar_chart:
            # Create a Horizontal Bar Chart
            fig_horizontal_bar = px.bar(leaderboard.sort_values(by="DOLLAR_AMOUNT",ascending=True), 
                                        x='DOLLAR_AMOUNT', y='NAME', orientation='h', title='Horizontal Bar Chart')
            fig_horizontal_bar.update_layout(xaxis_title="Amount [USD]", yaxis_title="Name",height=600, width=800)
            st.plotly_chart(fig_horizontal_bar, use_container_width=True, theme=None)

        if line_chart:
            # Create a Line Chart
            fig_line = px.line(leaderboard, x='NAME', y='PERCENTAGE', title='Line Chart')
            fig_line.update_layout(xaxis_title="Name", yaxis_title="Percentage",height=600, width=800)
            st.plotly_chart(fig_line, use_container_width=True, theme=None)

    with tab3:
        # Set the title of the Streamlit app
        st.title("Image Search and Download")

        # Take user input for image search query
        query = st.text_input("Enter your image search query:")

        # Check if the "Search" button is clicked
        if st.button("Search"):
            # Prepare parameters for Google Images Search
            search_params = {
                'q': query,
                'num': 5,  # Number of images to retrieve
                'safe': 'off',  # Disable safe search
            }

            # Perform Google Images Search
            gis.search(search_params=search_params)

            # Display images in the search results
            for image in gis.results():
                # Get the URL and description of the image
                image_url, image_description = display_image(image)

                # Display the image with its caption
                st.image(image_url, caption=image_description, use_column_width=True)

                # Check if the "Download" button is clicked for the current image
                if st.button("Download"):
                    # Download the image
                    img = download_image(image)

                    # Prompt the user to choose where to save the image
                    file_path = st.file_uploader("Choose where to save the image:", type="png")

                    # Check if the user has chosen a file path
                    if file_path:
                        # Save the image to the specified file path
                        img.save(file_path, "PNG")
                        st.success(f"Image saved to {file_path}")

if __name__ == "__main__":
    main()