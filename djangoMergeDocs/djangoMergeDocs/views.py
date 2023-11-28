from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfMerger
from PIL import Image
import aiohttp
import io
import base64
import json

from .models import MergeRequest

async def fetch_pdf(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            file_data = await response.read()
            return file_data


async def merge(request):
        # If this is a POST request then process the Form data
    if request.method == 'POST':

        try:
            data = json.loads(request.body)
            merge_request = MergeRequest(**data)
            

            if len(merge_request.urls) < 2 or not merge_request.nombreArchivo:
                return JsonResponse({"error": "Invalid 'urls' or 'nombreArchivo.'"}, status=400)

            merger = PdfMerger()

            for url in merge_request.urls:
                try:
                    file_data = await fetch_pdf(url)
                    pdf_file = io.BytesIO(file_data)
                    merger.append(pdf_file)

                except Exception:
                    try:
                        image = Image.open(io.BytesIO(file_data))
                        image_pdf = io.BytesIO()
                        image.save(image_pdf, format='PDF', resolution=100.0)
                        merger.append(image_pdf)

                    except Exception:
                        error_message = f"Formato de archivo no admitido para la URL: {url}"
                        return HttpResponse({"error": error_message}, status=400)

            output_pdf = io.BytesIO()
            merger.write(output_pdf)
            encoded_file = base64.b64encode(output_pdf.getvalue()).decode('utf-8')

            return JsonResponse({"message": "Fusión exitosa", "output_filename": merge_request.nombreArchivo, "output_pdf": encoded_file})

        except Exception as e:
            return HttpResponse({"error": str(e)}, status=400)

# Asegúrate de utilizar 'await' para ejecutar la vista asíncrona
async def async_merge_view(request):
    return await merge(request)
        
def helloworld(reponse):
    return HttpResponse("Hello world! from Django")

