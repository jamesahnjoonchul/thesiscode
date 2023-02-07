import pandas as pd
import numpy as np
import json
import requests
import bs4 as bs
import re
from html import unescape
from collections import Counter, defaultdict
import warnings
import pickle
warnings.filterwarnings('ignore')
import sys
pd.set_option('display.max_colwidth', None)
import time
import sys 

def get_recent_dict(sub_dict):
    recent_dict = sub_dict['filings']['recent']
    recent_date = recent_dict['reportDate']
    recent_form = recent_dict['form']
    recent_access = recent_dict['accessionNumber']
    return recent_date, recent_form, recent_access

def build_df(date, form, access):
    df = pd.DataFrame({'report_date' : date, 'recent_form' : form, 'access_num' : access})
    df_clean = df[df['report_date'] != ''] #remove null dates
    df_clean['clean_num'] = df_clean['access_num'].map(lambda x: x.replace('-',''))
    df_clean['clean_date'] = df_clean['report_date'].map(lambda x: x.replace('-',''))
    df_clean = df_clean.loc[(df_clean['recent_form'] == '10-Q')  | (df_clean['recent_form'] == '10-K')]
    df_clean = df_clean[~df_clean['clean_num'].str.startswith('999999')]
    return df_clean

# def get_url(df_clean, ticker):
#     add_url_list = []
#     ticker = str(ticker).lower()
#     for link in df_clean['url']:
#         test_link = requests.get(link, headers=headers)
#         html = bs.BeautifulSoup(test_link.text, 'lxml')
#         table = html.find('table')
#         html_table = pd.DataFrame(pd.read_html(str(table))[0])
#         html_table = html_table.loc[html_table['Name'].apply(lambda x: x[-3:] == 'htm')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'ex[hv_\-0-9]+')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'R[0-9]+')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'exhibit')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'merger')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'certification')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'credit')]
#         html_table = html_table.loc[~html_table['Name'].str.contains(r'_d[0-9]{1,2}')]
#         html_table = html_table.sort_values(by='Size', ascending = False).reset_index()
#         try:
#             file_name = html_table['Name'][0]
#             if len(file_name) < 5:
#                 file_name = html_table['Name'][1]
#                 add_url_list.append(file_name)
#             elif re.match(r'ex[\-0-9]+', file_name):
#                 file_name = html_table['Name'][1]
#                 add_url_list.append(file_name)
#             else:
#                 add_url_list.append(file_name)
#         except KeyError:
#             continue
#     return add_url_list

def get_url(df_clean):
    try:
        add_url_list = df_clean['url'].map(get_file_name)
    except:
        print('get url fail')
    return add_url_list

def get_file_name(link):
    test_link = s.get(link, headers=headers)
    html = bs.BeautifulSoup(test_link.text, 'lxml')
    table = html.find('table')
    html_table = pd.DataFrame(pd.read_html(str(table))[0])
    html_table = html_table.loc[html_table['Name'].apply(lambda x: x[-3:] == 'htm')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'ex[hv_\-0-9]+')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'R[0-9]+')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'exhibit')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'merger')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'lease')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'certification')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'credit')]
    html_table = html_table.loc[~html_table['Name'].str.contains(r'_d[0-9]{1,2}')]
    html_table = html_table.sort_values(by='Size', ascending = False).reset_index()
    try:
        file_name = html_table['Name'][0]
        if len(file_name) < 5:
            file_name = html_table['Name'][1]
        elif re.match(r'ex[\-0-9]+', file_name):
            file_name = html_table['Name'][1]
        else:
            file_name = file_name
    except: #KeyError
        print('get file name fail')
    return file_name
# def get_doc(df_clean):
#     key_dict = {}
#     for date, link in zip(df_clean['report_date'], df_clean['f_url']):
#         html = requests.get(link, headers = headers)
#         bs_html = bs.BeautifulSoup(html.text, 'lxml')
#         text = bs_html.find_all('body')
#         text = unescape(text)
#         lis =[]
#         for t in text:
#             clean = re.sub('<[^<]+?>', ' ', str(t))
#             clean = clean.replace(u'\xa0', u' ')
#             clean = clean.replace(u'\x90', u' ')
#             clean = clean.replace(u'\x91', u' ')
#             clean = clean.replace(u'\x92', u' ')
#             clean = clean.replace(u'\x93', u' ')
#             clean = clean.replace(u'\x94', u' ')
#             clean = clean.replace(u'\x95', u' ')
#             clean = clean.replace(u'\x96', u' ')
#             clean = clean.replace(u'\x97', u' ')
#             clean = clean.replace(u'\x98', u' ')
#             clean = clean.replace(u'\x99', u' ')
#             clean = clean.replace('\n',' ')
#             lis.append(clean)
#         text = [text.lower() for text in lis]
#         flat_text = [te for te in text]
#         one = " ".join(flat_text)
#         key_text = re.findall("discussion\s{0,9}and\s{0,9}analysis.*?quantitative\s{0,9}and\s{0,9}qualitative\s{0,9}disclosures\s{0,9}about\s{0,9}market\s{0,9}risk", one)
#         if len(key_text) == 0:
#             key_text = re.findall(r"discussion\s{0,9}and\s{0,9}analysis.{1000,}results\s{0,9}of\s{0,9}operations\s{0,9}[summary]*\s{0,9}[of]*\s{0,9}[selected]*\s{0,9}[financial]*\s{0,9}[data]*", one)
#         if len(key_text) == 0:
#             key_text = re.findall(r"[()a-z0-9\s]*it[\s]*em\s{0,9}[237a-z.—\s]*\s{0,9}management['’\s]+s\s{0,9}discussion\s{0,9}and\s{0,9}analysis(.*?)item\s{0,9}[3478]+[a-z]*.\s{0,9}", one)
#         try:
#             key_text = max(key_text, key = len)
#             key_dict[date] = key_text
#         except:
#             print(f'{date}failure')
#     return key_dict

def get_doc(df_clean):
    try:
        df_clean['text'] = df_clean['f_url'].map(get_text)
        key_dict = dict(zip(df_clean['report_date'], df_clean['text']))
        return key_dict
    except:
        print('get document fail')

def get_text(link):
    html = s.get(link, headers = headers)
    bs_html = bs.BeautifulSoup(html.text, 'lxml')
    text = bs_html.find_all('body')
    text = unescape(text)
    lis = []
    for t in text:
        clean = re.sub('<[^<]+?>', ' ', str(t))
        clean = clean.replace(u'\xa0', u' ')
        clean = clean.replace(u'\x90', u' ')
        clean = clean.replace(u'\x91', u' ')
        clean = clean.replace(u'\x92', u' ')
        clean = clean.replace(u'\x93', u' ')
        clean = clean.replace(u'\x94', u' ')
        clean = clean.replace(u'\x95', u' ')
        clean = clean.replace(u'\x96', u' ')
        clean = clean.replace(u'\x97', u' ')
        clean = clean.replace(u'\x98', u' ')
        clean = clean.replace(u'\x99', u' ')
        clean = clean.replace('\n',' ')
        lis.append(clean)
    text = [text.lower() for text in lis]
    flat_text = [te for te in text]
    one = " ".join(flat_text)
    key_text = re.findall("discussion\s{0,9}and\s{0,9}analysis.*?quantitative\s{0,9}and\s{0,9}qualitative\s{0,9}disclosures\s{0,9}about\s{0,9}market\s{0,9}risk", one)
    if len(key_text) == 0:
        key_text = re.findall(r"discussion\s{0,9}and\s{0,9}analysis.{1000,}results\s{0,9}of\s{0,9}operations\s{0,9}[summary]*\s{0,9}[of]*\s{0,9}[selected]*\s{0,9}[financial]*\s{0,9}[data]*", one)
    if len(key_text) == 0:
        key_text = re.findall(r"[()a-z0-9\s]*it[\s]*em\s{0,9}[237a-z.—\s]*\s{0,9}management['’\s]+s\s{0,9}discussion\s{0,9}and\s{0,9}analysis(.*?)item\s{0,9}[3478]+[a-z]*.\s{0,9}", one)
    try:
        key_text = max(key_text, key = len)
    except:
        print('get text fail')
    return key_text

# pool = multiprocessing.Pool() #multiprocessing to the list of  api links

# for comments, data_json in zip(df['data.num_comments'], data_json_pool):

def main_operation(cik_df):
    total_dict = {}
    for i in range(len(cik_df)):
        cik_long = cik_df.iloc[i,:]['cik_long']
        ticker = cik_df.iloc[i,:]['ticker']
        print(ticker)
        cik = cik_df.iloc[i,:]['cik_str']
        sub = s.get(f'https://data.sec.gov/submissions/CIK{cik_long}.json', headers = headers)
        sub_dict = dict(sub.json())
        date, form , access = get_recent_dict(sub_dict)
        df_clean = build_df(date, form, access)
        df_clean['url'] = 'https://www.sec.gov/Archives/edgar/data/' + str(cik) + '/' + df_clean['clean_num']
        add_url_list = get_url(df_clean)
        try:
            df_clean['add_url'] = add_url_list
            df_clean['f_url'] = df_clean['url'] + '/' + df_clean['add_url']
            key_dict = get_doc(df_clean)
            total_dict[ticker] = key_dict
        except ValueError: 
            print('truncated')
            df_clean = df_clean.iloc[:len(add_url_list),:]
            df_clean['add_url'] = add_url_list
            df_clean['f_url'] = df_clean['url'] + '/' + df_clean['add_url']
            key_dict = get_doc(df_clean)
            total_dict[ticker] = key_dict
    return total_dict

if __name__ == '__main__':
    s = requests.Session()
    stdoutOrigin=sys.stdout
    sys.stdout = open("log.txt", "w")
    headers = {'User-Agent': "joonchulahn@gmail.com"}
    tickers_cik = s.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
    cik_df = pd.json_normalize(pd.json_normalize(tickers_cik.json(), max_level = 0).values[0])
    cik_df['cik_long'] = cik_df['cik_str'].astype('str').str.zfill(10)
    cik_df_sample = cik_df[250:3000] #try 2 250:1000
    total_dict = main_operation(cik_df_sample)
    sys.stdout.close()
    sys.stdout=stdoutOrigin
    with open('total_dict_test2.pickle', 'wb') as handle:
        pickle.dump(total_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)