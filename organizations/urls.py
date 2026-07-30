from django.urls import path
from .views import BranchStructureAPIView, DepartmentStructureAPIView, BranchListAPIView

urlpatterns = [
    path("branches/", BranchListAPIView.as_view(), name="branch-list"),
    path("branches/<int:pk>/structure/", BranchStructureAPIView.as_view(), name="branch-structure"),
    path("departments/<int:pk>/structure/", DepartmentStructureAPIView.as_view(), name="department-structure"),
]