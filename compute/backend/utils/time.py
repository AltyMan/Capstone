from pandas import DataFrame, to_datetime
from datetime import datetime

def fix_time(minutes: int) -> str:
    if minutes < 10:
            minutes = "0"+str(minutes)
    else:
        str(minutes)
            
    return minutes

def break_timestamp(df: DataFrame) -> DataFrame:
        df['timestamp'] = to_datetime(df['timestamp'])
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['second'] = df['timestamp'].dt.second
        df = df.drop('timestamp', axis=1)
        return df
    
def _timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")