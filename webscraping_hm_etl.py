#!/usr/bin/env python
# coding: utf-8

# 0.0 Imports
import os
import logging
import sqlite3
import requests
import inflection
import regex as re
import numpy as np
import pandas as pd
import seaborn as sns

from datetime import datetime
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from matplotlib import pyplot as plt
from IPython.core.display import HTML


def data_collection(url, headers):
    # 1.0 Extração de dados
    # make request
    page = requests.get(url, headers=headers)

    # Instance Beautiful Soup
    soup = BeautifulSoup(page.text, "html.parser")

    # ---------------- Product Data -----------------------------

    # extract all products
    products = soup.find('ul', class_='products-listing small')

    product_list = products.find_all('article', class_='hm-product-item')

    # product id
    product_id = [p.get('data-articlecode') for p in product_list]

    # product_category
    product_category = [p.get('data-category') for p in product_list]

    # product name
    product_list = products.find_all('a', class_='link')
    product_name = [p.get_text() for p in product_list]

    # price
    product_list = products.find_all('span', class_='price regular')
    product_price = [p.get_text() for p in product_list]

    # merge scrapy into data frame
    data = pd.DataFrame([product_id, product_category, product_name, product_price]).T
    data.columns = ['product_id', 'product_category', 'product_name', 'product_price']

    return data


def data_collection_by_product(data, headers):
    # 2.0 Extração de dados por produtos

    # Empty dataframe
    df_compositions = pd.DataFrame()

    # unique columns for all products
    aux = []

    cols = {'Art. No.', 'Care instructions', 'Composition', 'Concept', 'Description', 'Fit', 'Imported',
     'Material', 'More sustainable materials', 'Nice to know', 'Size', 'color_id', 
     'messages.clothingStyle', 'messages.garmentLength', 'messages.waistRise', 'style_id'}
    df_pattern = pd.DataFrame(columns=cols)

    for i in range(len(data)):
        #Api Request
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] + '.html'
        logger.debug('product: %s', url)
        #url = 'https://www2.hm.com/en_us/productpage.0690449022.html' # test for one product

        page = requests.get(url, headers=headers)

        # Beautiful Soup
        soup = BeautifulSoup(page.text, 'html.parser')
        
        try:
            # color name
            product_list = soup.find_all('a', {'class':['filter-option miniature', 'filter-option miniature active']} )
            color_name = [p.get('data-color') for p in product_list]

            # product id
            product_id = [p.get('data-articlecode') for p in product_list]

            df_color = pd.DataFrame( [product_id, color_name]).T
            df_color.columns = ['product_id', 'color_name']

            #-------------------------- request detail products for colors -----------------------------
            for j in range(len(df_color)):
                #Api Request
                url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id'] + '.html'
                logger.debug('color: %s', url)
                
                page = requests.get(url, headers=headers)

                # Beautiful Soup
                soup = BeautifulSoup(page.text, 'html.parser')

                # product name
                products = soup.find_all('section', class_='product-name-price')
                product_name = products[0].find('h1').get_text()

                # price
                product_price = products[0].find('span').get_text()
                product_price = re.findall(r'\d+\.?\d', product_price)[0]

                #------------------------composition----------------------------

                product_composition_list = soup.find_all('div', class_='details-attributes-list-item')
                product_composition = [list(filter(None, p.get_text().split('\n'))) for p in product_composition_list]

                # rename dataframe
                df_composition = pd.DataFrame(product_composition).T
                df_composition.columns = df_composition.iloc[0]

                # delete first row
                df_composition = df_composition.iloc[1:].fillna(method='ffill')

                # Remove shell, pocket and lining
                df_composition['Composition'] = df_composition['Composition'].replace('Shell: ', '', regex=True)
                df_composition['Composition'] = df_composition['Composition'].replace('Pocket lining: ', '', regex=True)
                df_composition['Composition'] = df_composition['Composition'].replace('Pocket: ', '', regex=True)
                df_composition['Composition'] = df_composition['Composition'].replace('Lining: ', '', regex=True)

                # garantee the same number of columns
                df_composition = pd.concat([df_pattern, df_composition], axis=0)

                # keep new columns if they shows  up
                aux = aux + df_composition.columns.tolist()

                # collect most important columns
                df_composition = df_composition[['Art. No.', 'Composition', 'Size', 'Fit', 
                                                 'Material', 'Description']]

                # rename columns
                df_composition.columns = ['product_id', 'composition', 'size', 'fit', 'material', 'description']

                # adding name and price
                df_composition['product_name'] = product_name
                df_composition['product_price'] = product_price

                # merge data color + decomposition
                df_composition = pd.merge(df_composition, df_color, how='left', on='product_id')

                # all products
                df_compositions = pd.concat([df_compositions, df_composition], axis=0)
        except:
            continue
    # Join showroom data + details
    df_compositions['style_id'] = df_compositions['product_id'].apply(lambda x: x[:-3])
    df_compositions['color_id'] = df_compositions['product_id'].apply(lambda x: x[-3:])

    # scrapy datetime
    df_compositions['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return df_compositions


def data_cleaning(data1):
    # 3.0 Limpeza dos dados

    # collect all collumns
    old_cols = ['product_id', 'composition', 'size', 'fit', 'material', 'description',
           'product_name', 'product_price', 'color_name', 'style_id', 'color_id',
           'scrapy_datetime']

    # function for new format for each collumn
    snakecase = lambda x : inflection.underscore(x)

    # applying change in columns for snakecase and underline
    new_cols = list(map(snakecase, old_cols))

    data1.columns = new_cols

    # Create Collumn Inner Leg
    data1['inner_leg_size'] = data1['size'].apply(lambda x: 89.5 if x=='Inner leg: Length: 89.5 cm (Size 33)'
                                                  else 0)

    # Create collumn Waist
    data1['waist_size'] = data1['size'].apply(lambda x: 90.5 if x=='Waist: Circumference: 90.5 cm (Size 33)'
                                                  else 0)

    # fillout size value
    data1['size'] = data1['size'].apply(lambda x: 0 if pd.isnull(x) else 33)

    # product_name - undercase and removing special characters
    data1['product_name'] = data1['product_name'].apply(lambda x: x.replace(' ', '_').replace('®', '').lower())

    # color_name - undercase and removing space
    data1['color_name'] = data1['color_name'].apply(lambda x: x.replace(' ', '_').replace('/', '_').lower())

    # fit - undercase and removing space
    data1['fit'] = data1['fit'].apply(lambda x: x.replace(' ', '_').lower())

    #--------------Cleaning composition------------------------------------------------

    # break composition by comma
    dfaux = data1['composition'].str.split(',', expand=True).reset_index(drop=True)

    # choose order from columns
    df_ref = pd.DataFrame(index=np.arange(len(data1)), columns=['cotton', 'spandex', 'polyester'])

    #--------------------------  cotton ----------------------------------------------
    # Collect cotton from first collumn
    df_cotton = dfaux.loc[dfaux[0].str.contains('Cotton', na=True), 0]
    df_cotton.name = 'cotton'

    df_ref = pd.concat([df_ref, df_cotton], axis=1)

    # Collect cotton from second collumn
    df_cotton2 = dfaux.loc[dfaux[1].str.contains('Cotton', na=True), 1]
    df_cotton2.name = 'cotton2'

    df_ref = pd.concat([df_ref, df_cotton2], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # merge results from cotton in one collumn
    df_ref['cotton'] = df_ref.apply(lambda x: x['cotton'] if pd.isna(x['cotton2']) else x['cotton2'], axis=1)
    df_ref.drop(columns='cotton2', inplace=True)

    #-------------------------- polyester ----------------------------------------------
    # Collect polyester from first collumn
    df_polyester = dfaux.loc[dfaux[0].str.contains('Polyester', na=True), 0]
    df_polyester.name = 'polyester'

    df_ref = pd.concat([df_ref, df_polyester], axis=1)

    # Collect polyester from second collumn
    df_polyester2 = dfaux.loc[dfaux[1].str.contains('Polyester', na=True), 1]
    df_polyester2.name = 'polyester2'

    df_ref = pd.concat([df_ref, df_polyester2], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # merge results from cotton in one collumn
    df_ref['polyester'] = df_ref.apply(lambda x: x['polyester'] if pd.isna(x['polyester2']) else x['polyester2'], axis=1)
    df_ref.drop(columns='polyester2', inplace=True)

    #-------------------------- Elastomultiester ----------------------------------------------
    # Collect elastomultiester from second collumn
    df_elastomultiester = dfaux.loc[dfaux[1].str.contains('Elastomultiester', na=True), 1]
    df_elastomultiester.name = 'elastomultiester'

    # merge results
    df_ref = pd.concat([df_ref, df_elastomultiester], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    #-------------------------- spandex ----------------------------------------------
    # Collect spandex from second collumn
    df_spandex = dfaux.loc[dfaux[1].str.contains('Spandex', na=True), 1]
    df_spandex.name = 'spandex'

    df_ref = pd.concat([df_ref, df_spandex], axis=1)

    # Collect spandex from third collumn
    df_spandex2 = dfaux.loc[dfaux[2].str.contains('Spandex', na=True), 2]
    df_spandex2.name = 'spandex2'

    df_ref = pd.concat([df_ref, df_spandex2], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # merge results from cotton in one collumn
    df_ref['spandex'] = df_ref.apply(lambda x: x['spandex'] if pd.isna(x['spandex2']) else x['spandex2'], axis=1)
    df_ref.drop(columns='spandex2', inplace=True)

    # format composition data
    df_ref['cotton'] = df_ref['cotton'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_ref['polyester'] = df_ref['polyester'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_ref['elastomultiester'] = df_ref['elastomultiester'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)
    df_ref['spandex'] = df_ref['spandex'].apply(lambda x: int(re.search('\d+', x).group(0))/100 if pd.notnull(x) else x)

    # drop all rows with NA in all collumns
    df_ref.dropna(axis=0, how='all', inplace=True)
    df_ref.fillna(0, inplace=True)

    # reset index and final join
    data1.reset_index(drop=True, inplace=True)

    data1 = pd.concat([data1, df_ref], axis=1)

    # description - undercase and removing space
    data1['description'] = data1['description'].apply(lambda x: x.replace(' ', '_').lower())

    # material - undercase and removing space
    data1['material'] = data1['material'].apply(lambda x: x.replace(' ', '_').lower())

    # product_price
    data1['product_price'] = data1['product_price'].astype('float64')

    # cotton
    data1['cotton'] = data1['cotton'].astype('float64')

    # spandex
    data1['spandex'] = data1['spandex'].astype('float64')

    # polyester
    data1['polyester'] = data1['polyester'].astype('float64')

    # drop composition
    data1.drop(columns='composition', inplace=True)

    return data1


def data_insert(data1):
    # 4.0 Insert into Database

    # organize columns
    data1 = data1[['product_id', 'style_id', 'color_id', 'product_name', 'color_name','fit', 'size', 'inner_leg_size', 'waist_size',
                   'cotton', 'polyester', 'elastomultiester', 'spandex', 'material', 'description', 'scrapy_datetime']]

    # connect in the database
    conn = create_engine('sqlite:///hm_db.sqlite', echo=False)

    # insert data to table
    data1.to_sql('showroom', con=conn, if_exists='append', index=False)

    return None


if __name__ == '__main__':
    # logging
    path = 'F:/SamuelOliveiraAlvesd/Desktop/Data_Science/Projetos/Ds_ao_Dev/webscraping_jeans/'

    if not os.path.exists(path + 'Logs'):
        os.makedirs(path + 'Logs')

    logging.basicConfig(
        filename = path + 'Logs/webscraping_hm.log',
        level = logging.DEBUG, 
        format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('webscraping_hm')


    # parameters and constants
    # URL
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'

    # parameters
    headers = {'User-Agent': 'Mozilla/5.0 {Macintosh; Intel Mac Os X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36}'}

    # data collection
    data = data_collection(url, headers)
    logger.info('data collection done')

    # data collection by product
    data_product = data_collection_by_product(data, headers)
    logger.info('data collection by product done')

    # data cleaning
    data_product_cleaned = data_cleaning(data_product)
    logger.info('data product cleaned done')

    # data insertion into database
    data_insert(data_product_cleaned)
    logger.info('data insertion into database done')
