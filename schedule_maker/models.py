from django.db import models
from .process_data import create_classes


class Student(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    islamic = models.BooleanField()
    gender_types = [
        ('M', 'Male'),
        ('F', 'Female')
                    ]
    gender = models.CharField(max_length=6, choices=gender_types, default='M')
    behavior = models.BooleanField()
    friend1 = models.IntegerField()
    friend2 = models.IntegerField()
    friend3 = models.IntegerField()
    friend4 = models.IntegerField()
    friend5 = models.IntegerField()

    def __str__(self):
        return self.first_name + " " + self.last_name

    @staticmethod
    def distribute_to_classes():
        students = list(Student.objects.values('first_name', 'last_name', 'islamic', 'behavior', 'gender', 'friend1', 'friend2', 'friend3', 'friend4', 'friend5', 'id'))
        students = [list(x.values()) for x in students]
        return create_classes(students)

