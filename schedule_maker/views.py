from django.shortcuts import render
from django.contrib import messages
import csv, io
from .forms import Student_form
from .models import Student


def process(request):
    classes, students_with_no_friends, overview = Student.distribute_to_classes()
    overview['Students With No Friends'] = len(students_with_no_friends)

    no_friends_processed = []
    for student in students_with_no_friends:
        no_friends_processed.append(
            [Student.objects.filter(id=student['id'])[0], student['gender'], student['islamic'], student['behavior']])

    if request.method == 'POST':
        class_number = int(list(request.POST.keys())[1])
        current_class = classes[class_number-1]
        students = []
        for student in current_class.students:
            students.append([Student.objects.filter(id=student['id'])[0], student['gender'], student['islamic'], student['behavior']])
        context = {
            'class_number': class_number,
            'Students': students,
            'overview': {'Males': current_class.males, 'Females': current_class.females, 'Islamic Students': current_class.islamic, 'Behavioral Students': current_class.behavior},
        }
        return render(request, 'class_stats.html', context)

    num_of_classes = range(1, len(classes)+1)
    processed_num_classes = []
    for i in range(0, len(num_of_classes), 5):
        processed_num_classes.append(num_of_classes[i:i + 5])
    print(processed_num_classes)

    context = {
        'no_friends': no_friends_processed,
        'classes': classes,
        'num_classes': processed_num_classes,
        'overview': overview
    }
    return render(request, 'schedule.html', context)


def upload(request):
    '''
    The user can upload a:
    - CSV file
    - A form

    This data is processed an put into the mySQL database
    '''

    form = Student_form(request.POST or None)

    context = {
        'form': form,
    }

    if request.method == 'GET':
        return render(request, 'upload_data.html', context)

    # Check if the user submits a form
    if 'form_submission' in request.POST:
        # If the form is valid, it saves the data to the db
        if form.is_valid():
            form.save()

    # Check if user uploads a file
    if 'file_submission' in request.POST:
        # Check if the file is of type csv
        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'This is not a csv file')
            return render(request, 'upload_data.html', context)

        # If it is a CSV file, process it
        data = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data)
        csv_reader = csv.reader(io_string, delimiter=',')

        # To skip the columns
        next(csv_reader)

        # Loop through all the students and save them to the database
        for row in csv_reader:
            # Remove ID from the data
            row = row[1:]

            # Save the model with student data
            is_islamic = True if row[2] == 'true' else False
            what_gender = 'M' if row[3] == 'Male' else 'F'
            is_behavior = True if row[4] == 'true' else False
            student = Student(
                first_name=row[0],
                last_name=row[1],
                islamic=is_islamic,
                gender=what_gender,
                behavior=is_behavior,
                friend1=row[5],
                friend2=row[6],
                friend3=row[7],
                friend4=row[8],
                friend5=row[9])
            student.save()


    # Once finished, redirect to the home page
    messages.success(request, 'File has been processed successfully')
    return render(request, 'upload_data.html')

