from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser
from .models import Branch, Department
from .serializers import BranchStructureSerializer, DepartmentStructureSerializer
from .permissions import IsBranchHeadOrAdmin, IsDepartmentOrBranchHeadOrAdmin


class BranchStructureAPIView(RetrieveAPIView):
    """Полная структура конкретного филиала — для admin или начальника этого филиала."""
    queryset = Branch.objects.prefetch_related("departments__employees__user", "head")
    serializer_class = BranchStructureSerializer
    permission_classes = [IsBranchHeadOrAdmin]


class DepartmentStructureAPIView(RetrieveAPIView):
    """Структура конкретного отдела — для admin, начальника отдела или начальника филиала."""
    queryset = Department.objects.select_related("branch", "head").prefetch_related("employees__user")
    serializer_class = DepartmentStructureSerializer
    permission_classes = [IsDepartmentOrBranchHeadOrAdmin]


class BranchListAPIView(ListAPIView):
    """Список всех филиалов со структурой — только для admin/staff."""
    queryset = Branch.objects.prefetch_related("departments__employees__user", "head")
    serializer_class = BranchStructureSerializer
    permission_classes = [IsAdminUser]