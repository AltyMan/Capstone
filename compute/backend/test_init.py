import random
from objects.user import User
import pandas as pd
from objects.rule import Rule
from services.habitscheduler import HabitScheduler

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
    
    res = query_habit(user.id, habits[0])

def habit_test_3():
    
    sc = HabitScheduler()
    sc.start()
    sc.restore_jobs()
    sc.print_active_jobs(User(1).id)
    
    User(1).repo.drop_all_rules()
        
    for i in range(0, 5):
        user: User = User(i)
        user.repo.generate_rules()
        user.repo.drop_dead_rules()
    