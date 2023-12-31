"""delicious_erp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

import erp.views as erp


urlpatterns = (
    [
        path("", erp.home),
        path("cost-centers", erp.CostCenterListView.as_view()),
        path("cost-centers/<int:pk>", erp.CostCenterDetailView.as_view(), name='cost-center'),
        path("purchases", erp.PurchasesListView.as_view()),
        path("purchases/<int:pk>", erp.PurchaseDetailView.as_view(), name='purchase'),
        path("purchases/create", erp.PurchaseCreateView.as_view()),
        path("fundings", erp.FundingsListView.as_view()),
        path("fundings/<int:pk>", erp.FundingDetailView.as_view(), name='funding'),
        path("s/<id>", erp.resolve_id),
        path("admin/", admin.site.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
