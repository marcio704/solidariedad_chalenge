# encoding: utf-8

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from bank.models import *
from bank.serializers import *


class AccountViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
    A viewset for viewing Account instances.
    """
    queryset = Conta.objects.all()

    def get_serializer_class(self):
        """
        Returns the right serializer for the given HTTP method
        :return:
        """
        if self.action == 'retrieve':
            return ContaRetrieveSerializer

        return ContaSerializer

    @detail_route(methods=["POST"], url_path="saque")
    def withdraw(self, request, *args, **kwargs):
        """
        Withdraws the given amount from current Account.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        account = self.get_object()
        account_serializer = self.get_serializer()
        value = request.data.get("valor", None)

        try:
            withdraw_result = account_serializer.withdraw(value, account)
        except ValueError as ve:
            return Response({"detail": "Could not withdraw: {0}.".format(ve),
                             "status_code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        return Response(withdraw_result)

    @detail_route(methods=["GET"], url_path="extrato")
    def history(self, request, *args, **kwargs):
        """
        Shows account transactions history.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        account = self.get_object()

        try:
            history = HistoricoConta.objects.filter(conta=account).order_by('-created')
        except ObjectDoesNotExist as obj:
            return Response({"detail": "Could not find history for thus account",
                             "status_code": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

        return Response(HistoricoContaSerializer(history, many=True).data)

    @detail_route(methods=["POST"], url_path="transferencia")
    def transfer(self, request, *args, **kwargs):
        """
        Transfers a given amount from one account to other.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        origin_account = self.get_object()
        destiny_account = request.data.get("id_conta", None)
        amount = request.data.get("valor", None)
        account_serializer = self.get_serializer()

        try:
            transfer = account_serializer.transfer(origin_account, destiny_account, amount)
        except ObjectDoesNotExist as obj:
            return Response({"detail": "Could not transfer the amount: Destiny account does not exist.",
                             "status_code": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as ve:
            return Response({"detail": "Could not transfer the amount: {0}.".format(ve),
                             "status_code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        return Response(transfer)


class ATMViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    """
    A viewset for viewing ATM instance.
    """
    queryset = ATM.objects.all()
    serializer_class = ATMSerializer

    def list(self, request, *args, **kwargs):
        """
        Rewriting list method in order to have a custom json output
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        atm = ATM.objects.all()
        return Response({registro.cedula.valor: registro.quantidade for registro in atm})

    def create(self, request, *args, **kwargs):
        """
        Rewriting create method in order to have a custom json input/outpu
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        atm_serializer = self.get_serializer()
        atm = atm_serializer.create(request.data)

        return Response(atm)


@csrf_exempt
def index(request):
    """
    Displays home page
    :param request:
    :return:
    """
    return render(request, 'domain/banco.html')
