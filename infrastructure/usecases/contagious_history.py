from datetime import timedelta, date

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from infrastructure.repositories.contagious_history import ContagiousHistoryRepository
from users.models import User


class GetEmployeeStatusContagious:
    def __init__(
        self,
        employee: User,
        repo: ContagiousHistoryRepository,
    ):
        self.employee = employee
        self.repository = repo

    def execute(self) -> QuerySet:

        employee = get_object_or_404(
            User,is_active=True,is_worker=True,id=int(self.employee)
        )

        contagious_history_employee = self.repository.get_contagious_history_by_employee(
            self.employee
        )

        return contagious_history_employee