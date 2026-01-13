# config.py
import logging

DEBUG = True
DATA_FORMAT = "timestamp,habit,state,is_device,self_reported\n"
DATEMATCH = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

logging.basicConfig(filename="data/general.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

#from apscheduler.schedulers.background import BackgroundScheduler

#scheduler = BackgroundScheduler(timezone="EST")
#scheduler.start()