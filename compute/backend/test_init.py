import random
from objects.user import User
import pandas as pd
from objects.rule import Rule
from db.sqlite import query_habit, HabitQueryResult

def habit_test():
    return       
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
    return
    habits = ['Gaming', 'Cooking']
    
    user = User(None, habits)
    user._log_user_habit(habits[0])
    print(user._get_user_habits())
    USERS[user.id] = user
    
    res: HabitQueryResult = query_habit(user.id, habits[0])

def habit_test_3():
    user: User = User.create()
    user.add_habit('Gaming')
    user.log_habit('Gaming')
    user.add_rule(1,Rule(1,1,1,1))
    print(user.get_habit_logs())
    

    