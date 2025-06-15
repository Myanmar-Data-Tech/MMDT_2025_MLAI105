# data_cleaning.py
import pandas as pd
from fuzzywuzzy import process # type: ignore #fuzzy string matching to find similar text strings

def joint_data_set(df1, df2):
    merged_df = pd.concat([df1, df2], ignore_index=True)
   
    return merged_df
#This function combines two DataFrames vertically using pd.concat(). The ignore_index=True parameter resets the index to create a continuous sequence starting from 0.
def remove_duplicates(df):  
    return df.drop_duplicates()
#Removes duplicate rows from the DataFrame
def remove_missing_values(df):
    return df.dropna()
#Eliminates rows containing missing values (NaN) using the dropna() method.
def find_closest_match(row, mimu_SR_Name):
    matches = process.extractOne(row, mimu_SR_Name, score_cutoff=90)
    return matches[0]
#Uses process.extractOne() from fuzzywuzzy to find the best match
#Sets a score cutoff of 90, meaning only matches with 90% or higher similarity are considered
#Returns the matched string (the first element of the tuple returned by extractOne)

def data_cleaning(df_towns, df_villages, df_news):
    df_towns.columns = ['SR_Name', 'name']
    df_villages.columns = ['SR_Name', 'name']
    df_news.columns = ['SR_Name', 'name']
    #Standardizes column names across all three datasets to 'SR_Name' and 'name' for consistency
    
    df_towns['name'] = df_towns['name'].apply(lambda name: name.replace('Town', '').strip())
    #remove Town" from town names and strips whitespace to normalize the naming convention.
    df_mimu = joint_data_set(df_towns, df_villages)
    df_mimu = remove_missing_values(df_mimu)
    df_news = remove_duplicates(df_news)
    #Removes duplicate entries from the news dataset.
    mimu_SR_Name = df_mimu['SR_Name'].unique()
    df_news.loc[:, 'SR_Name']  = df_news['SR_Name'].apply(lambda x: find_closest_match(x, mimu_SR_Name))
    df_mimu = joint_data_set(df_mimu, df_news)
    #Extracts unique SR_Name values from the combined mimu dataset
    #Uses fuzzy matching to standardize SR_Name values in the news dataset against the mimu reference list
    #This helps resolve naming inconsistencies between datasets
    return df_mimu



def main():
    # Load data from files  
    df_towns = pd.read_excel('C:/Intro-to-Deep-Learning/chapter2/Project_02/data/MMNames_mimu.xlsx', sheet_name='Towns')
    df_villages = pd.read_excel('C:/Intro-to-Deep-Learning/chapter2/Project_02/data/MMNames_mimu.xlsx', sheet_name='Villages')
    df_news = pd.read_csv('C:/Intro-to-Deep-Learning/chapter2/Project_02/data/MMNames_news.csv')
    df_mimu = data_cleaning(df_towns, df_villages, df_news)

    # save the cleaned data
    df_mimu.to_csv('C:/Intro-to-Deep-Learning/chapter2/Project_02/data/MMNames_clean.csv', index=False)
    
if __name__ == "__main__":
    main()