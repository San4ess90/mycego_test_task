import mimetypes
import os

from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
import requests
from typing import List, Dict, Union
from django.views.decorators.csrf import csrf_exempt

YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

DOCUMENT_TYPES = ["application/pdf",
                  "application/msword",
                  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                  "application/odt",
                  ]
IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]


def index(request):
    return render(request, 'diskviewer/index.html')


@csrf_exempt
def list_files(request):
    if request.method == 'POST' or 'public_key' in request.GET:
        public_key = request.POST.get('public_key') or request.GET.get('public_key')
        current_path = request.GET.get('path', '')
        file_type = request.GET.get('file_type', 'all')  # Новый параметр фильтрации
        parent_path = os.path.dirname(current_path) if current_path else ''

        files_list = fetch_files(public_key, current_path, file_type)
        return render(request, 'diskviewer/files.html', {
            'files': files_list,
            'public_key': public_key,
            'current_path': current_path,
            'parent_path': parent_path,
            'selected_file_type': file_type
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


def fetch_files(public_key: str, path: str = '', file_type: str = 'all') -> List[Dict[str, Union[str, List]]]:
    params = {'public_key': public_key, 'path': path}
    response = requests.get(YANDEX_API_URL, params=params)

    if response.status_code == 200:
        items = response.json().get('_embedded', {}).get('items', [])
        result = []

        for item in items:
            if item['type'] == 'dir':
                result.append({
                    'name': item['name'],
                    'type': 'folder',
                    'path': item['path']
                })
            elif item['type'] == 'file':
                mime_type, _ = mimetypes.guess_type(item['name'])

                if file_type == 'document' and mime_type not in DOCUMENT_TYPES:
                    continue
                elif file_type == 'image' and mime_type not in IMAGE_TYPES:
                    continue

                result.append({
                    'name': item['name'],
                    'type': 'file',
                    'url': item['file']
                })

        return result
    return []
