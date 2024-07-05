#!/usr/bin python3

import requests
import pandas as pd
import toml 
import subprocess
from datetime import datetime
import os 

def check_url_status(url):
    try:
        response = requests.get(url)
        # Check if the status code is 200 (OK)
        if response.status_code == 200:
            # Handle the success case
            print("Success:", response.status_code)
            # Process the response content if needed
            content = response.content
            # Process content...
        else:
            # Handle other status codes
            print("Received a different status code:", response.status_code)
            # You can add more specific handling for different status codes if needed
    except requests.exceptions.RequestException as e:
        if response.status_code[0] == 4:
             print("An error occurred:", e)
             print("This is a client Error")
        if response.status_code[0] == 5:
            print("An error occurred:", e)
            print("This is a server Error")


def read_api(url):
    """
    supply a url from API to return a base json payload
    """
    print('reading api')
    dataload = requests.get(url = url)
    print('returning api as json')
    return dataload.json()


print(os.getcwd())

if __name__=='__main__':
    app_config = toml.load(os.getcwd()+'/config.toml')
    count = 50
    url = app_config['api']['url']+str(count)

    check_url_status(url)
    load = read_api(url=url)

    locations_df = pd.json_normalize(load['results'], record_path=['locations'], meta=['name', 'type', 'publication_date', 'id'], record_prefix='location_')
    locations_df2 = pd.json_normalize(load['results'])[['company.name','id']]

    df = pd.merge(locations_df, locations_df2, on = 'id')

    df = df.rename(columns={
        'company.name':'company_name',
        'location_name':'location',
        'type':'job_type',
        'name':'job'
    })

    df['publication_date'] = pd.to_datetime(df['publication_date']).dt.date
    df[['city','country']] = df['location'].str.split(r', | /', n=1,expand=True,regex=True)
    df_final = df.drop(['id','location'], axis =1).loc[:,['publication_date','job_type', 'job', 'company_name', 'city','country']]

    output_path = os.environ['OUTPUT_FOLDER']
    timestamp = datetime.now()
    final_path = output_path+f'/{timestamp.strftime("%Y_%m_%d_%H:%M:%S")}_final.csv'

    print(df_final.shape)
    print('saving df to csv file')
    df_final.to_csv(final_path,index=False)
    
    if os.path.isfile(final_path):
        subprocess.run(['aws','s3','cp',final_path,f's3://py-project-pull/input'+f'/{timestamp.strftime("%Y_%m_%d_%H:%M:%S")}_final.csv'])
        print('success')
    else:
        print('Error something went wrong')