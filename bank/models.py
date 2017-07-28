# encoding: utf-8

from django.db import models
from django_extensions.db.models import TimeStampedModel


class Conta(TimeStampedModel):
    nome = models.CharField(max_length=150, null=False, blank=False, db_index=True)
    saldo = models.FloatField(default=0, null=False, blank=False)

    __saldo_original = None

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "%s: %s" % (self.nome, self.saldo)

    def __init__(self, *args, **kwargs):
        super(Conta, self).__init__(*args, **kwargs)
        self.__saldo_original = self.saldo


class Cedula(TimeStampedModel):
    valor = models.IntegerField(null=False, blank=False, unique=True)
    descricao = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        ordering = ['valor']

    def __str__(self):
        return "%s: %s" % (self.valor, self.descricao)


class ATM(TimeStampedModel):
    cedula = models.ForeignKey(Cedula, null=False, blank=False, unique=True)
    quantidade = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "%s: %s" % (self.cedula.descricao, self.quantidade)


class HistoricoConta(TimeStampedModel):
    conta = models.ForeignKey(Conta, null=False, blank=False)
    valor = models.FloatField(default=0, null=False, blank=False)
