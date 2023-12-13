import pandas as pd
from datetime import datetime, timedelta

def process_activity_date_columns(df):
    """
    Process the 'ACTIVITY_DATE' column in a DataFrame to extract year, month, and day.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the 'ACTIVITY_DATE' column.

    Returns:
    - pd.DataFrame: The DataFrame with additional columns 'ACTIVITY_YEAR', 'ACTIVITY_MONTH', and 'ACTIVITY_DAY'.
    """
    # Convert 'ACTIVITY_DATE' to datetime
    df["ACTIVITY_DATE"] = pd.to_datetime(df["ACTIVITY_DATE"])

    # Extract year, month, and day into new columns
    df["ACTIVITY_YEAR"] = df["ACTIVITY_DATE"].dt.year
    df["ACTIVITY_MONTH"] = df["ACTIVITY_DATE"].dt.month
    df["ACTIVITY_DAY"] = df["ACTIVITY_DATE"].dt.day

    return df

def calculate_start_date(end_date, frequency):
    """
    Calculate the start date based on an end date and specified frequency.

    Parameters:
    - end_date (str): The end date in 'YYYY-MM-DD' format.
    - frequency (str): The frequency to roll back to. Supported values are 'weekly', 'monthly', or 'yearly'.

    Returns:
    - str: The calculated start date in 'YYYY-MM-DD' format.
    """
    # Convert end_date to datetime object
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Calculate start_date based on frequency
    if frequency == 'weekly':
        start_date = end_date - timedelta(weeks=1)
    elif frequency == 'monthly':
        # Subtracting a month can be tricky due to varying days in each month
        # This approach subtracts 30 days, which is a common approximation
        start_date = end_date - timedelta(days=30)
    elif frequency == 'yearly':
        start_date = end_date - timedelta(days=365)
    else:
        raise ValueError("Invalid frequency. Supported values are 'weekly', 'monthly', or 'yearly'.")

    # Convert start_date back to string format
    start_date_str = start_date.strftime('%Y-%m-%d')

    return start_date_str

def generate_leaderboard(df, end_date, frequency=None):
    """
    Generate a leaderboard based on total profit for a selected time period.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing the data.
    - end_date (str): The end date of the desired time period in 'YYYY-MM-DD' format.
    - frequency (str, optional): The frequency to roll back to. Supported values are 'weekly', 'monthly', or 'yearly'.
      If not provided, the function will use the entire available data.

    Returns:
    - pd.DataFrame: The generated leaderboard DataFrame.
    """
    # If frequency is provided, calculate start_date using calculate_start_date
    if frequency:
        start_date = calculate_start_date(end_date, frequency)
    else:
        # If frequency is not provided, use the entire available data
        start_date = df['ACTIVITY_DATE'].min()

    # Filter DataFrame for the selected time period
    selected_period_df = df[(df['ACTIVITY_DATE'] >= start_date) & (df['ACTIVITY_DATE'] <= end_date)]

    # Group by 'media_buyer' and calculate total profit for each category buyer
    category_profit = selected_period_df.groupby('MEDIA_BUYER')['TOTAL_PROFIT'].sum().reset_index()

    # Calculate overall sum of total profit for percentage calculation
    overall_sum = category_profit['TOTAL_PROFIT'].sum()

    # Calculate percentage and rank
    category_profit['PERCENTAGE'] = round((category_profit['TOTAL_PROFIT'] / overall_sum) * 100, 2)
    category_profit['RANKING'] = category_profit['TOTAL_PROFIT'].rank(ascending=False, method='dense').astype(int)

    # Rename columns for clarity
    category_profit = category_profit.rename(columns={'TOTAL_PROFIT': 'DOLLAR_AMOUNT'})
    category_profit = category_profit.rename(columns={'MEDIA_BUYER': 'NAME'})

    # Round 'DOLLAR_AMOUNT' to two decimal places
    category_profit['DOLLAR_AMOUNT'] = category_profit['DOLLAR_AMOUNT'].round(2)

    # Sort the leaderboard by total profit in descending order
    category_profit = category_profit.sort_values(by='DOLLAR_AMOUNT', ascending=False)

    # Reset index to be ordered regardless of the ranking
    category_profit = category_profit.reset_index(drop=True)

    return category_profit
