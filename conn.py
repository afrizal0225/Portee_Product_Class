import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import numpy as np
from datetime import datetime

conn = st.connection('gsheets', type=GSheetsConnection)

#Data Source
online = conn.read(worksheet="PURCHASE REPORT")
sales = conn.read(worksheet="SALES REPORT")
sales = sales.iloc[80410:]
toko = conn.read(worksheet="Barang Masuk", usecols=list(range(8)))
toko = toko.loc[toko['location_destination']=='Toko Anggrek']
#Data Source

# Data Proses
sales['CodeArtikel'] = sales['Code'].str[:13]
sales['Date'] = pd.to_datetime(sales['Date'], format='%d-%b-%Y')
# toko['Date'] = toko['Date'].dt.strftime('%d-%m-%Y')
marsales = sales.loc[sales['Date'].between("01-Jan-2024", "31-Mar-2024")]


ons = marsales.loc[(marsales['CHANNEL']=='TOKOPEDIA')|(marsales['CHANNEL']=='SHOPEE')|(marsales['CHANNEL']=='TIKTOK')|(marsales['CHANNEL']=='SHOPIFY')|(marsales['CHANNEL']=='WHATSAPP')|(marsales['CHANNEL']=='LAZADA')]
offs = marsales.loc[(marsales['CHANNEL']=='TOKO')|(marsales['CHANNEL']=='MTO')]

online['CodeArtikel'] = online['Code'].str[:13]
toko['CodeArtikel'] = toko['SKU'].str[:13]

def label_values(x):
    if x >= 95:
        return 'C'
    elif x >= 80:
        return 'B'
    else:
        return 'A'

ons1 = ons.groupby(['Category','CodeArtikel'])['Net Sales'].sum().sort_values(ascending=False).reset_index()
ons1['Rev Contri'] = round(ons1['Net Sales']/ ons1['Net Sales'].sum()*100,2)
ons1['Cumsum'] = ons1['Rev Contri' ].cumsum()
ons1['Product Level'] = ons1['Cumsum'].apply(label_values)

offs1 = offs.groupby(['Category','CodeArtikel'])['Net Sales'].sum().sort_values(ascending=False).reset_index()
offs1['Rev Contri'] = round(offs1['Net Sales']/ offs1['Net Sales'].sum()*100,2)
offs1['Cumsum'] = offs1['Rev Contri' ].cumsum()
offs1['Product Level'] = offs1['Cumsum'].apply(label_values)

online1 = online[['CodeArtikel','Date']].sort_values(by=['CodeArtikel','Date'])


toko['received_date'] = pd.to_datetime(toko['received_date'], format='%d/%b/%Y %H:%M')
toko['received_date'] = toko['received_date'].dt.strftime('%d-%m-%Y')
toko1 = toko[['CodeArtikel','received_date']].sort_values(by=['CodeArtikel','received_date'])
toko1.rename(columns={'received_date': 'Date'}, inplace=True)

toko1= toko1.drop_duplicates(subset=['CodeArtikel'], keep='first')
online1 =online1.drop_duplicates(subset=['CodeArtikel'], keep='first')

nama = sales[['Product Name','CodeArtikel']]
nama= nama.drop_duplicates(subset=['Product Name','CodeArtikel'], keep='first')

monline = pd.merge(ons1,online1,how='outer',on=['CodeArtikel'])
monline = pd.merge(monline,nama,how='left',on=['CodeArtikel'])
moffline = pd.merge(offs1,toko1,how='outer',on=['CodeArtikel'])
moffline = pd.merge(moffline,nama,how='left',on=['CodeArtikel'])

mofflinec = moffline.loc[moffline['Product Level']=="C"]
mofflinec['current date']= datetime.today().strftime('%d-%m-%Y')
monlinec = monline.loc[monline['Product Level']=="C"]
monlinec['current date']= datetime.today().strftime('%d-%m-%Y')
mofflinec['Date'] = pd.to_datetime(mofflinec['Date'], format='%d-%m-%Y')
mofflinec['Date']=pd.to_datetime(mofflinec['Date'])
mofflinec['current date']=pd.to_datetime(mofflinec['current date'])
mofflinec['Date'] = pd.to_datetime(mofflinec['Date'], format='%d-%m-%Y')
monlinec['Date']=pd.to_datetime(monlinec['Date'])
monlinec['current date']=pd.to_datetime(monlinec['current date'])

mofflinec['Umur Product'] = ((mofflinec['current date'].dt.to_period('M').view(dtype='int64') - mofflinec['Date'].dt.to_period('M').view(dtype='int64')))
mofflinec=mofflinec[['Category','CodeArtikel','Product Name','Net Sales','Umur Product','Product Level']]

monlinec['Umur Product'] = ((monlinec['current date'].dt.to_period('M').view(dtype='int64') - monlinec['Date'].dt.to_period('M').view(dtype='int64')))
monlinec=monlinec[['Category','CodeArtikel','Product Name','Net Sales','Umur Product','Product Level']]

all1 = marsales.groupby(['Category','CodeArtikel'])['Net Sales'].sum().sort_values(ascending=False).reset_index()
all1['Rev Contri'] = round(all1['Net Sales']/ all1['Net Sales'].sum()*100,2)
all1['Cumsum'] = all1['Rev Contri' ].cumsum()
all1['Product Level'] = all1['Cumsum'].apply(label_values)
all1 = pd.merge(all1,nama,how='left',on=['CodeArtikel'])

# Data Proses

# Data Display
st.write("""
# All product Class
Gabungan produk  semua kategori dan levelnya.
""")

st.dataframe(all1[['Category','CodeArtikel','Product Name','Net Sales','Product Level']])

st.write("""
# Online product Class
Semua online product kategori dan levelnya.
""")

st.dataframe(monlinec)

st.write("""
# Offline product Class
Semua offline product kategori dan levelnya.
""")

st.dataframe(mofflinec)

