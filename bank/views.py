# encoding: utf-8

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
        conta = self.get_object()
        conta_serializer = self.get_serializer()
        value = request.data.get("valor", None)

        try:
            withdraw_result = conta_serializer.withdraw(value, conta)
        except ValueError as ve:
            return Response({"detail": "Could not withdraw: {0}.".format(ve),
                             "status_code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        return Response(withdraw_result)


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
