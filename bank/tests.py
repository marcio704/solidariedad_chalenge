# encode: utf-8

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from bank.models import *


class AccountAPITests(APITestCase):

    def setUp(self):
        """
        Setting up things before tests.
        :return:
        """

        # Creating Accounts for testing purposes.
        self.account_1 = Conta(nome="Teste 1", saldo=18)
        self.account_1.save()

        self.account_2 = Conta(nome="Teste 2", saldo=170)
        self.account_2.save()

        # Creating Cedulas for testing purposes.
        self.bank_note_1 = Cedula(valor=1, descricao="1 Real")
        self.bank_note_1.save()

        self.bank_note_2 = Cedula(valor=2, descricao="2 Reais")
        self.bank_note_2.save()

        self.bank_note_5 = Cedula(valor=5, descricao="5 Reais")
        self.bank_note_5.save()

        self.bank_note_10 = Cedula(valor=10, descricao="10 Reais")
        self.bank_note_10.save()

        self.bank_note_20 = Cedula(valor=20, descricao="20 Reais")
        self.bank_note_20.save()

        self.bank_note_50 = Cedula(valor=50, descricao="50 Reais")
        self.bank_note_50.save()

        self.bank_note_100 = Cedula(valor=100, descricao="100 Reais")
        self.bank_note_100.save()

        # Creating ATM charges
        self.atm_record_1 = ATM(cedula=self.bank_note_1, quantidade=1)
        self.atm_record_1.save()

        self.atm_record_2 = ATM(cedula=self.bank_note_2, quantidade=1)
        self.atm_record_2.save()

        self.atm_record_5 = ATM(cedula=self.bank_note_5, quantidade=1)
        self.atm_record_5.save()

        self.atm_record_10 = ATM(cedula=self.bank_note_10, quantidade=1)
        self.atm_record_10.save()

        self.atm_record_20 = ATM(cedula=self.bank_note_20, quantidade=1)
        self.atm_record_20.save()

        self.atm_record_50 = ATM(cedula=self.bank_note_50, quantidade=1)
        self.atm_record_50.save()

        self.atm_record_100 = ATM(cedula=self.bank_note_100, quantidade=1)
        self.atm_record_100.save()

    def test_get_api_200_list(self):
        """
        Tests GET (retrieve) API for status code 200.
        """
        url = reverse('bank:account-list')
        response = self.client.get(url)
        data = response.json()

        account_data = data[0]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(account_data['id'], self.account_1.id)
        self.assertEqual(account_data['nome'], self.account_1.nome)
        self.assertEqual(account_data['saldo'], self.account_1.saldo)

    def test_get_api_200_retrieve(self):
        """
        Tests GET (retrieve) API for status code 200.
        """
        url = reverse('bank:account-detail', kwargs={'pk': self.account_2.id})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['nome'], self.account_2.nome)
        self.assertEqual(data['saldo'], self.account_2.saldo)

    def test_get_api_invalid_pk_404(self):
        """
        Tests GET (retrieve) API for status code 404.
        """
        url = reverse('bank:account-detail', kwargs={'pk': 9999999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_api_200(self):
        """
        Tests POST API for status code 200.
        :return:
        """
        url = reverse('bank:account-list')

        # JSON (payload)
        data = {
            "nome": "Marcio Santiago",
            "saldo": "863"
        }

        response = self.client.post(url, data=data, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(data['id'])
        self.assertEqual(data['nome'], "Marcio Santiago")
        self.assertEqual(data['saldo'], 863)

    def test_post_api_400(self):
        """
        Tests POST API for status code 400.
        :return:
        """
        url = reverse('bank:account-list')

        # JSON (payload)
        data = {
            "saldo": "863"
        }

        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_api_withdraw(self):
        """
        Tests withdraw endpoint API.
        """
        data = {
            "valor": 18
        }
        url = reverse('bank:account-detail', kwargs={'pk': self.account_1.id})
        response = self.client.post(url + "saque/", data=data, format="json")

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['1'], 1)
        self.assertEqual(data['2'], 1)
        self.assertEqual(data['5'], 1)
        self.assertEqual(data['10'], 1)
        self.assertEqual(data['20'], 0)
        self.assertEqual(data['50'], 0)
        self.assertEqual(data['100'], 0)

        # Try to withdraw again, this user no longer has balance
        data = {
            "valor": 50
        }
        url = reverse('bank:account-detail', kwargs={'pk': self.account_1.id})
        response = self.client.post(url + "saque/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Withdraw 70 for account_2
        data = {
            "valor": 70
        }
        url = reverse('bank:account-detail', kwargs={'pk': self.account_2.id})
        response = self.client.post(url + "saque/", data=data, format="json")

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['1'], 0)
        self.assertEqual(data['2'], 0)
        self.assertEqual(data['5'], 0)
        self.assertEqual(data['10'], 0)
        self.assertEqual(data['20'], 1)
        self.assertEqual(data['50'], 1)
        self.assertEqual(data['100'], 0)

        # Try to withdraw value that there are no bank_notes combination available (account_2 still have balance):
        data = {
            "valor": 50
        }
        url = reverse('bank:account-detail', kwargs={'pk': self.account_2.id})
        response = self.client.post(url + "saque/", data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Withdraw the rest balance with the last 100 bank note available:
        data = {
            "valor": 100
        }
        url = reverse('bank:account-detail', kwargs={'pk': self.account_2.id})
        response = self.client.post(url + "saque/", data=data, format="json")

        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['1'], 0)
        self.assertEqual(data['2'], 0)
        self.assertEqual(data['5'], 0)
        self.assertEqual(data['10'], 0)
        self.assertEqual(data['20'], 0)
        self.assertEqual(data['50'], 0)
        self.assertEqual(data['100'], 1)


class ATMAPITests(APITestCase):

    def setUp(self):
        """
        Setting up things before tests.
        :return:
        """

        # Creating Cedulas for testing purposes.
        self.bank_note_1 = Cedula(valor=1, descricao="1 Real")
        self.bank_note_1.save()

        self.bank_note_2 = Cedula(valor=2, descricao="2 Reais")
        self.bank_note_2.save()

        self.bank_note_5 = Cedula(valor=5, descricao="5 Reais")
        self.bank_note_5.save()

        self.bank_note_10 = Cedula(valor=10, descricao="10 Reais")
        self.bank_note_10.save()

        self.bank_note_20 = Cedula(valor=20, descricao="20 Reais")
        self.bank_note_20.save()

        self.bank_note_50 = Cedula(valor=50, descricao="50 Reais")
        self.bank_note_50.save()

        self.bank_note_100 = Cedula(valor=100, descricao="100 Reais")
        self.bank_note_100.save()

        # Creating ATM charges
        self.atm_record_1 = ATM(cedula=self.bank_note_1, quantidade=10)
        self.atm_record_1.save()

        self.atm_record_2 = ATM(cedula=self.bank_note_2, quantidade=10)
        self.atm_record_2.save()

        self.atm_record_5 = ATM(cedula=self.bank_note_5, quantidade=10)
        self.atm_record_5.save()

        self.atm_record_10 = ATM(cedula=self.bank_note_10, quantidade=10)
        self.atm_record_10.save()

        self.atm_record_20 = ATM(cedula=self.bank_note_20, quantidade=10)
        self.atm_record_20.save()

        self.atm_record_50 = ATM(cedula=self.bank_note_50, quantidade=10)
        self.atm_record_50.save()

        self.atm_record_100 = ATM(cedula=self.bank_note_100, quantidade=10)
        self.atm_record_100.save()

    def test_get_api_200_list(self):
        """
        Tests GET API for status code 200.
        """
        url = reverse('bank:atm-list')
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['1'], 10)
        self.assertEqual(data['2'], 10)
        self.assertEqual(data['5'], 10)
        self.assertEqual(data['10'], 10)
        self.assertEqual(data['20'], 10)
        self.assertEqual(data['50'], 10)
        self.assertEqual(data['100'], 10)

    def test_post_api_200(self):
        """
        Tests POST API for status code 200.
        :return:
        """
        url = reverse('bank:atm-list')

        # JSON (payload)
        data = {
            "1": 1,
            "2": 1,
            "5": 1,
            "10": 1,
            "20": 1,
            "50": 1,
            "100": 1
        }

        response = self.client.post(url, data=data, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['1'], 1)
        self.assertEqual(data['2'], 1)
        self.assertEqual(data['5'], 1)
        self.assertEqual(data['10'], 1)
        self.assertEqual(data['20'], 1)
        self.assertEqual(data['50'], 1)
        self.assertEqual(data['100'], 1)
