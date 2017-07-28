# encoding: utf-8

import collections
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers
from bank.models import *


class ContaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conta
        fields = ('id', 'nome', 'saldo')

    @transaction.atomic
    def withdraw(self, value, conta):
        """
        Withdraw current amount from given account
        :param value:
        :param conta:
        :return:
        """
        self.validate_value(value, conta)
        count = self.count_cedulas(value)

        # Decrease used bank notes from database all at once together in a unique transaction:
        with transaction.atomic():
            # Update Account value:
            conta.saldo -= int(value)
            conta.save()

            # Update ATM:
            for registro_atm in count["atm"]:
                registro_atm.save()

        return count["cedulas"]

    @transaction.atomic
    def transfer(self, origin_account, destiny_account, amount):
        """
        Transfers a given amount from one account to other.
        :param origin_account:
        :param destiny_account:
        :param amount:
        :return:
        """
        self.validate_value(amount, origin_account)
        count = self.count_cedulas(amount)
        destiny_account = Conta.objects.get(id=destiny_account)

        with transaction.atomic():
            origin_account.saldo -= amount
            origin_account.save()

            destiny_account.saldo += amount
            destiny_account.save()

            # Update ATM:
            for registro_atm in count["atm"]:
                registro_atm.save()

        return {"conta_origem_id": origin_account.id, "conta_destino_id": destiny_account.id, "valor": amount}

    @staticmethod
    def validate_value(value, conta):
        if value is None:
            raise ValueError("The following fields are mandatory: [valor]")
        try:
            value = int(value)
        except ValueError:
            raise ValueError("Field 'valor' must be an integer")
        if value < 0:
            raise ValueError("Field 'valor' must be positive")
        if value > conta.saldo:
            raise ValueError("The given account doesn't have enough balance")

    @staticmethod
    def count_cedulas(value):
        """
        Count number of bank notes for the transaction
        :param value:
        :return: dict
        """
        atm = ATM.objects.all().order_by('-cedula__valor')
        cedulas = collections.OrderedDict({str(item.cedula.valor): 0 for item in atm})
        current_amount_missing = int(value)

        # Count number of bank notes:
        for registro_atm in atm:
            if registro_atm.quantidade == 0:
                continue

            num = current_amount_missing / registro_atm.cedula.valor
            if num > 0 and num < 1:
                continue
            elif num == 1:
                registro_atm.quantidade -= 1
                cedulas[str(registro_atm.cedula.valor)] += 1
                current_amount_missing -= registro_atm.cedula.valor
                break
            else:
                registro_atm.quantidade -= int(num)
                if registro_atm.quantidade < 0:
                    break
                cedulas[str(registro_atm.cedula.valor)] += int(num)
                current_amount_missing -= registro_atm.cedula.valor * int(num)

        if current_amount_missing > 0:
            raise ValueError("Not enough bank notes")

        return {"atm": atm, "cedulas": cedulas}


class ContaRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conta
        fields = ('nome', 'saldo')


class CedulaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cedula
        fields = ('valor', )


class ATMSerializer(serializers.ModelSerializer):
    valor = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ATM
        fields = ('valor', 'quantidade')

    @staticmethod
    def get_valor(instance):
        return instance.cedula.valor

    @transaction.atomic
    def create(self, validated_data):
        with transaction.atomic():
            registros_atm = {}
            for (valor, quantidade) in validated_data.items():
                try:
                    registro_atm = ATM.objects.get(cedula__valor=valor)
                    registro_atm.quantidade = quantidade

                except ObjectDoesNotExist:
                    cedula = Cedula.objects.get(valor=valor)
                    registro_atm = ATM(cedula=cedula, quantidade=quantidade)

                registro_atm.save()
                registros_atm[str(registro_atm.cedula.valor)] = registro_atm.quantidade

        return registros_atm


class HistoricoContaSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = HistoricoConta
        fields = ('id', 'valor', 'date')

    @staticmethod
    def get_date(instance):
        return instance.created
