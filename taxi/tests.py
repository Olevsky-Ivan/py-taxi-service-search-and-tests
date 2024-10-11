from django.test import TestCase, Client
from taxi.models import Driver, Manufacturer, Car
from taxi.forms import DriverCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse


class DriverTestCase(TestCase):
    def setUp(self):
        self.manufacturer1 = Manufacturer.objects.create(name="Ivan")
        self.manufacturer2 = Manufacturer.objects.create(name="Alex")
        self.car1 = (Car.objects.create
                     (model="BMW",
                      manufacturer=self.manufacturer1)
                     )
        self.car2 = Car.objects.create(
            model="Mercedes",
            manufacturer=self.manufacturer2
        )
        self.driver1 = Driver.objects.create(
            username="driver1",
            license_number="tes12345"
        )
        self.driver2 = Driver.objects.create(
            username="driver2",
            license_number="tes23456"
        )

    def test_car_list(self):
        self.car1.drivers.set([self.driver1])
        self.car2.drivers.set([self.driver2])
        response = self.client.get(CAR_LIST_URL)
        self.assertEqual(response.status_code, 302)


class AdminTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="password1",
        )
        self.client.force_login(self.admin_user)
        self.driver = get_user_model().objects.create_superuser(
            username="Karina",
            password="password",
            license_number="tes01234"
        )

    def test_admin_listed(self):
        url = reverse("admin:taxi_driver_changelist")
        res = self.client.get(url)
        self.assertContains(res, self.driver.username)

    def test_admin_listed_detail(self):
        url = reverse("admin:taxi_driver_change", args=[self.driver.id])
        res = self.client.get(url)
        self.assertContains(res, self.driver.username)


class FormTestCase(TestCase):
    def test_driver_creation_form_valid(self):
        form_data = {
            "username": "test_user",
            "password1": "StrongP@ssw0rd!",
            "password2": "StrongP@ssw0rd!",
            "first_name": "Test",
            "last_name": "User",
            "email": "test_user@example.com",
            "license_number": "ABC12345",
        }
        form = DriverCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["license_number"], "ABC12345")
        print(form.cleaned_data)


CAR_LIST_URL = reverse("taxi:car-list")


class PublicCarListTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_required(self):
        res = self.client.get(CAR_LIST_URL)
        self.assertEqual(res.status_code, 302)


class PrivateCarListTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test_password",
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )
        self.client.force_login(self.user)

        manufacturer1 = Manufacturer.objects.create(name="Ivan")
        manufacturer2 = Manufacturer.objects.create(name="Alex")
        self.car1 = Car.objects.create(model="BMW", manufacturer=manufacturer1)
        self.car2 = Car.objects.create(
            model="Mercedes",
            manufacturer=manufacturer2
        )

    def test_retrieve_car_list(self):
        response = self.client.get(reverse("taxi:car-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BMW")
        self.assertContains(response, "Mercedes")
