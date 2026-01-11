from services.users import USERS
import random
from models.user import User
import pandas as pd

def habit_test():       
    TEST_DATA = "habit_data.csv"
    
    habit_cols = sorted(pd.read_csv(TEST_DATA)['habit'].unique())
    user = User(TEST_DATA, habit_cols)
    user._log_user_habit(random.choice(habit_cols))
    #user.user_habits[0].schedule_habit(1)
    USERS[user.id] = user
    
    print(user.print_user_mqtt_topics())
    
    habit_cols = sorted(pd.read_csv(TEST_DATA)['habit'].unique())
    user = User(TEST_DATA, habit_cols)
    user._log_user_habit(random.choice(habit_cols))
    USERS[user.id] = user
    
    print(user.print_user_mqtt_topics())
    
def habit_test_2():
    habits = ['Gaming', 'Cooking']
    
    user = User(None, habits)
    user._log_user_habit(habits[0])
    print(user._get_user_habits())
    USERS[user.id] = user