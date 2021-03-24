from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests
from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.utils import timezone
BASE_CRAIGLIST_URL = 'https://mumbai.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    # return HttpResponse({'home is working'})
    return render(request, 'craiglist_app/base.html')


def new_search(request):
    # return HttpResponse({'new search is working'})
    search = request.POST.get('search')
    final_url = BASE_CRAIGLIST_URL.format(quote_plus(search))
    # print(final_url)
    models.SearchModel.objects.create(search=search, create_time=timezone.now())
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})
    final_postings = []
    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')
        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'
        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image = 'https://craigslist.org/images/peace.jpg'

        final_postings.append((post_title, post_url, post_price,post_image))
        # print(post_title)
        # print(post_price)
        # print(post_url)
        # print(data)
    for_frontend_use = {
        'search': search,
        'final_postings': final_postings,
    }

    return render(request, 'craiglist_app/new_search.html', for_frontend_use)
