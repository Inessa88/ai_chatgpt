from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from .models import Product


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def product():
    return Product.objects.create(
        name='Desk Lamp',
        description='Adjustable LED lamp',
        price=Decimal('49.99'),
        stock=12,
    )


@pytest.mark.django_db
def test_product_string_representation(product):
    assert str(product) == 'Desk Lamp'


@pytest.mark.django_db
def test_create_product(api_client):
    response = api_client.post(
        reverse('product-list'),
        {
            'name': 'Notebook',
            'description': 'Hardcover notebook',
            'price': '14.50',
            'stock': 25,
            'is_active': True,
        },
        content_type='application/json',
    )

    assert response.status_code == 201
    assert Product.objects.count() == 1
    assert response.json()['name'] == 'Notebook'
    assert response.json()['price'] == '14.50'


@pytest.mark.django_db
def test_list_products(api_client, product):
    response = api_client.get(reverse('product-list'))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == product.name


@pytest.mark.django_db
def test_retrieve_product(api_client, product):
    response = api_client.get(reverse('product-detail', args=[product.id]))

    assert response.status_code == 200
    assert response.json()['id'] == product.id
    assert response.json()['name'] == product.name


@pytest.mark.django_db
def test_update_product(api_client, product):
    response = api_client.patch(
        reverse('product-detail', args=[product.id]),
        {'stock': 7, 'price': '44.00'},
        content_type='application/json',
    )

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.stock == 7
    assert product.price == Decimal('44.00')


@pytest.mark.django_db
def test_delete_product(api_client, product):
    response = api_client.delete(reverse('product-detail', args=[product.id]))

    assert response.status_code == 204
    assert Product.objects.count() == 0


@pytest.mark.django_db
def test_rejects_negative_price(api_client):
    response = api_client.post(
        reverse('product-list'),
        {
            'name': 'Invalid Product',
            'price': '-1.00',
            'stock': 3,
        },
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'price' in response.json()
