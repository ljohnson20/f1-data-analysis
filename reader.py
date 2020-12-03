import os
import pandas as pd

def import_all():
    data = {}
    for dirname, _, filenames in os.walk('data/ergast'):
        for filename in filenames:
            name = filename.replace('.csv', '')
            data[name] = pd.read_csv(os.path.join(dirname, filename))
            
    return data


def add_ids(data, key):
    
    df = data[key]
    n_lines = df.shape[0]

    df = pd.merge(df, data['races'][['raceId', 'year', 'round', 'circuitId', 'date', 'time']], 
                  on='raceId', how='left')
    if df.shape[0] != n_lines:
        raise ValueError('Merging raceId went wrong')
        
    df = pd.merge(df, data['circuits'][['circuitId', 'circuitRef', 'location', 'country']], 
                  on='circuitId', how='left')
    if df.shape[0] != n_lines:
        raise ValueError('Merging circuitId went wrong')
        
    df = pd.merge(df, data['drivers'][['driverId', 'driverRef', 'forename', 'surname', 
                                       'dob', 'nationality']].rename(columns={'nationality': 'drv_nat'}), 
                  on='driverId', how='left')
    if df.shape[0] != n_lines:
        raise ValueError('Merging driverId went wrong')
    
    if (key != 'lap_times') and (key != 'pit_stops'):
        df = pd.merge(df, data['constructors'][['constructorId', 'constructorRef', 
                                                'name', 'nationality']].rename(columns={'nationality': 'cstr_nat'}), 
                      on='constructorId', how='left')
        if df.shape[0] != n_lines:
            raise ValueError('Merging constructorId went wrong')
        
    if key == 'results':
        df = pd.merge(df, data['status'], 
                      on='statusId', how='left')
        if df.shape[0] != n_lines:
            raise ValueError('Merging statusId went wrong')
        
    return df

data = import_all()
res = add_ids(data, 'results')
qual = add_ids(data, 'qualifying')
laps = add_ids(data, 'lap_times')
pits = add_ids(data, 'pit_stops')

print(res.info())
retires = res.loc[(res['year'] >= 2019) & (res['status'] != 'Finished') & (~res['status'].str.contains("Lap"))]
print(retires[['number', 'surname']].value_counts())

offences = pd.read_csv('data/fia/driver_offence.csv')
print(offences.info())
print(offences)
print(offences['surname'].value_counts())
