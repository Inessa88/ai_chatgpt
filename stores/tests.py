import pytest
from django.test import Client
from django.urls import reverse

from .models import Store


@pytest.fixture
def api_client():
    return Client()


@pytest.fixture
def store():
    return Store.objects.create(
        name='Downtown Shop',
        description='Flagship retail location',
        address='123 Main St, Springfield',
        phone='555-0100',
    )


@pytest.mark.django_db
def test_store_string_representation(store):
    assert str(store) == 'Downtown Shop'


@pytest.mark.django_db
def test_create_store(api_client):
    response = api_client.post(
        reverse('store-list'),
        {
            'name': 'Westside Branch',
            'description': 'Smaller satellite location',
            'address': '456 West Ave, Springfield',
            'phone': '555-0200',
            'is_active': True,
        },
        content_type='application/json',
    )

    assert response.status_code == 201
    assert Store.objects.count() == 1
    assert response.json()['name'] == 'Westside Branch'
    assert response.json()['address'] == '456 West Ave, Springfield'


@pytest.mark.django_db
def test_list_stores(api_client, store):
    response = api_client.get(reverse('store-list'))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == store.name


@pytest.mark.django_db
def test_retrieve_store(api_client, store):
    response = api_client.get(reverse('store-detail', args=[store.id]))

    assert response.status_code == 200
    assert response.json()['id'] == store.id
    assert response.json()['name'] == store.name


@pytest.mark.django_db
def test_update_store(api_client, store):
    response = api_client.patch(
        reverse('store-detail', args=[store.id]),
        {'phone': '555-9999', 'address': '789 New Rd, Springfield'},
        content_type='application/json',
    )

    assert response.status_code == 200
    store.refresh_from_db()
    assert store.phone == '555-9999'
    assert store.address == '789 New Rd, Springfield'


@pytest.mark.django_db
def test_delete_store(api_client, store):
    response = api_client.delete(reverse('store-detail', args=[store.id]))

    assert response.status_code == 204
    assert Store.objects.count() == 0


@pytest.mark.django_db
def test_rejects_missing_address(api_client):
    response = api_client.post(
        reverse('store-list'),
        {'name': 'Incomplete Store'},
        content_type='application/json',
    )

    assert response.status_code == 400
    assert 'address' in response.json()
