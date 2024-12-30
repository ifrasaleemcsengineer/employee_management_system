from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from employees.models import Employee

PERMISSION_MAPPING = {
    "employee_list": {"view_name": "EmployeeViewSet", "action": "list"},
    "employee_update": {"view_name": "EmployeeViewSet", "action": "update"},
    "employee_create": {"view_name": "EmployeeViewSet", "action": "create"},
    "employee_destroy": {"view_name": "EmployeeViewSet", "action": "destroy"},
    "salary_view_all": {"view_name": "SalaryViewSet", "action": "list"},
    "salary_update": {"view_name": "SalaryViewSet", "action": "update"},
    "salary_delete": {"view_name": "SalaryViewSet", "action": "destroy"},
    "leave_view_all": {"view_name": "LeaveViewSet", "action": "list"},
    "leave_update_status": {"view_name": "LeaveViewSet", "action": "update"},
    "leave_delete": {"view_name": "LeaveViewSet", "action": "destroy"},
    "department_create": {"view_name": "DepartmentViewSet", "action": "create"},
    "department_view_all": {"view_name": "DepartmentViewSet", "action": "list"},
    "department_delete": {"view_name": "DepartmentViewSet", "action": "destroy"},
    "department_update": {"view_name": "DepartmentViewSet", "action": "update"},
}

class DynamicRolePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self._raise_permission_denied("You must be logged in to perform this action.")

        if request.user.is_admin:
            return True

        view_name = view.__class__.__name__
        action = view.action
        employee_id = request.query_params.get("employee_id")

        required_permission = self._get_required_permission(view_name, action)
        if required_permission and self._check_role_permission(request.user, required_permission):
            return True

        if view_name in ["EmployeeViewSet", "LeaveViewSet", "SalaryViewSet"]:
            if employee_id:
                if self._is_own_employee(request.user, employee_id):
                    return True
                self._raise_permission_denied("You do not have permission to access this employee's data.")

            if action == "create" and view_name == "LeaveViewSet":
                employee_id = request.data.get("employee")
                if employee_id and self._is_own_employee(request.user, employee_id):
                    return True

        self._raise_permission_denied("You do not have permission to perform this action.")

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True

        if hasattr(obj, "user") and obj.user == request.user:
            return True
        if hasattr(obj, "employee") and obj.employee.user == request.user:
            return True

        user_role = getattr(request.user, "role", None)
        if user_role:
            view_name = view.__class__.__name__
            action = view.action
            required_permission = self._get_required_permission(view_name, action)
            if required_permission and required_permission in (user_role.permissions or []):
                return True

        self._raise_permission_denied("You do not have permission to perform this action.")

    def _is_own_employee(self, user, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
            return employee.user == user
        except Employee.DoesNotExist:
            self._raise_permission_denied(f"Employee with ID {employee_id} does not exist.")

    def _get_required_permission(self, view_name, action):
        if action in ["retrieve", "partial_update"]:
            action = "update"  
        if action == "retrieve":
            action = "list" 
        for perm_key, mapping in PERMISSION_MAPPING.items():
            if mapping["view_name"] == view_name and mapping["action"] == action:
                return perm_key
        return None

    def _check_role_permission(self, user, permission):
        user_role = getattr(user, "role", None)
        if user_role and permission in (user_role.permissions or []):
            return True
        return False

    def _raise_permission_denied(self, message):
        raise PermissionDenied(detail=message)



class CustomUserPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "create" and request.data.get("is_admin", False):
            return True
        if view.action in ["list", "destroy"]:
            return request.user.is_authenticated and request.user.is_admin
        if view.action in ["retrieve", "update", "partial_update"]:
            return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if view.action in ["retrieve", "update", "partial_update"]:
            return obj == request.user
        return False


