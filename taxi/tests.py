from django.test import TestCase, Client
from taxi.models import Driver, Manufacturer, Car
from taxi.forms import DriverCreationForm
from django.contrib.auth import get_user_model
from django.urls import reverse


class ModelsTests(TestCase):
    def test_driver_str(self):
        driver = get_user_model().objects.create(
            username="leleka",
            password="password",
            first_name="Ivan",
            last_name="Olevsky",
            email="ivan@example.com",
            license_number="AB123456789"
        )
        self.assertEqual(
            str(driver),
            f"{driver.username} ({driver.first_name} {driver.last_name})")

    def test_driver_with_license_number(self):
        password = "TEST PASSWORD"
        username = "Alexov"
        first_name = "Alex"
        last_name = "Statham"
        email = "alex@example.com"
        license_number = "1234567890"

        driver = Driver.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            license_number=license_number,
        )
        self.assertEqual(str(driver.license_number), license_number)
        self.assertTrue(driver.check_password(password))
        self.assertEqual(driver.get_full_name(), f"{first_name} {last_name}")

    def test_manufacturer_str(self):
        name = "Ivan"
        country = "Ukraine"

        manufacturer = Manufacturer.objects.create(name=name, country=country)
        self.assertEqual(
            str(manufacturer),
            f"{manufacturer.name} {manufacturer.country}")


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
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")
        print(form.cleaned_data)


CAR_LIST_URL = reverse("taxi:car-list")


class PublicCarListTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_login_required(self):
        res = self.client.get(CAR_LIST_URL)
        self.assertNotEqual(res.status_code, 200)


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

    def test_retrieve_car_list(self):
        manufacturer1 = Manufacturer.objects.create(name="Ivan")
        manufacturer2 = Manufacturer.objects.create(name="Alex")

        car1 = Car.objects.create(
            model="BMW",
            manufacturer=manufacturer1
        )
        car2 = Car.objects.create(
            model="Mercedes",
            manufacturer=manufacturer2
        )

        driver1 = Driver.objects.create(
            username="driver1",
            license_number="tes12345"
        )
        driver2 = Driver.objects.create(
            username="driver2",
            license_number="tes23456"
        )

        car1.drivers.set([driver1])
        car2.drivers.set([driver2])

        response = self.client.get(CAR_LIST_URL)
        self.assertEqual(response.status_code, 200)
