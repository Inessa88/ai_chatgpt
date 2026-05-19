import json
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Product


PRODUCT_FIELDS = ('name', 'description', 'price', 'stock', 'is_active')


def serialize_product(product):
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': f'{product.price:.2f}',
        'stock': product.stock,
        'is_active': product.is_active,
        'created_at': product.created_at.isoformat().replace('+00:00', 'Z'),
        'updated_at': product.updated_at.isoformat().replace('+00:00', 'Z'),
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


def apply_product_data(product, data, partial=False):
    required_fields = ('name', 'price')
    errors = {}

    if not partial:
        for field in required_fields:
            if field not in data:
                errors[field] = ['This field is required.']

    for field, value in data.items():
        if field not in PRODUCT_FIELDS:
            continue

        if field == 'price':
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError, ValueError):
                errors[field] = ['Enter a number.']
                continue

        setattr(product, field, value)

    if errors:
        raise ValidationError(errors)

    product.full_clean()
    return product


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = [serialize_product(product) for product in Product.objects.all()]
        return JsonResponse(products, safe=False)

    try:
        product = apply_product_data(Product(), parse_json_body(request))
    except ValidationError as error:
        return validation_error_response(error)

    product.save()
    return JsonResponse(serialize_product(product), status=201)


@csrf_exempt
@require_http_methods(['GET', 'PATCH', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise Http404('Product not found.')

    if request.method == 'GET':
        return JsonResponse(serialize_product(product))

    if request.method == 'DELETE':
        product.delete()
        return HttpResponse(status=204)

    try:
        product = apply_product_data(product, parse_json_body(request), partial=True)
    except ValidationError as error:
        return validation_error_response(error)

    product.save()
    return JsonResponse(serialize_product(product))
