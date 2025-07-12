import arcpy
import pandas as pd
import numpy as np
import itertools

proj = arcpy.mp.ArcGISProject('CURRENT')
m = proj.activeMap
PathDB = proj.defaultGeodatabase

arcpy.env.overwriteOutput = True
arcpy.env.workspace = proj.defaultGeodatabase
#################################################################Pathways############################################################################
path = r'\\tsclient\H\share\GIS Methods Group\TEA Dashboard'

data = r'{0}\RawData\TEA_Data.csv'.format(path)
shapefile = r'{0}\DistrictShapefile\Current_Districts.shp'.format(path)
cleandata = r'C:\Users\chenry\Documents\TEA\CleanData'
latlong = r'{0}\RawData\TCDistLatLong.csv'.format(path)

#################################################################Recodes############################################################################
#RACE
raceDic = {'WHI':'White',
        'HISP':'Hispanic',
        'BLA':'Black or African American',
        'ASI':'Asian',
        'TMR':'Two or More',
        'AIAN':'American Indian and Alaska Native',
        'PAI':'Pacific Islander'}

#SDs        
sdDic = {'ISSMT10':'In School Suspension > 10 days',
        'TDR':'Total Disciplinary Removal',
        'OSSELTE10':'Out of School Suspension or Expulsion <= 10 days',
        'OSSEMT10':'Out of School Suspension or expulsion  > 10 days',
        'ISSLTE10':'In School Suspension <= 10 days',
        'ID':'Intellectual Disability',
        'ED':'Emotional Disturbance',
        'REP':'All Disabilities',
        'AUT':'Autism',
        'OHI':'Other health Impairment',
        'SLI':'Speech/Language Impairment',
        'SLD':'Specific Learning Disability',
        'SS':'Separate Schools and Residential Facilities',
        'RCLT40':'Regular Class placement < 40%'}

#SD overall categories
sdLDic = {'ISSMT10':'Discipline',
        'TDR':'Discipline',
        'OSSELTE10':'Discipline',
        'OSSEMT10':'Discipline',
        'ISSLTE10':'Discipline',
        'ID':'Representation',
        'ED':'Representation',
        'REP':'Representation',
        'AUT':'Representation',
        'OHI':'Representation',
        'SLI':'Representation',
        'SLD':'Representation',
        'SS':'Placement',
        'RCLT40':'Placement'}

#################################################################Data############################################################################
df = pd.read_csv(data)

#Any mild data cleaning goes here
df['DISTNAME'] = np.where(df['DISTNAME'] == 'A W BROWN-FELLOWSHIP LEADERSHIP AC', 'A W BROWN LEADERSHIP ACADEMY', df['DISTNAME'] )

#pull out  the demos seprately for one file, and then SD vars in a second file
#we're going to fill in "missing" data, need a row for every year, indicator, eth combo for each district. 

#demos
df_dem = df.drop(columns = ['STATUS', 'ETHNICITY', 'INDICATOR', 'SDRR'])
df_dem = df_dem.drop_duplicates(keep = 'first')

demoConv = ['DPETBLAP',
            'DPETHISP',
            'DPETWHIP',
            'DPETINDP',
            'DPETASIP',
            'DPETPCIP',
            'DPETTWOP',
            'DPETECOP',
            'DPETLEPP',
            'DPETSPEP',
            'DPETBILP',
            'DPETVOCP',
            'DPETGIFP',
            'OIP',
            'OHIP',
            'AIP',
            'VIP',
            'DBP',
            'IDP',
            'EDP',
            'LDP',
            'SIP',
            'AUP',
            'DDP',
            'TBIP',
            'NCECP']

#convert all the percentages to proportions
for dc in demoConv:
    df_dem[dc] = df_dem[dc]/100

#SD data
df_SD = df[['STATUS', 'ETHNICITY', 'INDICATOR', 'SDRR', 'SDYEAR', 'DISTRICT']]


#create a df with each dist with each eth, ind, year
years = list(df_SD['SDYEAR'].unique())

df_list = pd.DataFrame()

for y in years:
    # a is [list of unique SD IDs for y, list of SDs, list of races]
    a = [list(df_SD.loc[df_SD['SDYEAR'] == y, 'DISTRICT'].unique()),list(sdDic), list(raceDic)]
    df_temp = pd.DataFrame(list(itertools.product(*a)), columns = ['DISTRICT','INDICATOR','ETHNICITY'])
    df_temp['SDYEAR'] = y
    df_list = df_list.append(df_temp)

df_master = df_list.merge(df_SD, on = ['DISTRICT', 'SDYEAR','ETHNICITY', 'INDICATOR'] , how = 'left', validate = "1:1")
df_master = df_master.merge(df_dem, on = ['DISTRICT', 'SDYEAR'], how = 'left', validate = "m:1")

#recode race and indicators into label variables, etc. 

df_master['eth_label'] = df_master['ETHNICITY'].map(raceDic)
df_master['sd_label'] = df_master['INDICATOR'].map(sdDic)
df_master['sd_category'] = df_master['INDICATOR'].map(sdLDic)

#The date for the charts will include ALL district, year, etc. combos
df_master.to_csv(r'{0}\Table_ChartData.csv'.format(cleandata))

#We're only going to map districts with SD, so filter out those without
df_map = df_master.loc[df_master['SDRR'].isna()== False]


#################################################################Mapping############################################################################
#We need to split up districts that are part of the distirct shapefile and those that aren't
arr = arcpy.da.TableToNumPyArray(shapefile, 'DISTRICT_N')
df_sf = pd.DataFrame(arr)
df_sf = df_sf.drop_duplicates(keep = 'first')

df_map = df_map.merge(df_sf, left_on = 'DISTRICT',  right_on = 'DISTRICT_N', how = 'left', validate = "m:1")

df_charter = df_map.loc[(df_map['DISTRICT_N'].isna() == True) & (df_map['CHARTER_STATUS'] == 1)] #Charter districts( those without shapes)
#need too add lats and longs to data
df_ll = pd.read_csv(latlong, skiprows= 6, usecols = [2, 3, 4])
df_ll.columns = ['ID', 'Lat', 'Long']
df_ll = df_ll.loc[df_ll['ID'].isna() == False]
df_ll['DISTRICT'] = df_ll['ID'].str[3:].astype(int)

df_charter = df_charter.merge(df_ll, how= 'left', on = 'DISTRICT', validate = 'm:1')

print(df_charter.loc[df_charter.Lat.isna()==True])
##NOTE: two districts are missing Lats and longs, Fill those in--------------------------------------------------------------
###Always stop here and check, this will probably change from year to year. 

df_charter['Lat'] = np.where(df_charter['DISTRICT'] == 101813, 29.70577, df_charter['Lat'])
df_charter['Long'] = np.where(df_charter['DISTRICT'] == 101813, -94.313456, df_charter['Long'])

df_charter['Lat'] = np.where(df_charter['DISTRICT'] == 57837, 32.728282, df_charter['Lat'])
df_charter['Long'] = np.where(df_charter['DISTRICT'] == 57837, -96.812601, df_charter['Long'])

print(df_charter.loc[df_charter.Lat.isna()==True])

df_charter.to_csv(r'{0}\Table_CharterDistricts.csv'.format(cleandata))

df_map = df_map.loc[df_map['DISTRICT_N'].isna() == False] #Trad districts (with shapes)

###Traditional Districts with shapes------

#Add district shapefile to map
arcpy.Select_analysis(shapefile, 'TEMP')

#We'll need this file broke out by year, indicator, and race
layList = []
a = [years, list(sdDic), list(raceDic)]
for z in list(itertools.product(*a)):
    df_temp = df_map.loc[(df_map['SDYEAR'] == z[0]) & (df_map['INDICATOR'] == '{0}'.format(z[1])) & (df_map['ETHNICITY'] == '{0}'.format(z[2]))]
    #some of these won't have any data, so lets skip those by testing if the length of the df is >0
    if len(df_temp) > 0:
        tableN = r'{0}\Table_{1}_{2}_{3}.csv'.format(cleandata, z[0], z[1], z[2])
        df_temp.to_csv(tableN)
        layerN = 'Layer_{0}_{1}_{2}'.format(z[0], z[1], z[2])
        layList.append(layerN)
        arcpy.CopyFeatures_management('TEMP', layerN)
        arcpy.JoinField_management(layerN, 'DISTRICT_N', tableN, 'DISTRICT_N')

        lyr = m.listLayers(layerN)[0]
        lyr.definitionQuery = "SDRR IS NOT NULL"

layerN = 'Layer_All_SDs_merge'
arcpy.Merge_management(layList, layerN)

lyr = m.listLayers(layerN)[0]
sym = lyr.symbology
sym.updateRenderer('SimpleRenderer')
sym.renderer.symbol.color = {'RGB': [0, 112, 255, 100]}
sym.renderer.symbol.size = .5
lyr.symbology  = sym

arcpy.management.AddField(layerN, 'SDYEAR2', 'TEXT')
arcpy.management.CalculateField(layerN, 'SDYEAR2', "!SDYEAR!")

###Charter Districts with lat/long------
layerN = 'Layer_All_Charters'
arcpy.management.XYTableToPoint(r'{0}\Table_CharterDistricts.csv'.format(cleandata), layerN)

lyr = m.listLayers(layerN)[0]
sym = lyr.symbology
sym.updateRenderer('SimpleRenderer')
sym.renderer.symbol.color = {'RGB': [0, 112, 255, 100]}
sym.renderer.symbol.size = 8
lyr.symbology  = sym

arcpy.management.AddField(layerN, 'SDYEAR2', 'TEXT')
arcpy.management.CalculateField(layerN, 'SDYEAR2', "!SDYEAR!")


###Districts outlines------
lyr = m.listLayers('Current_Districts')[0]
sym = lyr.symbology
sym.updateRenderer('SimpleRenderer')
sym.renderer.symbol.color = {'RGB': [0, 0, 0, 0]}
sym.renderer.symbol.size = .5
lyr.symbology  = sym








