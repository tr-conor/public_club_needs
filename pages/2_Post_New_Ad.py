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



sql = """select s.id,s.englishofficialname name,c.id comp_id,c.name comp,c.divisionlevel,a.id area_id,a.name area
from tr.squad s 
left join tr.parentsquads ps on s.id = ps.squadid
left join tr.competitionsquad cs on cs.squadid = s.id
left join tr.competition c on c.id = cs.competitionid
left join tr.area a on a.id = c.areaid
where s.id in (select distinct squadid from tr.usersquad) and ps.squadid is null
and s.name not like '%transfer%' and s.name <> ''
order by 2"""

squads = pd.DataFrame(engine.connect().execute(text(sql)))
squad_names = squads['name']

pos_sql = """select id,name pos from tr.generalposition order by name"""
pos = pd.DataFrame(engine.connect().execute(text(pos_sql)))

sty_sql  = """select distinct position_role style from tr.position_role"""
style = pd.DataFrame(engine.connect().execute(text(sty_sql)))

feet_sql = """select id,name from tr.foot"""
feet = pd.DataFrame(engine.connect().execute(text(feet_sql)))
feet_op = feet['name']

st.set_page_config(
     page_title="TransferRoom Squad Needs",
     #page_icon="🧊",
     #layout="wide",
     initial_sidebar_state="expanded",
     # menu_items={
     #     'Get Help': 'https://www.extremelycoolapp.com/help',
     #     'Report a bug': "https://www.extremelycoolapp.com/bug",
     #     'About': "# This is a header. This is an *extremely* cool app!"
     # }
 )


###### need
## search for squads looking for XX position and see ads + cs entries combined
    ## lower priority filters - transfer type
## insert new needs - position, budget, date, why isn't this an ad
    ## lower priority columns: detail, wage budget
    ## remove a need low priority
## order by date, budget

st.markdown("<font color=darkblue>Transfer</font><font color=green>Room</font>", unsafe_allow_html=True)
st.title("CS Team - Squad Needs Tracker")


#st.write(st.experimental_user['email'])
email = st.experimental_user['email']


st.header('Post new hidden-ad')

st.subheader('Squad')
squad = st.selectbox(
     'Select Squad',
     squad_names)
squadid = squads[squads['name']==squad].iloc[0,0]
comp_id = int(squads[squads['name']==squad].iloc[0,2])
comp = squads[squads['name']==squad].iloc[0,3]
comp_div_lev = int(squads[squads['name']==squad].iloc[0,4])
area_id = int(squads[squads['name']==squad].iloc[0,5])
area = squads[squads['name']==squad].iloc[0,6]
    
#print(all_squads)

st.subheader('Select Position(s)')


position = st.multiselect(
    'Select Position(s)'
    ,pos['pos'])

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

# all_pos_ch = st.checkbox('All Positions',value = True)

# all_pos = '0'
# if all_pos_ch and len(pos_ids_chosen) <= 4:
#     all_pos = '1'


for posi in position:
    st.subheader(str(posi)+' Ad')
    posit = pos[pos['pos']==str(posi)]
    pos_id = str(posit.iloc[0,0]) 
    posid = posit.iloc[0,0]
    
    all_styles = '0'
    
    st.subheader('Playing Style & Preferred Foot')

    sty_col,foot_col = st.columns(2)
    with sty_col:
        all_style_ch = st.checkbox(str(posi)+' All Playing Styles')
        
        if all_style_ch:
            all_styles = '1'
        else:        
            style_sql = """select pr.*,concat(position_role,' (',gp.code,')') style from tr.position_role pr
                            left join tr.GeneralPosition gp on gp.Id = pr.generalpositionid
                            where gp.id in ("""+pos_id+""") and pr.position_role != 'All Rounder'"""
            selected_styles = pd.DataFrame(engine.connect().execute(text(style_sql)))
            style = selected_styles['style']
            style_sb = st.selectbox(str(posi)+' Playing Style',style)
            
            style_sel = selected_styles[selected_styles['style']==style_sb]
            style_id = style_sel.iloc[0,0]
        
        
        
    with foot_col:
        all_feet = '0'
        all_feet_ch = st.checkbox(str(posi)+' Either Foot')
        
        if all_feet_ch:
            all_feet = '1'
        
        else:
            foot_sb = st.selectbox(str(posi)+' Foot',('Left','Right'))
            
            foot_id_selected = feet[feet['name']==foot_sb].iloc[0,0]
        
    st.subheader('Ad Type & Budgets')
    
    ttype,cur = st.columns(2)
    
    with ttype:
        transfer_type = st.selectbox(str(posi)+' Buy or Loan',('Buy and Loan','Buy','Loan'))
    with cur:
        currency = st.selectbox(str(posi)+' Currency',('Euro','GBP','USD'))
    
    if transfer_type == 'Buy':
        
        # st.subheader('To Buy Ad')
        st.write('Transfer fee budget')
        
        buy_budget_blank_ch = st.checkbox(str(posi)+' Transfer fee budget unknown / withheld')
    
        buy_budget_blank = 0
        if buy_budget_blank_ch:
            buy_budget_blank = 1
        else:
            tf1,tf2 = st.columns(2)
            with tf1:
                buy_budget_min = st.number_input(str(posi)+' Fee min.')
            with tf2:
                buy_budget_max = st.number_input(str(posi)+' Fee max.')
       
        
        
        st.write('Gross annual salary budget')
        
        salary_blank_ch = st.checkbox(str(posi)+' Salary unknown / withheld')
        salary_blank = 0
        if salary_blank_ch:
            salary_blank = 1
        else:
            sal1,sal2 = st.columns(2)
            with sal1:
                salary_min = st.number_input(str(posi)+' Sal min.')
            with sal2:
                salary_max = st.number_input(str(posi)+' Sal max.')
        
    
        
    
    elif transfer_type == 'Loan':
        st.write('Monthly loan fee budget (including salary)')
        
        loan_budget_blank_ch = st.checkbox(str(posi)+' Monthly loan fee budget unknown / withheld')
        
        loan_budget_blank = 0
        if loan_budget_blank_ch:
            loan_budget_blank = 1
        else:
            lc1,lc2 = st.columns(2)
            with lc1:
                loan_budget_min = st.number_input(str(posi)+' Loan min.')    
            with lc2:
                loan_budget_max = st.number_input(str(posi)+' Loan max.')
           
    
    
    else:
        st.subheader('To Buy Ad')
        st.write('Transfer fee budget')
        buy_budget_blank_ch = st.checkbox(str(posi)+' Transfer fee budget unknown / withheld')
    
        buy_budget_blank = 0
        if buy_budget_blank_ch:
            buy_budget_blank = 1
        else:
            tf1,tf2 = st.columns(2)
            with tf1:
                buy_budget_min = st.number_input(str(posi)+' Fee min.')
            with tf2:
                buy_budget_max = st.number_input(str(posi)+' Fee max.')
       
        
        
        st.write('Gross annual salary budget')
        
        salary_blank_ch = st.checkbox(str(posi)+' Salary unknown / withheld')
        salary_blank = 0
        if salary_blank_ch:
            salary_blank = 1
        else:
            sal1,sal2 = st.columns(2)
            with sal1:
                salary_min = st.number_input(str(posi)+' Sal min.')
            with sal2:
                salary_max = st.number_input(str(posi)+' Sal max.')
        

    
    
        st.subheader('To Loan Ad')
        st.write('Monthly loan fee budget (including salary)')
        
        loan_budget_blank_ch = st.checkbox(str(posi)+' Monthly loan fee budget unknown / withheld')
        
        loan_budget_blank = 0
        if loan_budget_blank_ch:
            loan_budget_blank = 1
        else:
            lc1,lc2 = st.columns(2)
            with lc1:
                loan_budget_min = st.number_input(str(posi)+' Loan min.')    
            with lc2:
                loan_budget_max = st.number_input(str(posi)+' Loan max.')
        
        
            
    st.subheader('Other Information')
        
        
    other = st.text_input(str(posi)+' - Other Information of Note')
    
    reason = st.text_input(str(posi)+' - Why isnt this created as an ad on the platform? MANDATORY')
    
    info = st.text_input(str(posi)+' - Where did you get this information? MANDATORY')
        
        
    if st.button('Insert '+str(posi)+' Ad'):
        if transfer_type == 'Buy':
        # st.write(str(transfer_type)+' '+str(currency)+' '+str(feet_ms))
            
            if reason == '':
                st.warning("You must specify a reason why this hasn't been created as an Ad on the platform")
            else:
                if info =='':
                    st.warning("You must specify where you got this information from")
                else:       
                    if buy_budget_blank == 0:
                        input_budget_min = buy_budget_min
                        input_budget_max = buy_budget_max
                    if buy_budget_blank == 1:
                        input_budget_min = None
                        input_budget_max = None
                    if salary_blank == 0:
                        input_sal_min = salary_min
                        input_sal_max = salary_max
                    if salary_blank == 1:
                        input_sal_min = None
                        input_sal_max = None
                    
                    if all_styles == '1':
                        input_style_id = None
                        input_style = None
                    if all_styles == '0':
                        input_style_id = style_id
                        input_style = style_sb
                    transfer_type_id = 1
                    
                    if all_feet == '0':
                        input_foot = foot_sb
                        input_foot_id = foot_id_selected
                    if all_feet == '1':
                        input_foot = None
                        input_foot_id = None
                        
                    now = date.today()
                    
                        
                    df = pd.DataFrame({'squadid':[squadid]
                                        ,'squad':[squad]
                                        ,'areaid':[area_id]
                                        ,'area':[area]
                                        ,'comp_id':[comp_id]
                                        ,'competition':[comp]
                                        ,'divisionlevel':[comp_div_lev]
                                        ,'insertedat':[now]
                                        ,'positionid':[posid]
                                        ,'position':[posi]
                                        ,'footid':[input_foot_id]
                                        ,'foot':[input_foot]
                                        ,'position_roleid':[input_style_id]
                                        ,'position_role':[input_style]
                                        ,'ad_type_id':[transfer_type_id]
                                        ,'ad_type':[transfer_type]
                                        ,'budget_euros_min':[input_budget_min]
                                        ,'budget_euros_max':[input_budget_max]
                                        ,'annual_salary_euros_min':[input_sal_min]
                                        ,'annual_salary_euros_max':[input_sal_max]
                                        ,'other_info':[other]
                                        ,'not_an_ad_reason':[reason]
                                        ,'info_source':[info]
                                        ,'email':[email]
                                        })
                    
                    st.write('To Buy Ad inserted to database')
                    st.write(df)
                    
                    df.to_sql("temp_squad_needs", engine, index=False, 
                                                  if_exists="append", schema="tr")
                
        if transfer_type == 'Loan':
            # st.write(str(transfer_type)+' '+str(currency)+' '+str(feet_ms))
                
            if reason == '':
                st.warning("You must specify a reason why this hasn't been created as an Ad on the platform")
            else:
                if info =='':
                    st.warning("You must specify where you got this information from")
                else:       
                    if loan_budget_blank == 0:
                        input_budget_min = loan_budget_min
                        input_budget_max = loan_budget_max
                    if loan_budget_blank == 1:
                        input_budget_min = None
                        input_budget_max = None
                    
                    input_sal_min = None
                    input_sal_max = None
                    
                    if all_styles == '1':
                        input_style_id = None
                        input_style = None
                    if all_styles == '0':
                        input_style_id = style_id
                        input_style = style_sb
                        
                    transfer_type_id = 2
                    
                    if all_feet == '0':
                        input_foot = foot_sb
                        input_foot_id = foot_id_selected
                    if all_feet == '1':
                        input_foot = None
                        input_foot_id = None
                        
                    now = date.today()
                        
                    df = pd.DataFrame({'squad':[squad]
                                        ,'squadid':[squadid]
                                        ,'areaid':[area_id]
                                        ,'area':[area]
                                        ,'comp_id':[comp_id]
                                        ,'competition':[comp]
                                        ,'divisionlevel':[comp_div_lev]
                                        ,'insertedat':[now]
                                        ,'positionid':[pos_id]
                                        ,'position':[posi]
                                        ,'footid':[input_foot_id]
                                        ,'foot':[input_foot]
                                        ,'position_roleid':[input_style_id]
                                        ,'position_role':[input_style]
                                        ,'ad_type_id':[transfer_type_id]
                                        ,'ad_type':[transfer_type]
                                        ,'budget_euros_min':[input_budget_min]
                                        ,'budget_euros_max':[input_budget_max]
                                        ,'annual_salary_euros_min':[input_sal_min]
                                        ,'annual_salary_euros_max':[input_sal_max]
                                        ,'other_info':[other]
                                        ,'not_an_ad_reason':[reason]
                                        ,'info_source':[info]
                                        ,'email':[email]
                                        })
                    
                    st.write('To Loan Ad inserted to database')
                    st.write(df)
                    
                    df.to_sql("temp_squad_needs", engine, index=False, 
                                                  if_exists="append", schema="tr")
        
        if transfer_type == 'Buy and Loan':
            # st.write(str(transfer_type)+' '+str(currency)+' '+str(feet_ms))
                
            if reason == '':
                st.warning("You must specify a reason why this hasn't been created as an Ad on the platform")
            else:
                if info =='':
                    st.warning("You must specify where you got this information from")
                else:       
                    
                    if buy_budget_blank == 0:
                        buy_input_budget_min = buy_budget_min
                        buy_input_budget_max = buy_budget_max
                    if buy_budget_blank == 1:
                        buy_input_budget_min = None
                        buy_input_budget_max = None
                    if salary_blank == 0:
                        buy_input_sal_min = salary_min
                        buy_input_sal_max = salary_max
                    if salary_blank == 1:
                        buy_input_sal_min = None
                        buy_input_sal_max = None
                    
                    if loan_budget_blank == 0:
                        loan_input_budget_min = loan_budget_min
                        loan_input_budget_max = loan_budget_max
                    if loan_budget_blank == 1:
                        loan_input_budget_min = None
                        loan_input_budget_max = None
                    
                    loan_input_sal_min = None
                    loan_input_sal_max = None
                    
                    if all_styles == '1':
                        input_style_id = None
                        input_style = None
                    if all_styles == '0':
                        input_style_id = style_id
                        input_style = style_sb
                        
                    buy_transfer_type_id = 1
                    buy_transfer_type = 'Buy'
                    loan_transfer_type_id = 2
                    loan_transfer_type = 'Loan'
                    
                    if all_feet == '0':
                        input_foot = foot_sb
                        input_foot_id = foot_id_selected
                    if all_feet == '1':
                        input_foot = None
                        input_foot_id = None
                        
                    now = date.today()
                    
                    buy_df = pd.DataFrame({'squad':[squad]
                                        ,'squadid':[squadid]
                                        ,'areaid':[area_id]
                                        ,'area':[area]
                                        ,'comp_id':[comp_id]
                                        ,'competition':[comp]
                                        ,'divisionlevel':[comp_div_lev]
                                        ,'insertedat':[now]
                                        ,'positionid':[pos_id]
                                        ,'position':[posi]
                                        ,'footid':[input_foot_id]
                                        ,'foot':[input_foot]
                                        ,'position_roleid':[input_style_id]
                                        ,'position_role':[input_style]
                                        ,'ad_type_id':[buy_transfer_type_id]
                                        ,'ad_type':[buy_transfer_type]
                                        ,'budget_euros_min':[buy_input_budget_min]
                                        ,'budget_euros_max':[buy_input_budget_max]
                                        ,'annual_salary_euros_min':[buy_input_sal_min]
                                        ,'annual_salary_euros_max':[buy_input_sal_max]
                                        ,'other_info':[other]
                                        ,'not_an_ad_reason':[reason]
                                        ,'info_source':[info]
                                        ,'email':[email]
                                        })
                    st.write('To Buy Ad inserted to database')
                    st.write(buy_df)
                    
                    buy_df.to_sql("temp_squad_needs", engine, index=False, 
                                                  if_exists="append", schema="tr")
                   
                        
                    loan_df = pd.DataFrame({'squad':[squad]
                                        ,'squadid':[squadid]
                                        ,'areaid':[area_id]
                                        ,'area':[area]
                                        ,'comp_id':[comp_id]
                                        ,'competition':[comp]
                                        ,'divisionlevel':[comp_div_lev]
                                        ,'insertedat':[now]
                                        ,'positionid':[pos_id]
                                        ,'position':[posi]
                                        ,'footid':[input_foot_id]
                                        ,'foot':[input_foot]
                                        ,'position_roleid':[input_style_id]
                                        ,'position_role':[input_style]
                                        ,'ad_type_id':[loan_transfer_type_id]
                                        ,'ad_type':[loan_transfer_type]
                                        ,'budget_euros_min':[loan_input_budget_min]
                                        ,'budget_euros_max':[loan_input_budget_max]
                                        ,'annual_salary_euros_min':[loan_input_sal_min]
                                        ,'annual_salary_euros_max':[loan_input_sal_max]
                                        ,'other_info':[other]
                                        ,'not_an_ad_reason':[reason]
                                        ,'info_source':[info]
                                        ,'email':[email]
                                        })
                    
                    st.write('To Loan Ad inserted to database')
                    st.write(loan_df)
                    
                    loan_df.to_sql("temp_squad_needs", engine, index=False, 
                                                  if_exists="append", schema="tr")
                    
                        # df.to_sql("temp_squad_needs", engine, index=False, 
                        #                               if_exists="append", schema="tr") 
                    
                    
                    
    
    
    
         
    

