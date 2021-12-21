import pandas as pd
# Output display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 3)

# Read the csvs
sample1 = pd.read_csv('sample1.csv')#, skipinitialspace=True)
sample2 = pd.read_csv('sample2.csv')#, skipinitialspace=True)
# Drop empty rows
sample1.dropna(inplace=True)
sample2.dropna(inplace=True)

# Break the R.T column into two
sample1[['RTX', 'RTY']] = sample1['R.T. (s)'].str.split(
    ' , ', expand=True)
sample2[['RTX', 'RTY']] = sample2['R.T. (s)'].str.split(
    ' , ', expand=True)

# Create regex pattern and filter
pattern = r'Unknown.*|.*siloxan.*|Silanediol.*|Oxime.*|Carbon dioxide|Ethanol'
filter1 = sample1['Name'].str.contains(pattern)
filter2 = sample2['Name'].str.contains(pattern)

# Merge the two datasets on 'Name', filtered out (~)
merged = pd.merge(sample1[~filter1], sample2[~filter2], how='inner', on='Name')

# Create format string
format_merged_noscore = ['Peak #_x', 'Peak #_y', 'Name', 'Retention Index_x', 'Retention Index_y', 'UniqueMass_x', 'UniqueMass_y', 'RTX_x', 'RTY_x', 'RTX_y', 'RTY_y', 'Area_x', 'Area_y' ]
format_merged = ['Peak #_x', 'Peak #_y', 'score', 'Name', 'Retention Index_x', 'Retention Index_y', 'UniqueMass_x', 'UniqueMass_y', 'RTX_x', 'RTY_x', 'RTX_y', 'RTY_y', 'Area_x', 'Area_y' ]
# Change column types
merged['RTX_x'] = merged['RTX_x'].astype(float)
merged['RTX_y'] = merged['RTX_y'].astype(float)
merged['RTY_x'] = merged['RTY_x'].astype(float)
merged['RTY_y'] = merged['RTY_y'].astype(float)
merged['UniqueMass_x'] = merged['UniqueMass_x'].astype(float)
merged['UniqueMass_y'] = merged['UniqueMass_y'].astype(float)

# Divide value in first sample by value in second sample (always divide smallest by biggest), then multiply for a "relevance factor"
scored = merged.assign(score=lambda x: 
    x[['RTX_x', 'RTX_y']].min(axis=1)/x[['RTX_x', 'RTX_y']].max(axis=1) * 1 +
    x[['RTY_x', 'RTY_y']].min(axis=1)/x[['RTY_x', 'RTY_y']].max(axis=1) * 1 +
    x[['Retention Index_x', 'Retention Index_y']].min(axis=1)/x[['Retention Index_x', 'Retention Index_y']].max(axis=1) * 1 +
    x[['UniqueMass_x', 'UniqueMass_y']].min(axis=1)/x[['UniqueMass_x', 'UniqueMass_y']].max(axis=1) * 0.8
)

# Group by Name, pick only the row with the biggest score for each Name
grouped = scored.groupby('Name')
scored.iloc[grouped['score'].agg(pd.Series.idxmax)][format_merged].to_csv('output.csv')