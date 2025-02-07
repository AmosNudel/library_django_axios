from django.urls import path
from . import views
from .views import MyTokenObtainPairView 

urlpatterns = [
    path('', views.index),
     path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Use the view class
    path('register-staff', views.register_staff),
    path('register', views.register),
    path('books/', views.get_books, name='get_books'),  # Get all books
    # Get book by title
    path('books/<str:title>/', views.get_book, name='get_book_by_title'),  # Get specific book
    path('book/update/<int:book_id>/', views.get_book_by_id, name='get_book_by_id'),
    path('book/create/', views.create_book, name='create_book'),  # Create new book
    path('book/upd/<int:pk>/', views.update_book, name='update_book'),  # Update book
    path('book/delete/<int:pk>/', views.delete_book, name='delete_book'),  # Delete book
    # Non-staff can create a loan (borrow a book)
    path('loan/create/', views.create_loan, name='create_loan'),

    # Non-staff can return (delete) a loan
    path('loan/return/<int:pk>/', views.return_loan, name='return_loan'),

    # Staff can update a loan (e.g., changing return date or other updates)
    path('loan/update/<int:pk>/', views.update_loan, name='update_loan'),
    # Staff can view all loans
    path('loans/all/', views.get_loans_for_staff, name='get_loans_for_staff'),
    
    path('loan/<int:loan_id>/', views.get_loan_by_id, name='get_loan_by_id'),  # URL to get a loan by its ID

    # Non-staff users can view their own loans
    path('loans/my/', views.get_loans_for_user, name='get_loans_for_user'),
    # Endpoint for staff to view overdue loans
    path('staff/overdue-loans/', views.get_overdue_loans, name='staff-overdue-loans'),
    
    # Endpoint for non-staff users (customers) to view their own overdue loans
    path('user/overdue-loans/', views.get_overdue_loans_for_user, name='user-overdue-loans'),
]
