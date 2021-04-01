from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import requests
from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.utils import timezone
BASE_CRAIGLIST_URL = 'https://{}.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    # return HttpResponse({'home is working'})
    return render(request, 'craiglist_app/base.html')


def new_search(request):
    # return HttpResponse({'new search is working'})
    # print(request.POST)
    search = request.POST.get('search')
    if request.POST.get('min_price'):
        min_price = int(request.POST.get('min_price'))
    else:
        min_price=0
    if request.POST.get('max_price'):
        max_price = int(request.POST.get('max_price'))
    else:
        max_price=10000000000
    location =request.POST.get('location')
    print(location)
    print((min_price))
    print(max_price)
    final_url = BASE_CRAIGLIST_URL.format(location,quote_plus(search))
    print(final_url)
    models.SearchModel.objects.create(search=search, create_time=timezone.now())
    response = requests.get(final_url)
    data = response.text
    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})
    final_postings = []
    for post in post_listings:
        if post.find(class_='result-price'):
            price_csv = post.find(class_='result-price').text[1:].split(',')
            post_price=""
            for price in price_csv:
                post_price+=price
            if int(post_price)>=min_price and int(post_price)<=max_price:

                post_title = post.find(class_='result-title').text
                post_url = post.find('a').get('href')
                post_price=post.find(class_='result-price').text
                # if post.find(class_='result-price'):

                # else:
                #     post_price = 'N/A'
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