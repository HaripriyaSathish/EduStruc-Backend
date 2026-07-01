from django.db import models

class Schedule(models.Model):
    DAY_CHOICES = [
        ('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),
        ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),
    ]
    course_name  = models.CharField(max_length=200)
    instructor   = models.CharField(max_length=100)
    day          = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time   = models.TimeField()
    end_time     = models.TimeField()
    room         = models.CharField(max_length=50)
    academic_year= models.CharField(max_length=20)
    semester     = models.CharField(max_length=20)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_name} - {self.day} {self.start_time}"
