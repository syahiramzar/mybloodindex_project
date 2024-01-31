import pandas as pd
from datetime import datetime
import requests
from io import StringIO
import seaborn as sns

def myblood_etl():
    # extract data from MOH GitHub repo
    github_urls = [
        'https://github.com/MoH-Malaysia/data-darah-public/blob/main/donations_state.csv?raw=true',
        'https://github.com/MoH-Malaysia/data-darah-public/blob/main/newdonors_state.csv?raw=true']

    parquet_file_path = 'https://dub.sh/ds-data-granular'

    # List to store DataFrames
    dataframes = []

    # Loop through the GitHub URLs
    for url in github_urls:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(StringIO(response.text))
            dataframes.append(df)
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")

    # naming dataframe for extracted data

    state_d_total = dataframes[0]  # total daily donations by state
    new_d_total = dataframes[1]  # total new donors by state
    granulated_total = pd.read_parquet(parquet_file_path)  # granulated data

    # dataframe 1 & 2: total daily donations in Malaysia and by states

    state_d_total['date'] = pd.to_datetime(state_d_total['date'], format='%Y-%m-%d')
    state_d_total['donations_returning'] = state_d_total['donations_regular'] + state_d_total['donations_irregular']
    cols = ['blood_a', 'blood_b', 'blood_o', 'blood_ab', 'location_centre', 'location_mobile', 'type_wholeblood',
            'type_apheresis_platelet', 'type_apheresis_plasma', 'type_other', 'social_civilian', 'social_student',
            'social_policearmy', 'donations_regular', 'donations_irregular']
    state_d_total.drop(cols, axis=1, inplace=True)

    donations_my = state_d_total.loc[state_d_total["state"] == 'Malaysia'].copy()  # Dataframe 1
    donations_my.to_csv('/home/ubuntu/refined_df/donations_my.csv', index=False)
    
    donations_state = state_d_total.loc[state_d_total["state"] != 'Malaysia'].copy()  # Dataframe 2
    donations_state['year'] = donations_state['date'].dt.year
    donations_state.to_csv('/home/ubuntu/refined_df/donations_state.csv', index=False)

    # dataframe 3 & 4:  total new donors in Malaysia and by states

    new_d_total['date'] = pd.to_datetime(new_d_total['date'], format='%Y-%m-%d')
    newdonor_my = new_d_total.loc[new_d_total["state"] == 'Malaysia'].copy()  # Dataframe 3
    newdonor_my.to_csv('/home/ubuntu/refined_df/newdonor_my.csv', index=False)

    newdonor_state = new_d_total.loc[new_d_total["state"] != 'Malaysia'].copy()  # Dataframe 4
    newdonor_state['year'] = newdonor_state['date'].dt.year
    newdonor_state.to_csv('/home/ubuntu/refined_df/newdonor_state.csv', index=False)

    # dataframe 5: unique donor information from visits

    granulated_total['visit_date'] = pd.to_datetime(granulated_total['visit_date'], format='%Y-%m-%d')
    granulated_total['current_age'] = datetime.now().year - granulated_total['birth_date']
    granulated_total['age_during_visit'] = granulated_total['visit_date'].dt.year - granulated_total['birth_date']

    # remove donors whose age 70 above and below 17 during visit
    donor_all_visits = granulated_total[
        (granulated_total['age_during_visit'] <= 70) & (granulated_total['age_during_visit'] >= 17)]  # Dataframe 5
    donor_all_visits.to_csv('/home/ubuntu/refined_df/donor_all_visits.csv', index=False)
    
    # Dataframe 6: returning donor information
    grp_id = donor_all_visits.groupby(by=["donor_id", "current_age"]).size().reset_index()  # temporary df
    grp_id.rename(columns={0: 'total_visits'}, inplace=True)
    grp_id.loc[grp_id['total_visits'] == 1, 'status'] = 'non-returning'
    grp_id.loc[grp_id['total_visits'] > 1, 'status'] = 'returning'
    first_visit = donor_all_visits.groupby('donor_id').first().reset_index()  # temporary df
    first_visit.rename(columns={'visit_date': 'first_visit_date', 'age_during_visit': 'age_first_visit'}, inplace=True)
    first_visit.drop(columns=['birth_date', 'current_age'], inplace=True)
    donor_visit_total = grp_id.merge(first_visit, on='donor_id')  # temporary df

    returning_donor = donor_visit_total[donor_visit_total["status"] == 'returning'].copy()  # Dataframe 6
    returning_donor.loc[returning_donor['age_first_visit'].between(17, 20), 'age_group_first_visit'] = '17-20'
    returning_donor.loc[returning_donor['age_first_visit'].between(21, 24), 'age_group_first_visit'] = '21-24'
    returning_donor.loc[returning_donor['age_first_visit'].between(25, 29), 'age_group_first_visit'] = '25-29'
    returning_donor.loc[returning_donor['age_first_visit'].between(30, 34), 'age_group_first_visit'] = '30-34'
    returning_donor.loc[returning_donor['age_first_visit'].between(35, 39), 'age_group_first_visit'] = '35-39'
    returning_donor.loc[returning_donor['age_first_visit'].between(40, 44), 'age_group_first_visit'] = '40-44'
    returning_donor.loc[returning_donor['age_first_visit'].between(45, 49), 'age_group_first_visit'] = '45-49'
    returning_donor.loc[returning_donor['age_first_visit'].between(50, 54), 'age_group_first_visit'] = '50-54'
    returning_donor.loc[returning_donor['age_first_visit'].between(55, 59), 'age_group_first_visit'] = '55-59'
    returning_donor.loc[returning_donor['age_first_visit'] >= 60, 'age_group_first_visit'] = '60 and above'
    returning_donor.loc[returning_donor['current_age'].between(17, 20), 'age_group_current'] = '17-20'
    returning_donor.loc[returning_donor['current_age'].between(21, 24), 'age_group_current'] = '21-24'
    returning_donor.loc[returning_donor['current_age'].between(25, 29), 'age_group_current'] = '25-29'
    returning_donor.loc[returning_donor['current_age'].between(30, 34), 'age_group_current'] = '30-34'
    returning_donor.loc[returning_donor['current_age'].between(35, 39), 'age_group_current'] = '35-39'
    returning_donor.loc[returning_donor['current_age'].between(40, 44), 'age_group_current'] = '40-44'
    returning_donor.loc[returning_donor['current_age'].between(45, 49), 'age_group_current'] = '45-49'
    returning_donor.loc[returning_donor['current_age'].between(50, 54), 'age_group_current'] = '50-54'
    returning_donor.loc[returning_donor['current_age'].between(55, 59), 'age_group_current'] = '55-59'
    returning_donor.loc[returning_donor['current_age'] >= 60, 'age_group_current'] = '60 and above'

    returning_donor.loc[returning_donor['total_visits'].between(0, 2), 'visit_freq'] = '2'
    returning_donor.loc[returning_donor['total_visits'].between(3, 5), 'visit_freq'] = '3-5'
    returning_donor.loc[returning_donor['total_visits'].between(6, 8), 'visit_freq'] = '6-8'
    returning_donor.loc[returning_donor['total_visits'].between(9, 11), 'visit_freq'] = '9-11'
    returning_donor.loc[returning_donor['total_visits'] >= 11, 'visit_freq'] = '11-higher' 
    
    returning_donor.to_csv('/home/ubuntu/refined_df/returning_donor.csv', index=False)