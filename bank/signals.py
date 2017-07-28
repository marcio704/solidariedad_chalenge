# encode: utf-8

from django.db.models.signals import post_save
from django.dispatch import receiver

from bank.models import Conta, HistoricoConta


@receiver(post_save, sender=Conta)
def save_account_transaction_history(sender, instance, created, **kwargs):
    """
    Saves transaction history for the given account
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if instance._Conta__saldo_original == instance.saldo:
        return

    transaction_value = abs(instance._Conta__saldo_original - instance.saldo)
    if instance._Conta__saldo_original > instance.saldo:
        transaction_value *= -1

    transaction = HistoricoConta(conta=instance, valor=transaction_value)
    transaction.save()
