import pandas as pd
from datetime import timedelta, datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

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
