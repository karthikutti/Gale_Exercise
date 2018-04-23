from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from django.core.exceptions import MultipleObjectsReturned
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
from main.models import ScrapyItem

scrapyd = ScrapydAPI('http://localhost:6800')

def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False

    return True

@csrf_exempt
@require_http_methods(['POST', 'GET'])
def crawl(request):
    if request.method == 'POST':

        url = request.POST.get('url', '')
        depth = request.POST.get('depth','1')
        depth = int(depth)

        if not url:
            return JsonResponse({'error': 'Missing  args','url':url})

        if not is_valid_url(url):
            return JsonResponse({'error': 'URL is invalid','url':url})

        domain = urlparse(url).netloc
        unique_id = str(uuid4())

        settings = {
            'unique_id': unique_id,
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        try:
            item = ScrapyItem.objects.get(url=url)
        except MultipleObjectsReturned:
            item = ScrapyItem.objects.filter(url=url).first()
        except ScrapyItem.DoesNotExist:
            item = False

        if item and (depth is 1):
            return JsonResponse({'link_url': item.to_dict['link_url'], 'image_urls': item.to_dict['image_urls'],
                                 'url': item.to_dict['url']})
        else:
            task = scrapyd.schedule('default', 'icrawler',
                               settings=settings, url=url, depth=depth, unique_id=unique_id, domain=domain)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    elif request.method == 'GET':
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                item = ScrapyItem.objects.get(unique_id=unique_id)
                return JsonResponse({'link_url': item.to_dict['link_url'], 'image_urls' : item.to_dict['image_urls'], 'url' : item.to_dict['url']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})


@csrf_exempt
@require_http_methods(['GET'])
def fetchdb(request):
    if request.method == 'GET':

        url = request.GET.get('url', '')

        if not url:
            return JsonResponse({'error': 'Missing  args','url':url})

        if url:
            try:
                item = ScrapyItem.objects.get(url=url)
            except MultipleObjectsReturned:
                item = ScrapyItem.objects.filter(url=url).first()
            except ScrapyItem.DoesNotExist:
                item = False

            if item:
                return JsonResponse({'link_url': item.to_dict['link_url'], 'image_urls': item.to_dict['image_urls'],
                                     'url': item.to_dict['url']})
            else:
                return JsonResponse({'status': '200 OK Not in DB'})