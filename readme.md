# Library Management System
This project is a Library Management System built using Django for the backend, HTML with Axios for the frontend, and SQLite for the database. The system allows users to manage books, loans, and users with different roles (staff and non-staff). It includes functionalities like book registration, loan creation, loan tracking, and overdue loan management.

# Features
## Backend (Django)
Authentication and Authorization:

Custom JWT authentication with rest_framework_simplejwt.
Role-based access control for staff and non-staff users.
Book Management:

CRUD operations for books (create, read, update, delete).
Books can be marked as active/inactive.
Loan Management:

Loan creation, return, and update functionality.
Loans can be tracked with due dates.
Overdue loan tracking.
User Management:

Register staff and non-staff users.
Login functionality with JWT token generation.
Overdue Loan Detection:

Identify overdue loans for staff and non-staff users.

## Frontend (HTML & Axios)
Interface to interact with the Django backend via API requests using Axios.
Allows users to view books, create loans, return books, and view their active/inactive loans.
Database (SQLite)
SQLite database to store user information, books, and loans.

## Clone the repository:
git clone https://github.com/yourusername/library-management-system.git