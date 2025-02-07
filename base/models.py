from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

# Create your models here.

class Book(models.Model):
    TYPE_CHOICES = [
        (1, 'Up to 10 days'),
        (2, 'Up to 5 days'),
        (3, 'Up to 2 days'),
    ]

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    year_published = models.IntegerField()
    type = models.IntegerField(choices=TYPE_CHOICES)
    image = models.ImageField(null=True, blank=True, default='/placeholder.png')
    active = models.BooleanField(default=True)  # Add this field to track active/inactive status

    def __str__(self):
        return self.title


class Loan(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_staff': False}  # Only non-staff users can be selected
    )
    loan_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)  # Add this field to track active/inactive status

    def __str__(self):
        return f'Loan of {self.book.title} to {self.customer.username}'

    def save(self, *args, **kwargs):
        # Automatically calculate the return date based on the book type
        if not self.return_date:  # Only set if not already set
            loan_duration_map = {
                1: timedelta(days=10),  # Type 1 -> 10 days
                2: timedelta(days=5),   # Type 2 -> 5 days
                3: timedelta(days=2),   # Type 3 -> 2 days
            }
            # Set the return date based on the book's type
            self.return_date = self.loan_date + loan_duration_map.get(self.book.type, timedelta(days=0))
        
        super(Loan, self).save(*args, **kwargs)

