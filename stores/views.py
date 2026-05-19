import json

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Store


STORE_FIELDS = ('name', 'description', 'address', 'phone', 'is_active')


def serialize_store(store):
    return {
        'id': store.id,
        'name': store.name,
        'description': store.description,
        'address': store.address,
        'phone': store.phone,
        'is_active': store.is_active,
        'created_at': store.created_at.isoformat().replace('+00:00', 'Z'),
        'updated_at': store.updated_at.isoformat().replace('+00:00', 'Z'),
    }


def parse_json_body(request):
    if not request.body:
        return {}

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        raise ValidationError({'detail': ['Invalid JSON.']})

    if not isinstance(data, dict):
        raise ValidationError({'detail': ['Expected a JSON object.']})

    return data


def validation_error_response(error):
    if hasattr(error, 'message_dict'):
        return JsonResponse(error.message_dict, status=400)

    return JsonResponse({'detail': error.messages}, status=400)


def apply_store_data(store, data, partial=False):
    required_fields = ('name', 'address')
    errors = {}

    if not partial:
        for field in required_fields:
            if field not in data:
                errors[field] = ['This field is required.']

    for field, value in data.items():
        if field not in STORE_FIELDS:
            continue

        setattr(store, field, value)

    if errors:
        raise ValidationError(errors)

    store.full_clean()
    return store


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def store_list(request):
    if request.method == 'GET':
        stores = [serialize_store(store) for store in Store.objects.all()]
        return JsonResponse(stores, safe=False)

    try:
        store = apply_store_data(Store(), parse_json_body(request))
    except ValidationError as error:
        return validation_error_response(error)

    store.save()
    return JsonResponse(serialize_store(store), status=201)


@csrf_exempt
@require_http_methods(['GET', 'PATCH', 'DELETE'])
def store_detail(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404('Store not found.')

    if request.method == 'GET':
        return JsonResponse(serialize_store(store))

    if request.method == 'DELETE':
        store.delete()
        return HttpResponse(status=204)

    try:
        store = apply_store_data(store, parse_json_body(request), partial=True)
    except ValidationError as error:
        return validation_error_response(error)

    store.save()
    return JsonResponse(serialize_store(store))
