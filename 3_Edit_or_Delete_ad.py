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


st.set_page_config(
     page_title="Edit CS Ad",
     layout="wide",
     initial_sidebar_state="collapsed",    
 )


st.markdown("<font color=darkblue>Transfer</font><font color=green>Room</font>", unsafe_allow_html=True)
st.title("CS Team - Squad Needs Tracker")


st.header('Edit existing CS Ad')


#st.write(st.experimental_user['email'])
email = st.experimental_user['email']



sql = """select *, case	when datediff(ww,insertedat,getdate()) >= 5 and datediff(mm,insertedat,getdate()) = 1 then concat(datediff(mm,insertedat,getdate()),' month ago')
 	when datediff(ww,insertedat,getdate()) >= 5 then concat(datediff(mm,insertedat,getdate()),' months ago')
		when datediff(dd,insertedat,getdate()) >= 7 and datediff(ww,insertedat,getdate()) = 1 then concat(datediff(ww,insertedat,getdate()),' week ago')
 	when datediff(dd,insertedat,getdate()) >= 7 then concat(datediff(ww,insertedat,getdate()),' weeks ago')
		when datediff(hh,insertedat,getdate()) >= 24 and datediff(dd,insertedat,getdate()) = 1 then concat(datediff(dd,insertedat,getdate()),' day ago')
 	when datediff(hh,insertedat,getdate()) >= 24 then concat(datediff(dd,insertedat,getdate()),' days ago')
		when datediff(mi,insertedat,getdate()) >= 60 and datediff(hh,insertedat,getdate()) = 1 then concat(datediff(hh,insertedat,getdate()),' hour ago')
 	when datediff(mi,insertedat,getdate()) >= 60 then concat(datediff(hh,insertedat,getdate()),' hours ago')
 	when datediff(mi,insertedat,getdate()) = 1 then '1 minute ago'
 	else concat(datediff(mi,insertedat,getdate()),' minutes ago') end
 	[Time caption] from tr.temp_squad_needs"""

cs_ads = pd.read_sql(sql, engine)

cs_ads_show = cs_ads[['Hidden_ad_id','squad','area','competition','Time caption','position','foot','position_role','ad_type','budget_euros_min','budget_euros_max','annual_salary_euros_min','annual_salary_euros_max','other_info','not_an_ad_reason','info_source','email']]

builder = GridOptionsBuilder.from_dataframe(cs_ads_show)
builder.configure_default_column(sortable=True,width = 750)
builder.configure_column('Hidden_ad_id',header_name = 'ID',width=70,maxWidth=80,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('squad',header_name = 'Squad',width=150,maxWidth=200,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('area',header_name = 'Country',width=150,maxWidth=200,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('competition',header_name = 'Competition',width=150,maxWidth=200,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('Time caption',header_name = 'Posted At',width=150,maxWidth=200,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('position',header_name = 'Position',width=150,maxWidth=200,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('foot',header_name='Foot',width=70,maxWidth=80,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('position_role',header_name = 'Playing Style',width=150,maxWidth=200,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('ad_type',header_name = 'Buy / Loan',width=110,maxWidth=130,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('budget_euros_min',header_name = 'Budget Min. (€)',width=130,maxWidth=150,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('budget_euros_max',header_name = 'Budget Max. (€)',width=130,maxWidth=150,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('annual_salary_euros_min',header_name = 'Sal Min. (€)',width=130,maxWidth=150,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('annual_salary_euros_max',header_name = 'Sal Max. (€)',width=130,maxWidth=150,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('other_info',header_name = 'Extra Info',width=130,wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('not_an_ad_reason',header_name = 'Not Ad Reason',wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('info_source',header_name = 'Source',wrapText = True,autoHeight=True,filterable = True)
builder.configure_column('email',header_name = 'CS Rep Email',width = 370,wrapText = True,autoHeight=True,filterable = True)
builder.configure_selection(use_checkbox = True, selection_mode = 'single')
builder.configure_auto_height(autoHeight = True)

# builder.configure_column('Other Player Verified', header_name='OPV', maxWidth = 150)
# builder.configure_auto_height(autoHeight = False)
go = builder.build()


pre_selection = AgGrid(cs_ads_show,gridOptions=go)

selected_rows = pre_selection["selected_rows"]

rows_selected = pd.DataFrame(selected_rows)

if len(rows_selected)>0:
    select_ad_id = rows_selected.iloc[0,1]
    selected_ad = cs_ads[cs_ads['Hidden_ad_id']==select_ad_id]
    
    pos_id = selected_ad['positionid'].iloc[0]
    
    ad_type_id = selected_ad['ad_type_id'].iloc[0]
    
    old_foot_id = selected_ad['footid'].iloc[0]
    old_foot = selected_ad['foot'].iloc[0]
    
    old_style_id = selected_ad['position_roleid'].iloc[0]
    old_style = selected_ad['position_role'].iloc[0]
    
    old_budget_min = selected_ad['budget_euros_min'].iloc[0]
    old_budget_max = selected_ad['budget_euros_max'].iloc[0]
    
    old_salary_min = selected_ad['annual_salary_euros_min'].iloc[0]
    old_salary_max = selected_ad['annual_salary_euros_max'].iloc[0]
    
    old_info = selected_ad['other_info'].iloc[0]
    
    pos_id = selected_ad['positionid'].iloc[0]
    
    
    style_sql = """select pr.*,concat(position_role,' (',gp.code,')') style from tr.position_role pr
                    left join tr.GeneralPosition gp on gp.Id = pr.generalpositionid
                    where gp.id in ("""+str(pos_id)+""") and pr.position_role != 'All Rounder'"""
    full_styles = pd.read_sql(style_sql,engine)
    styles = full_styles['style']
    
    
    st.subheader('Edit / Delete Ad')
    
    footupdtsql = ''
    
    st.text('Current foot = '+str(old_style))
    change_foot = st.checkbox('Change foot')
    if change_foot:
         all_feet = st.checkbox('Either foot',value=True)         
         
         if all_feet:
             new_foot_ = 'null'
             new_foot_id = 'null'
         else:
             new_foot = st.selectbox('Foot',('Left','Right'))
             
             if new_foot == 'Left':
                 new_foot_ = """'Left'"""
                 new_foot_id = '1'
             elif new_foot == 'Right':
                 new_foot_ = """'Right'"""
                 new_foot_id = '2'
             
         
         footupdtsql = """ update tr.temp_squad_needs set foot = """+new_foot_+""" where hidden_ad_id = """+str(select_ad_id)+"""
                          update tr.temp_squad_needs set footid = """+ new_foot_id+""" where hidden_ad_id = """+str(select_ad_id)+"""
                         """
    
    
    styleupdtsql = ''
    
    st.text('Current playing style = '+str(old_style))
    change_style = st.checkbox('Change playing style')
    if change_style:
         all_styles = st.checkbox('All Playing Styles',value=True)         
         
         if all_styles == True:
             new_style_ = 'null'
             new_style_id = 'null'
        
         else:
             new_style = st.selectbox('Playing Stle',styles)
             new_style_id = str(full_styles[full_styles['style']==new_style].iloc[0,0])
             new_style_ = """'"""+new_style+"""'"""
             
         styleupdtsql = """ update tr.temp_squad_needs set position_role = """+new_style_+""" where hidden_ad_id = """+str(select_ad_id)+"""
                           update tr.temp_squad_needs set position_roleid = """+new_style_id+""" where hidden_ad_id = """+str(select_ad_id)+"""
                            """

            
    bud_update_sql = ''
    
    st.text('Current budget = '+str(old_budget_min)+' - '+str(old_budget_max))
    change_budget = st.checkbox('Change budget')
    if change_budget:
         minbud,maxbud = st.columns(2)     
         with minbud:
             new_minbud = st.number_input('Min budget (euros)',value = old_budget_min)
             new_minbud = str(new_minbud)
         with maxbud:
             new_maxbud = st.number_input('Max budget (euros)',value = old_budget_max)
             new_maxbud = str(new_maxbud)
         
         bud_update_sql = """ update tr.temp_squad_needs set budget_euros_min = """+new_minbud+""" where hidden_ad_id = """+str(select_ad_id)+"""
                              update tr.temp_squad_needs set budget_euros_max = """+new_maxbud+""" where hidden_ad_id = """+str(select_ad_id)+"""
                             """
    
    sal_update_sql = ''
    
    if ad_type_id ==1:
        st.text('Current salary = '+str(old_salary_min)+' - '+str(old_salary_max))
        change_sal = st.checkbox('Change salary')
        if change_sal:
             minsal,maxsal = st.columns(2)     
             with minsal:
                 new_minsal = st.number_input('Min salary (euros)',value = old_salary_min)
                 new_minsal = str(new_minsal)
             with maxsal:
                 new_maxsal = st.number_input('Max salary (euros)',value = old_salary_max)
                 new_maxsal = str(new_maxsal)
                 
             sal_update_sql = """ update tr.temp_squad_needs set annual_salary_euros_min = """+new_minsal+""" where hidden_ad_id = """+str(select_ad_id)+"""   
                                 update tr.temp_squad_needs set annual_salary_euros_max = """+new_maxsal+""" where hidden_ad_id = """+str(select_ad_id)+"""
                                 """
        
    new_info_sql = ''
    
    st.text('Current info = '+str(old_info))
    change_info = st.checkbox('Add new extra info')
    if change_info:
         new_info = st.text_input('Extra info',value = old_info)
         new_info_sql = """ update tr.temp_squad_needs set other_info = '"""+new_info+"""' where hidden_ad_id = """+str(select_ad_id)+"""
         """
    
    now = date.today()
    
    new_inserted_at_sql = """update tr.temp_squad_needs set insertedat = """+str(now)+""" where hidden_ad_id = """+str(select_ad_id)+"""
                            """
         
    update_sql = footupdtsql+styleupdtsql+bud_update_sql+sal_update_sql+new_info_sql
    st.write(update_sql)
                
    
    delete_sql = """ delete from tr.temp_squad_needs where hidden_ad_id = """+str(select_ad_id)+"""
    """
    
    updatecol,deletecol = st.columns(2)
    
    with updatecol:
        if st.button('Update Ad'):
            cursor.execute(update_sql)
            cursor.commit()
            st.text('Ad Updated')
            
    with deletecol:
        if st.button('Delete Ad'):
            cursor.execute(delete_sql)
            cursor.commit()
            st.text('Ad Deleted')
            
        

    
