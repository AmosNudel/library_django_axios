from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth.models import User
from base.models import Book, Loan
from base.serializer import BookSerializer, LoanSerializer
from rest_framework import status
from django.utils import timezone


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        # Only allow staff users
        return request.user.is_authenticated and request.user.is_staff


# login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_staff'] = user.is_staff  # Adding custom field
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def index(req):
    return Response('hello')

# register Staff
@api_view(['POST'])
def register_staff(request):
    user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password']
            )
    user.is_active = True
    user.is_staff = True
    user.save()
    return Response("new staff user born")

# register not Staff
@api_view(['POST'])
def register(request):
    user = User.objects.create_user(
                username=request.data['username'],
                email=request.data['email'],
                password=request.data['password']
            )
    user.is_active = True
    user.is_staff = False
    user.save()
    return Response("new user born")

@api_view(['GET']) 
def get_books(request):
    books = Book.objects.all()  # Get all books
    # Get all active books (where 'active' is True)
    books = Book.objects.filter(active=True)  # Filter books to only get active ones
    serializer = BookSerializer(books, many=True)  # Serialize the data
    return Response(serializer.data)  # Return serialized data

@api_view(['GET'])
def get_book(request, title):
    try:
        # Query the book by its title (case-insensitive)
        book = Book.objects.get(title__iexact=title, active=True)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookSerializer(book)  # Serialize the data
    return Response(serializer.data)  # Return serialized data

@api_view(['GET'])
def get_book_by_id(request, book_id):
    try:
        # Query the book by its id
        book = Book.objects.get(id=book_id, active=True)
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = BookSerializer(book)  # Serialize the data
    return Response(serializer.data)  # Return serialized data


@api_view(['POST'])
@permission_classes([IsStaff])  # Only staff can create books
def create_book(request):
    print(request.data)
    serializer = BookSerializer(data=request.data)  # Deserialize the input data
    if serializer.is_valid():  # Validate input
        serializer.save()  # Save new book
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # Return the created book
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Validation failed

@api_view(['PUT'])
@permission_classes([IsStaff])  # Only staff can update books
def update_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)  # Find the book
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = BookSerializer(book, data=request.data)  # Deserialize with data to update
    if serializer.is_valid():  # Validate input
        serializer.save()  # Save changes
        return Response(serializer.data)  # Return updated data
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Validation failed

@api_view(['DELETE'])
@permission_classes([IsStaff])  # Only staff can change the book's active status
def delete_book(request, pk):
    try:
        book = Book.objects.get(pk=pk)  # Find the book
    except Book.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Set the book's 'active' status to False
    book.active = False
    book.save()  # Save the changes
    
    return Response({"detail": "Book marked as inactive successfully."}, status=status.HTTP_200_OK)  # Return success message


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_loan(request):
    # Ensure the user is either staff or non-staff
    if request.user.is_staff:
        # If the user is staff, they can choose a non-staff user as the customer by name and email
        customer_name = request.data.get('customer_name')
        customer_email = request.data.get('customer_email')
        
        if not customer_name or not customer_email:
            return Response({"detail": "Customer name and email must be specified."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try to find the customer by name and email (non-staff users only)
            customer = User.objects.get(username=customer_name, email=customer_email, is_staff=False)
        except User.DoesNotExist:
            return Response({"detail": "Customer with the provided name and email must be a non-staff user and must exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the book by title (instead of id) and ensure it is active
        book_title = request.data.get('book_title')
        if not book_title:
            return Response({"detail": "Book title must be specified."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(title__iexact=book_title, active=True)  # Ensure the book is active
        except Book.DoesNotExist:
            return Response({"detail": "Book not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the loan with the selected non-staff customer
        data = {
            'book': book.id,  # Use the book ID in the loan
            'customer': customer.id,  # Set the non-staff customer
        }

    else:
        # If the user is non-staff, automatically set customer to the logged-in user
        book_title = request.data.get('book_title')
        if not book_title:
            return Response({"detail": "Book title must be specified."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(title__iexact=book_title, active=True)  # Ensure the book is active
        except Book.DoesNotExist:
            return Response({"detail": "Book not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'book': book.id,  # Use the book ID in the loan
            'customer': request.user.id,  # Non-staff user creates the loan for themselves
        }

    # Serialize the data
    serializer = LoanSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def return_loan(request, pk):
    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response({"detail": "Loan not found or you are not authorized to return this loan."}, status=status.HTTP_404_NOT_FOUND)
    
    # Mark the loan as inactive instead of deleting it
    loan.active = False  # Assuming you have an `active` field, if not add one to the Loan model
    loan.save()  # Save the updated loan instance

    return Response({"detail": "Loan returned successfully."}, status=status.HTTP_200_OK)  # Return success message


@api_view(['PUT'])
@permission_classes([IsStaff])
def update_loan(request, pk):
    if not request.user.is_staff:
        return Response({"detail": "Only staff can update loans."}, status=status.HTTP_403_FORBIDDEN)

    try:
        loan = Loan.objects.get(pk=pk)
    except Loan.DoesNotExist:
        return Response({"detail": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the book title and customer username from request data (if provided)
    book_title = request.data.get('book_title')
    customer_username = request.data.get('customer_username')

    # Update book title if provided
    if book_title:
        try:
            book = Book.objects.get(title__iexact=book_title, active=True)  # Ensure the book is active
            loan.book = book
        except Book.DoesNotExist:
            return Response({"detail": "Book not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)

    # Update customer username if provided
    if customer_username:
        try:
            customer = User.objects.get(username=customer_username, is_staff=False)  # Ensure non-staff user
            loan.customer = customer
        except User.DoesNotExist:
            return Response({"detail": "Customer not found or inactive."}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize the loan data with the updates
    serializer = LoanSerializer(loan, data=request.data, partial=True)  # partial=True means we don't need to send all fields
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsStaff])
def get_loans_for_staff(request):
    if not request.user.is_staff:
        return Response({"detail": "Only staff can view all loans."}, status=status.HTTP_403_FORBIDDEN)

    loans = Loan.objects.filter(active=True)  # Get only active loans

    # Manually adding the book title and customer username
    loan_data = []
    for loan in loans:
        loan_info = LoanSerializer(loan).data
        loan_info['book_title'] = loan.book.title  # Add the book title to the response
        loan_info['customer_username'] = loan.customer.username  # Add the customer username to the response
        loan_data.append(loan_info)

    return Response(loan_data)  # Return the modified serialized data


@api_view(['GET'])
@permission_classes([IsStaff])
def get_loan_by_id(request, loan_id):
    if not request.user.is_staff:
        return Response({"detail": "Only staff can view loans."}, status=status.HTTP_403_FORBIDDEN)

    try:
        loan = Loan.objects.get(id=loan_id, active=True)  # Get the loan by ID if it's active
    except Loan.DoesNotExist:
        return Response({"detail": "Loan not found."}, status=status.HTTP_404_NOT_FOUND)

    loan_info = LoanSerializer(loan).data
    loan_info['book_title'] = loan.book.title  # Add the book title to the response
    loan_info['customer_username'] = loan.customer.username  # Add the customer username to the response

    return Response(loan_info)  # Return the modified serialized data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_loans_for_user(request):
    if request.user.is_staff:
        return Response({"detail": "Staff cannot view their own loans here."}, status=status.HTTP_403_FORBIDDEN)

    loans = Loan.objects.filter(customer=request.user, active=True)  # Get only the active loans for the logged-in user

    # Manually adding the book title and customer username
    loan_data = []
    for loan in loans:
        loan_info = LoanSerializer(loan).data
        loan_info['book_title'] = loan.book.title  # Add the book title to the response
        loan_info['customer_username'] = loan.customer.username  # Add the customer username to the response
        loan_data.append(loan_info)

    return Response(loan_data)  # Return the modified serialized data

@api_view(['GET'])
@permission_classes([IsStaff])  # Only staff can access this method
def get_overdue_loans(request):
    # Get the current time
    current_time = timezone.now()  # Now should be accessed from django.utils.timezone

    # Filter loans that are overdue and still active
    overdue_loans = Loan.objects.filter(return_date__lt=current_time, active=True)

    # Manually adding the book title and customer username
    loan_data = []
    for loan in overdue_loans:
        loan_info = LoanSerializer(loan).data
        loan_info['book_title'] = loan.book.title  # Add the book title to the response
        loan_info['customer_username'] = loan.customer.username  # Add the customer username to the response
        loan_data.append(loan_info)

    return Response(loan_data)  # Return the modified serialized data


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only authenticated users can access this method
def get_overdue_loans_for_user(request):
    # Get the current time
    current_time = timezone.now()  # Now should be accessed from django.utils.timezone

    # Filter loans that are overdue and still active for the logged-in user
    overdue_loans = Loan.objects.filter(customer=request.user, return_date__lt=current_time, active=True)

    # Manually adding the book title and customer username
    loan_data = []
    for loan in overdue_loans:
        loan_info = LoanSerializer(loan).data
        loan_info['book_title'] = loan.book.title  # Add the book title to the response
        loan_info['customer_username'] = loan.customer.username  # Add the customer username to the response
        loan_data.append(loan_info)

    return Response(loan_data)  # Return the modified serialized data


