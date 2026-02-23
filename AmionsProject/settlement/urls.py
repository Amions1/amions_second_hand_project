from django.contrib import admin
from django.urls import path
from settlement.views import SettlementView, PaySuccess, SettlementSuccessView

urlpatterns = [
    path('', SettlementView.as_view(), name='SettlementView'),
    path('paysuccess/', PaySuccess.as_view(), name='PaySuccess'),
    path('settlementSuccess/', SettlementSuccessView.as_view(), name='SettlementSuccessView'),

]