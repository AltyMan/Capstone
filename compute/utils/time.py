def fix_time(minutes: int) -> str:
    if minutes < 10:
            minutes = "0"+str(minutes)
    else:
        str(minutes)
            
    return minutes
