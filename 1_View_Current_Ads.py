# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 16:26:35 2023

@author: caolw
"""

import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine,text
import urllib
from st_aggrid import GridOptionsBuilder
from datetime import date


driver= '{ODBC Driver 17 for SQL Server}'
params = 'DRIVER='+driver+';SERVER='+st.secrets['MY_SERVER']+';PORT=1433;DATABASE='+st.secrets['MY_DB']+';UID='+st.secrets['MY_USERNAME']+';PWD='+ st.secrets['MY_PASSWORD']
cnxn = pyodbc.connect(params)
cursor = cnxn.cursor()
cursor.fast_executemany = True
db_params = urllib.parse.quote_plus(params)
engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}".format(db_params)) 




sql = """select s.id,englishofficialname name,a.name country,a.id area_id,concat(a.name,' (',c.divisionlevel,')',' - ',c.name) competition,c.id comp_id
from tr.squad s 
left join tr.parentsquads ps on s.id = ps.squadid
left join tr.area a on a.id = s.areaid
left join tr.competitionsquad cs on cs.squadid = s.id
left join tr.competition c on c.id = cs.competitionid
where s.id in (select distinct squadid from tr.usersquad) and ps.squadid is null
and s.name not like '%transfer%' and s.name <> ''
order by 2"""

squads = pd.DataFrame(engine.connect().execute(text(sql)))
squad_names = squads['name']
country_names = squads['country']
country_names = country_names.drop_duplicates().sort_values()

comp_names = squads['competition']
comp_names = comp_names.drop_duplicates().sort_values().dropna()

pos_sql = """select id,name pos from tr.generalposition order by name"""
pos = pd.DataFrame(engine.connect().execute(text(pos_sql)))

adtype_sql = """select id,iif(id=1,'Buy',Name) Name from tr.playeradtype"""
adtype = pd.DataFrame(engine.connect().execute(text(adtype_sql)))

max_buy_ad_sql = """select max(round(tr.ConvertCurrencyToEuros((pa.Amount),pa.CurrencyId,(pa.UpdatedAt)),0)) Fee
,max(round(tr.ConvertCurrencyToEuros((pa.grosssalary),pa.CurrencyId,(pa.UpdatedAt)),0)) Sal
,0.0 minn 
from tr.playerad pa where playeradtypeid = 1 and active = 1 and pa.UpdatedAt >= dateadd(mm,-6,getdate())"""
max_buy_ad = pd.DataFrame(engine.connect().execute(text(max_buy_ad_sql)))
max_fee = max_buy_ad.iloc[0,0]#.astype(float)
max_sal = max_buy_ad.iloc[0,1]#.astype(float)
minn = max_buy_ad.iloc[0,2]#.astype(float)

max_loan_ad_sql = """select max(round(tr.ConvertCurrencyToEuros((pa.Amount),pa.CurrencyId,(pa.UpdatedAt)),0)) Loan
,0.0 minn 
from tr.playerad pa where playeradtypeid = 2 and active = 1 and pa.UpdatedAt >= dateadd(mm,-6,getdate())"""
max_loan_ad = pd.DataFrame(engine.connect().execute(text(max_loan_ad_sql)))
max_loan = max_loan_ad.iloc[0,0].astype(float)


sty_sql  = """select id,generalpositionid, position_role style from tr.position_role"""
styles =  pd.DataFrame(engine.connect().execute(text(sty_sql)))
style = styles['style'].drop_duplicates()


st.set_page_config(
     page_title="TransferRoom Squad Needs",
     #page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     # menu_items={
     #     'Get Help': 'https://www.extremelycoolapp.com/help',
     #     'Report a bug': "https://www.extremelycoolapp.com/bug",
     #     'About': "# This is a header. This is an *extremely* cool app!"
     # }
 )




st.markdown("<font color=darkblue>Transfer</font><font color=green>Room</font>", unsafe_allow_html=True)
st.title("CS Team - Squad Needs Tracker")


#st.write(st.experimental_user['email'])
email = st.experimental_user['email']



st.header("Current Squad Needs") 



position = st.multiselect(
    'Select Position(s)'
    ,pos['pos'])

st.write(position)

posns_chosen = []
for i in range(0,len(position)):
    pos_chosen = position[i]
    posns_chosen.append(pos_chosen)

pos_ids_chosen = ['']
for r in range(0,len(posns_chosen)):
    pos_r = pos[pos['pos']==posns_chosen[r]]
    pos_r_id = str(pos_r.iloc[0,0])
    pos_ids_chosen.append(pos_r_id)

pos_ids_chosen = str(pos_ids_chosen).replace('[','').replace(']','')

st.write(pos_ids_chosen)

all_pos_ch = st.checkbox('All Positions',value = True)

all_pos = '0'
if all_pos_ch and len(pos_ids_chosen) <= 4:
    all_pos = '1'

all_styles = '1'

style_ids_chosen="""' '"""

left_foot = """'0'"""
foot_ids_chosen = """1,2,3"""
all_feet = '1'

if all_pos == '0' :
    sty_col,foot_col = st.columns(2)
    with sty_col:
        if pos_ids_chosen == """'', '6'""":
            styles = st.multiselect('Playing Style (CS added only)',[])
        else:
            style_sql = """select pr.*,concat(position_role,' (',gp.code,')') style from tr.position_role pr
                            left join tr.GeneralPosition gp on gp.Id = pr.generalpositionid
                            where gp.id in ("""+pos_ids_chosen+""")"""
            selected_styles = pd.DataFrame(engine.connect().execute(text(style_sql)))
            style = selected_styles['style']
            styles = st.multiselect('Playing Style (CS added only)',style)
            

        
        styles_chosen = []
        for s in range(0,len(styles)):
            style_chosen =styles[i]
            styles_chosen.append(style_chosen)
        
        style_ids_chosen = [' ']
        for r in range(0,len(styles_chosen)):
            style_r = selected_styles[selected_styles['style']==styles_chosen[r]]
            style_r_id = str(style_r.iloc[0,0])
            style_ids_chosen.append(pos_r_id)
        
        style_ids_chosen = str(style_ids_chosen).replace('[','').replace(']','')
        
        all_style_ch = st.checkbox('All Playing Styles',value = True)
        
        all_styles = '0'
        if all_style_ch and len(style_ids_chosen) <= 4:
            all_styles = '1'
        
    with foot_col:
        left_cb_ch = st.selectbox('Foot (CS/CB Only)',('Either','Left','Right'))
        
        if left_cb_ch == 'Either':
            foot_ids_chosen = """1,2,3"""
            left_foot = '0'
        elif left_cb_ch == 'Right':
            foot_ids_chosen = """2,3"""
            left_foot = '0'
            all_feet = '0'
        elif left_cb_ch == 'Left':
            foot_ids_chosen = """1,3"""
            left_foot = '1'
            all_feet = '0'
        
        
finan_col,squad_col = st.columns(2)

with finan_col:
    ad_type_ms = st.multiselect(
        'Select Ad Type(s)'
        ,adtype['Name'])
    
    adtyps_chosen = []
    for i in range(0,len(ad_type_ms)):
        ad_chosen = ad_type_ms[i]
        adtyps_chosen.append(ad_chosen)
    
    ad_ids_chosen = ['']
    for r in range(0,len(adtyps_chosen)):
        ad_r = adtype[adtype['Name']==adtyps_chosen[r]]
        ad_r_id = str(ad_r.iloc[0,0])
        ad_ids_chosen.append(ad_r_id)
    
    ad_ids_chosen = str(ad_ids_chosen).replace('[','').replace(']','')
    
    all_adtyp_ch = st.checkbox('All Ad Types',value = True)
    
    buy_ad_budget_min = '0'
    buy_ad_budget_max = '999999999'
    buy_ad_sal_min = '0'
    buy_ad_sal_max = '999999999'
    loan_ad_budget_min = '0'
    loan_ad_budget_max = '999999999'
    
    all_types = '0'
    if all_adtyp_ch and len(ad_ids_chosen) <= 4:
        all_types = '1'
    
    if ad_ids_chosen == """'', '1', '2'""" or all_types =='1':
        mincol,maxcol = st.columns(2)
        with mincol:
            buy_ad_budget_min = st.number_input('Transfer Fee Budget Min')
            buy_ad_sal_min    = st.number_input('Salary Budget Min')
            loan_ad_budget_min = st.number_input('Monthly Loan Fee Budget Min')
        
        with maxcol:
            buy_ad_budget_max = st.number_input('Transfer Fee Budget Max',value=max_fee)
            buy_ad_sal_max    = st.number_input('Salary Budget Max',value=max_sal)
            loan_ad_budget_max = st.number_input('Monthly Loan Fee Budget Max',value=max_loan)
    elif ad_ids_chosen == """'', '1'""":
        mincol,maxcol = st.columns(2)
        with mincol:
            buy_ad_budget_min = st.number_input('Transfer Fee Budget Min')
            buy_ad_sal_min    = st.number_input('Salary Budget Min')      
        with maxcol:
            buy_ad_budget_max = st.number_input('Transfer Fee Budget Max',value=max_fee)
            buy_ad_sal_max    = st.number_input('Salary Budget Max',value=max_sal)
    elif  ad_ids_chosen == """'', '2'""":
        mincol,maxcol = st.columns(2)
        with mincol:
            loan_ad_budget_min = st.number_input('Monthly Loan Fee Budget Min')
        with maxcol:
            loan_ad_budget_max = st.number_input('Monthly Loan Fee Budget Max',value=max_loan)

with squad_col:
    area = st.multiselect('Select Country(s)',country_names)
    area_ids_sql = ['']
    for i in range(0,len(area)):
        sql_syntax = "'"+str(area[i])+"',"
        area_ids_sql.append(sql_syntax)
    
    area_ids_sql = str(area_ids_sql)
    area_ids_sql = area_ids_sql.replace('",','')
    area_ids_sql = area_ids_sql.replace('"','')
    if len(area_ids_sql) > 4:
        area_ids_sql = area_ids_sql[1:len(area_ids_sql)-2]
    else:
        area_ids_sql = area_ids_sql[1:len(area_ids_sql)-1]
    
    area_ch = st.checkbox('All countries',value=True)
    
    all_area = '0' 
    if area_ch and len(area_ids_sql)<=4:
        all_area = '1'
    
    
    
    
    if len(area_ids_sql) > 4:
        comp_names_sql = """select distinct id, name,divisionlevel from (select concat(a.name,' (',c.divisionlevel,')',' - ',c.name) name,c.divisionlevel,c.id from tr.competition c left join tr.area a on a.id = c.areaid
        left join tr.competitionsquad cs on cs.competitionid = c.id
        where a.name in ("""+area_ids_sql+""")
        and male = 1 and category = 'default' and format = 'domestic league' and divisionlevel > 0 and cs.squadid is not null
        ) a
        order by name"""
        comps = pd.DataFrame(engine.connect().execute(text(comp_names_sql)))
        comp_names = comps['name']
        
        comp = st.multiselect('Select Competition (s)',comp_names)
    
        
        comps_chosen = []
        for i in range(0,len(comp)):
            comp_chosen = comp[i]
            comps_chosen.append(comp_chosen)
        
        comp_ids_chosen = ['']
        for r in range(0,len(comps_chosen)):
            comps_r = comps[comps['name']==comps_chosen[r]]
            comp_r_id = str(comps_r.iloc[0,0])
            comp_ids_chosen.append(comp_r_id)
        
        comp_ids_chosen = str(comp_ids_chosen).replace('[','').replace(']','')
    else:
        comp = st.multiselect('Select Competition (s)',comp_names)
        
        
        if len(comp)>0:
            comps_chosen = []
            for i in range(0,len(comp)):
                comp_chosen = comp[i]
                comps_chosen.append(comp_chosen)
            
            comp_ids_chosen = ['']
            for r in range(0,len(comps_chosen)):
                comps_r = squads[squads['competition']==comps_chosen[r]]
                comp_r_id = str(comps_r.iloc[0,5].astype(int))
                comp_ids_chosen.append(comp_r_id)
            
            comp_ids_chosen = str(comp_ids_chosen).replace('[','').replace(']','')
        else:
            comp_ids_chosen = """' '"""
    
    
    
    comp_ch = st.checkbox('All competitions',value = True)
    
    all_comps = '0' 
    if comp_ch and len(comp_ids_chosen)<=4:
        all_comps = '1'
    
    
    #### UPDATE TO BE LIKE COMPS
    
    
        
    if len(comp_ids_chosen) > 4:
       squad_names_sql = """select s.id,s.englishofficialname name
                            from tr.squad s 
                            left join tr.parentsquads ps on s.id = ps.squadid
                            left join tr.area a on a.id = s.areaid
                            left join tr.competitionsquad cs on cs.squadid = s.id
                            left join tr.competition c on c.id = cs.competitionid
                            where s.id in (select distinct squadid from tr.usersquad) and ps.squadid is null
                            and s.name not like '%transfer%' and s.name <> ''
                            and (a.name in ("""+area_ids_sql+""") or '"""+all_area+"""' = '1')
                            and (c.id in ("""+comp_ids_chosen+""") or '"""+all_comps+"""' = '1')"""
       squads = pd.DataFrame(engine.connect().execute(text(squad_names_sql)))
       squad_names = squads['name']
    
       squad = st.multiselect(
             'Select Squad(s)',
             squad_names)
        
       squads_chosen = []
       for i in range(0,len(squad)):
           squad_chosen = squad[i]
           squads_chosen.append(squad_chosen)
        
       squad_ids_chosen = ['']
       for r in range(0,len(squads_chosen)):
            squads_r = squads[squads['name']==squads_chosen[r]]
            squad_r_id = str(squads_r.iloc[0,0])
            squad_ids_chosen.append(squad_r_id)
        
       squad_ids_chosen = str(squad_ids_chosen).replace('[','').replace(']','')
       
    elif len(area_ids_sql) > 4:
        squad_names_sql = """select s.id,s.englishofficialname name
                             from tr.squad s 
                             left join tr.parentsquads ps on s.id = ps.squadid
                             left join tr.area a on a.id = s.areaid
                             left join tr.competitionsquad cs on cs.squadid = s.id
                             left join tr.competition c on c.id = cs.competitionid
                             where s.id in (select distinct squadid from tr.usersquad) and ps.squadid is null
                             and s.name not like '%transfer%' and s.name <> ''
                             and (a.name in ("""+area_ids_sql+""") or '"""+all_area+"""' = '1')
                             -- and (c.id in ("""+comp_ids_chosen+""") or '"""+all_comps+"""' = '1')"""
        squads = pd.DataFrame(engine.connect().execute(text(squad_names_sql)))
        squad_names = squads['name']
    
        squad = st.multiselect(
              'Select Squad(s)',
              squad_names)
         
        squads_chosen = []
        for i in range(0,len(squad)):
            squad_chosen = squad[i]
            squads_chosen.append(squad_chosen)
         
        squad_ids_chosen = ['']
        for r in range(0,len(squads_chosen)):
             squads_r = squads[squads['name']==squads_chosen[r]]
             squad_r_id = str(squads_r.iloc[0,0])
             squad_ids_chosen.append(squad_r_id)
         
        squad_ids_chosen = str(squad_ids_chosen).replace('[','').replace(']','')
    else:
        squad = st.multiselect(
              'Select Squad(s)',
              squad_names)
         
        if len(squad)>0:
            squads_chosen = []
            for i in range(0,len(squad)):
                squad_chosen = squad[i]
                squads_chosen.append(squad_chosen)
             
            squad_ids_chosen = ['']
            for r in range(0,len(squads_chosen)):
                 squads_r = squads[squads['name']==squads_chosen[r]]
                 squad_r_id = str(squads_r.iloc[0,0])
                 squad_ids_chosen.append(squad_r_id)
             
            squad_ids_chosen = str(squad_ids_chosen).replace('[','').replace(']','')
        else:
            squad_ids_chosen = """' '"""
    
    
    
    all_squads_ch = st.checkbox('All Squads', value = True)
    
    all_squads = '0'
    
    if all_squads_ch and len(squad_ids_chosen)<4:
        all_squads = '1'




npl_ch = st.checkbox('Show non-platform entries only')
npl = '0'
if npl_ch:
    npl = '1'





current_sql = """
select Country,Competition,Divisionlevel [Div. Level],squad,pos,foot
,ad_type,cast(budget_euros as int) budget_euros, cast(gross_salary_euros as int) gross_salary_euros
,typ
,case	when datediff(ww,date,getdate()) >= 5 and datediff(mm,date,getdate()) = 1 then concat(datediff(mm,date,getdate()),' month ago')
 	when datediff(ww,date,getdate()) >= 5 then concat(datediff(mm,date,getdate()),' months ago')
		when datediff(dd,date,getdate()) >= 7 and datediff(ww,date,getdate()) = 1 then concat(datediff(ww,date,getdate()),' week ago')
 	when datediff(dd,date,getdate()) >= 7 then concat(datediff(ww,date,getdate()),' weeks ago')
		when datediff(hh,date,getdate()) >= 24 and datediff(dd,date,getdate()) = 1 then concat(datediff(dd,date,getdate()),' day ago')
 	when datediff(hh,date,getdate()) >= 24 then concat(datediff(dd,date,getdate()),' days ago')
		when datediff(mi,date,getdate()) >= 60 and datediff(hh,date,getdate()) = 1 then concat(datediff(hh,date,getdate()),' hour ago')
 	when datediff(mi,date,getdate()) >= 60 then concat(datediff(hh,date,getdate()),' hours ago')
 	when datediff(mi,date,getdate()) = 1 then '1 minute ago'
 	else concat(datediff(mi,date,getdate()),' minutes ago') end
 	[Time caption]
from (
select *
,ROW_NUMBER() over (partition by squad,pos order by r) rw
from (
select a.name Country,c.name Competition,c.DivisionLevel,s.englishofficialName squad
,gp.name pos,max(pa.UpdatedAt) date ,round(tr.ConvertCurrencyToEuros(max(pa.Amount),pa.CurrencyId,max(pa.UpdatedAt)),0) budget_euros 
,'' not_an_ad_reason 
,case when pa.PlayerAdTypeId = 1 then 'buy' else 'loan' end ad_type 
,round(tr.ConvertCurrencyToEuros(max(pa.GrossSalary),pa.CurrencyId,max(pa.UpdatedAt)),0) gross_salary_euros 
,'' info_source ,'' email ,'Ad' typ,1 r 
,cast(f.name as nvarchar(100)) foot
,'' PlayStyle
from tr.PlayerAd pa 
inner join tr.Squad s on pa.SquadId = s.id 
inner join tr.GeneralPosition gp on pa.GeneralPositionId = gp.id 
inner join tr.CompetitionSquad cs on cs.SquadId = s.id 
inner join tr.Competition c on c.id = cs.CompetitionId 
inner join tr.area a on a.id = s.AreaId 
left join tr.foot f on f.id = pa.IsLeftFooted
where pa.Active = 1 
and pa.UpdatedAt >= dateadd(mm,-6,getdate())
and (pa.playeradtypeid in ("""+ad_ids_chosen+""") or '"""+all_types+"""' = '1')
and s.name not like '%transfer%' and s.name <> ''
and (pa.generalpositionid in ("""+pos_ids_chosen+""") or '"""+all_pos+"""' = '1')
and '"""+npl+"""' = 0
and (a.name in ("""+area_ids_sql+""") or '"""+all_area+"""' = '1')
and (c.id in ("""+comp_ids_chosen+""") or '"""+all_comps+"""' = '1')
and (s.id in ("""+squad_ids_chosen+""") or '"""+all_squads+"""' = '1')
and tr.convertcurrencytoeuros(pa.amount,pa.currencyid,pa.updatedat) >= iif(playeradtypeid = 1,"""+str(buy_ad_budget_min)+""","""+str(loan_ad_budget_min)+""")
and tr.convertcurrencytoeuros(pa.amount,pa.currencyid,pa.updatedat) <= iif(playeradtypeid = 1,"""+str(buy_ad_budget_max)+""","""+str(loan_ad_budget_max)+""")
and iif(playeradtypeid = 1,tr.convertcurrencytoeuros(pa.grosssalary,pa.currencyid,pa.updatedat),1) >= iif(playeradtypeid = 1,"""+str(buy_ad_sal_min)+""",0)
and iif(playeradtypeid = 1,tr.convertcurrencytoeuros(pa.grosssalary,pa.currencyid,pa.updatedat),2) <= iif(playeradtypeid = 1,"""+str(buy_ad_sal_max)+""",3)
and (iif(pa.generalpositionid = 3 and pa.isleftfooted=1,pa.isleftfooted,0) = iif(pa.generalpositionid = 3,"""+left_foot+""",0) or """+all_feet+""" = 1)
group by s.englishofficialName,gp.name,pa.CurrencyId,pa.PlayerAdTypeId,a.name,c.name,c.DivisionLevel,cast(f.name as nvarchar(100))
union
select area 
,competition 
,divisionlevel 
,squad 
,position 
,insertedat 
,budget_euros_max 
,not_an_ad_reason 
,ad_type ,annual_salary_euros_max 
,info_source 
,email 
,'CS Tracking' 
,2 
,cast(foot as nvarchar(100)) 
,position_role
from tr.temp_squad_needs sn 
where insertedat >= dateadd(mm,-6,getdate()) 
and (positionid in ("""+pos_ids_chosen+""") or '"""+all_pos+"""' = '1')
and (area in ("""+area_ids_sql+""") or '"""+all_area+"""' = '1')
and (comp_id in ("""+comp_ids_chosen+""") or '"""+all_comps+"""' = '1')
and (squadid in ("""+squad_ids_chosen+""") or '"""+all_squads+"""' = '1')
and (position_roleid in ("""+str(style_ids_chosen)+""") or '"""+all_styles+"""' = '1')
and (footid in ("""+foot_ids_chosen+""") or footid is null)
) a
) b
where rw = 1
order by date desc
"""


current =  pd.DataFrame(engine.connect().execute(text(current_sql)))
st.table(current)
    
    
    

    
    
         
    

