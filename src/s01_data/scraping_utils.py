import re
from bs4 import BeautifulSoup
import os
from os import path
from datetime import datetime
import pickle

CITY_DIMENSION_LABEL = {
     'Environnement': 'environment',
     'Transports': 'transport',
     'Sécurité': 'security',
     'Santé': 'health',
     'Sports et loisirs': 'sport_entertainment',
     'Culture': 'culture',
     'Enseignement':'education',
     'Commerces': 'business',
     'Qualité de vie': 'life_quality'
 }

vi_base_url = 'https://www.ville-ideale.fr/'

dict_cities = {}

def retrieve_city_general_data(soup):
    d_city = {
        'name': soup.find(id='colleft').find('h1').text.split(' ')[0],
        'postal_code': soup.find(id='colleft').find('h1').text.split(' ')[1][1:-1],
        'average_note': float(soup.find(id='ng').text.split(' ')[0].replace(',','.')),
        'count': int(soup.find(id='nobt').text.split(' ')[-2]),
        'update_time': datetime.now()
    }
    general_note_table = soup.find(id='tablonotes')
    for label_note in general_note_table.find_all('tr'):
        d_city[CITY_DIMENSION_LABEL[label_note.find('th').text]] =  float(label_note.find('td').text.replace(',','.'))
    return d_city

def retrieve_review_data(review_block):
    re_search = re.search(r'\d{2}-\d{2}-\d{4}',review_block.find_all('p')[0].text)
    date_text = re_search.group(0)
    re_search = re.search(r'\d{2}:\d{2}',review_block.find_all('p')[0].text)
    time_text = re_search.group(0)
    post_time = datetime.strptime('{}-{}'.format(date_text, time_text),'%d-%m-%Y-%H:%M')

    dimensions = [th.text for th in review_block.find_all('th')]
    notes = [int(td.text) for td in review_block.find_all('td')]
    vote_counts = review_block.find_all('p')[3].find_all('strong')
    d_review = {
        'post_time': post_time,
        'mean_note': float(review_block.find(class_='moyenne').text),
        **dict(zip(dimensions, notes)),
        'positive': review_block.find_all('p')[1].text,
        'negative': review_block.find_all('p')[2].text,
        'count_agree': int(vote_counts[0].text),
        'count_disagree': int(vote_counts[1].text)
    }
    return d_review

def proceed_to_next_page(driver):
    """
    redirect to the next review page if any.
    """
    try:
        driver.find_element_by_xpath('//a[starts-with(.,"Suivant")]').click()
        return True
    except:
        return False