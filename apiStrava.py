
import requests
import urllib3
import pandas as pd
from pandas.io.json import json_normalize
import seaborn as sns
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"


payload = {
    'client_id': "76418",
    'client_secret': '0ff5f11c39f57c39f4ad64bd769136881739ec73',
    'refresh_token': '579f760be58c4af05724cfe57544d93510d1bb5d',
    'grant_type': "refresh_token",
    'f': 'json'
}


print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}\n".format(access_token))

header = {'Authorization': 'Bearer ' + access_token}
param = {'per_page': 200, 'page': 1}
my_dataset = requests.get(activites_url, headers=header, params=param).json()



activities = json_normalize(my_dataset)
#print(activities)

#info metrics
metrics = ['name', 'upload_id', 'type', 'distance', 'moving_time',   
         'average_speed', 'max_speed','total_elevation_gain',
         'start_date_local', 'elapsed_time', "average_cadence"
       ]

activities = activities[metrics]

#Break date into start time and date
activities['start_date_local'] = pd.to_datetime(activities['start_date_local'])
activities['start_time'] = activities['start_date_local'].dt.time
activities['start_date_local'] = activities['start_date_local'].dt.date

activities.head(5)
activities['type'].value_counts()




runs = activities.loc[activities['type'] == 'Run'] 
runs.head(5)
sns.set(style="ticks", context="talk")
sns.scatterplot(x='distance', y = 'average_speed', data = runs).set_title("Average Speed vs Distance")
sns.scatterplot(x='distance', y = 'max_speed', data = runs).set_title("Average Cadence vs Distance")


fig = plt.figure()
ax = fig.add_subplot(111)
x = np.asarray(runs.start_date_local)
y = np.asarray(runs.average_cadence)
ax.plot_date(x, y)
ax.set_title('Average Speed over Time')
fig.autofmt_xdate(rotation=45)
fig.tight_layout()
fig.savefig('avg_Speed.png')
fig = plt.figure()
ax1 = fig.add_subplot(111)
x = np.asarray(runs.start_date_local)
y = np.asarray(runs.average_speed)
ax1.plot_date(x, y)
ax1.set_title('Average Cadence over Time')
fig.autofmt_xdate(rotation=45)
fig.tight_layout()
fig.savefig('avg_Cad.png')



home_date= '2021-09-1' #date I flew home
home_date = datetime.strptime(home_date, '%Y-%m-%d').date()
runs['start_date_local'] = pd.to_datetime(runs['start_date_local']).dt.date
runs['uw'] = np.where(runs['start_date_local'] < home_date, 'true', 'false')


home = runs.loc[runs['uw'] == 'true']
uw = runs.loc[runs['uw'] == 'false']


home_speed = round(home['average_speed'].mean() * 3.6, 2)
uw_speed = round(uw['average_speed'].mean() * 3.6, 2)
home_max_speed = round(home['max_speed'].mean()* 3.6, 2)
uw_max_speed = round(uw['max_speed'].mean()* 3.6, 2)
print("Average Home Speed: " + str(home_speed) + " | Average Home Max Speed: " + str(home_max_speed) + '\n'
      + "Average Waterloo Speed: " + str(uw_speed) + " | Average Waterloo Max Speed: " + str(uw_max_speed))



percent_increase_average = round((uw_speed - home_speed) * 100 / uw_speed,2)
print(percent_increase_average)