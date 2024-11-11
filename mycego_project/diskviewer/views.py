from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
import requests
from typing import List, Dict, Union
from django.views.decorators.csrf import csrf_exempt

YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

def index(request):
    return render(request, 'diskviewer/index.html')

@csrf_exempt
def list_files(request):
    if request.method == 'POST' or 'public_key' in request.GET:
        public_key = request.POST.get('public_key') or request.GET.get('public_key')
        path = request.GET.get('path', '')  # Получаем текущий путь, если он указан
        files_list = fetch_files(public_key, path)
        return render(request, 'diskviewer/files.html', {
            'files': files_list,
            'public_key': public_key,
            'current_path': path
        })
    return redirect('index')

@csrf_exempt
def download_file(request):
    if request.method == 'POST':
        file_url = request.POST.get('file_url')
        file_name = request.POST.get('file_name')
        response = requests.get(file_url, stream=True)

        if response.status_code == 200:
            return FileResponse(response.raw, as_attachment=True, filename=file_name)
        else:
            return HttpResponse("Ошибка при загрузке файла", status=500)
    return redirect('index')

def fetch_files(public_key: str, path: str = '') -> List[Dict[str, Union[str, List]]]:
    """
    Получаем список файлов и папок на Яндекс.Диске по публичной ссылке с учетом вложенности.
    """
    params = {'public_key': public_key, 'path': path}
    response = requests.get(YANDEX_API_URL, params=params)

    if response.status_code == 200:
        items = response.json().get('_embedded', {}).get('items', [])
        result = []

        for item in items:
            if item['type'] == 'dir':
                # Если элемент - папка, добавляем её как папку
                result.append({
                    'name': item['name'],
                    'type': 'folder',
                    'path': item['path']
                })
            elif item['type'] == 'file':
                # Если элемент - файл, добавляем его в список
                result.append({
                    'name': item['name'],
                    'type': 'file',
                    'url': item['file']
                })

        return result
    return []
