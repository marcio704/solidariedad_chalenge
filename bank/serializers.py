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
def withdraw(value, conta):
    """
    Withdraw current amount from given account
    :param value:
    :param conta:
    :return:
    """
    if value is None:
        raise ValueError("The following fields are mandatory: [valor]")
    if type(value) is not int:
        raise ValueError("Field 'valor' must be an integer")
    if value < 0:
        raise ValueError("Field 'valor' must be positive")
    if value > conta.saldo:
        raise ValueError("The given account doesn't have enough balance")

    atm = ATM.objects.all().order_by('-cedula__valor')
    cedulas = {str(item.cedula.valor): 0 for item in atm}
    cedulas = collections.OrderedDict(cedulas)
    current_amount_missing = value

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

    # Decrease used bank notes from database all at once together in a unique transaction:
    with transaction.atomic():
        for registro_atm in atm:
            registro_atm.save()

    return cedulas


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
                registros_atm[str(registro_atm.cedula.valor)] = str(registro_atm.quantidade)

        return registros_atm
