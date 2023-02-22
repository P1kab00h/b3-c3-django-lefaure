
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages


# Create your views here.

# Render the template (index.html):
def index(request):
    return render(request, "index.html", {})

# two-step booking process :
# first, it gets the next 21 valid days (week days) using validWeekday()
# then checks if this days are full. After, it will show the days in the template for user to choose
# When user select the service and the date it store the data in Django sessions
# And go to the next step


def booking(request):
    # Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)
    # Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        if service == None:
            messages.success(request, "Merci de sélectionner un cours !")
            return redirect('booking')

        # Keep the day and course in a django Session
        request.session['day'] = day
        request.session['service'] = service

        return redirect('bookingSubmit')

    return render(request, 'booking.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
    })

# bookingSubmit() correspond for the second step of the booking process.
# It gets the previous session data then unse checkTime() function in order to checks
# if the current time is available for the day selected
# Finally will store in databse the user choice


def bookingSubmit(request):
    user = request.user
    times = [
        "08h00", "09h00", "10h00", "11h00", "13h00", "14h00", "15h00", "16h00", "17h00"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    # Get stored data from django session:
    day = request.session.get('day')
    service = request.session.get('service')

    # Only show the time of the day that has not been selected before:
    hour = checkTime(times, day)
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Tuesday' or date == 'Wednesday' or date == 'Thursday' or date == 'Friday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            AppointmentForm = Appointment.objects.get_or_create(
                                user=user,
                                service=service,
                                day=day,
                                time=time,
                            )
                            messages.success(
                                request, "Rendez-vous pour le cours pris")
                            return redirect('index')
                        else:
                            messages.success(
                                request, "Ce créneau est déjà reservé")
                    else:
                        messages.success(
                            request, "Cette journée est déjà compléte")
                else:
                    messages.success(request, "Cette date n'est pas correct")
            else:
                messages.success(
                    request, "Ce créneau n'est pas disponible pour ce jour")
        else:
            messages.success(request, "Merci de sélectionner un cours")

    return render(request, 'bookingSubmit.html', {
        'times': hour,
    })

# The userPanel() function will displays the user’s booked appointments
#  and allows the user to edit his appointments.


def userPanel(request):
    user = request.user
    appointments = Appointment.objects.filter(
        user=user).order_by('day', 'time')
    return render(request, 'userPanel.html', {
        'user': user,
        'appointments': appointments,
    })

# The userUpdate() function takes the id argument from the appointment selected to edit (update)
# and in addition to the booking() function it has a “delta24” variable which is to determine if the selected date is
# 24hrs before the day user’s in using datetime.today() function.


def userUpdate(request, id):
    appointment = Appointment.objects.get(pk=id)
    userdatepicked = appointment.day
    # Copy  booking:
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')

    # 24h if statement in template:
    delta24 = (userdatepicked).strftime(
        '%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    # Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(22)

    # Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')

        # Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service

        return redirect('userUpdateSubmit', id=id)

    return render(request, 'userUpdate.html', {
        'weekdays': weekdays,
        'validateWeekdays': validateWeekdays,
        'delta24': delta24,
        'id': id,
    })

# userUpdateSubmit() function is just like the bookingSubmit() function


def userUpdateSubmit(request, id):
    user = request.user
    times = [
        "08h00", "09h00", "10h00", "11h00", "13h00", "14h00", "15h00", "16h00", "17h00"
    ]
    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')
    service = request.session.get('service')

    # Only show the time of the day that has not been selected before and the time he is editing:
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Tuesday' or date == 'Wednesday' or date == 'Thursday' or date == 'Friday':
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            AppointmentForm = Appointment.objects.filter(pk=id).update(
                                user=user,
                                service=service,
                                day=day,
                                time=time,
                            )
                            messages.success(
                                request, "Rendez-vous mis à jour !")
                            return redirect('index')
                        else:
                            messages.success(
                                request, "Ce créneau a déjà était reservé !")
                    else:
                        messages.success(
                            request, "Cett journée est compléte !")
                else:
                    messages.success(request, "Cette date est incorrecte")
            else:
                messages.success(
                    request, "Cette période n'est aps disponible pour ce jour !")
        else:
            messages.success(request, "Merci de sélectionner un cours!")
        return redirect('userPanel')

    return render(request, 'userUpdateSubmit.html', {
        'times': hour,
        'id': id,
    })

# staffPanel() will show the bookings in the next 21 days in the template.


def staffPanel(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    # Only show the Appointments 21 days from today
    items = Appointment.objects.filter(
        day__range=[minDate, maxDate]).order_by('day', 'time')

    return render(request, 'staffPanel.html', {
        'items': items,
    })

# dayToWeekday() function takes a day and converts it to a string so the Django template can show it to the user.


def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

# validWeekday() function takes an argument “days” and checks if each day in the period from Lundi to Vendredi
# then returns a list of “weekdays” of valid days.


def validWeekday(days):
    # Loop days you want in the next 21 days:
    today = datetime.now()
    weekdays = []
    for i in range(0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Tuesday' or y == 'Wednesday' or y == 'Thursday' or y == 'Friday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays

# isWeekdayValid() function takes an argument “x”
# and checks the list of days from validWeekday() if the days are full or not.
# Then returns a list of “validateWeekdays” of weekdays that are Lundi to Vendredi and are not completely booked.


def isWeekdayValid(x):
    validateWeekdays = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 10:
            validateWeekdays.append(j)
    return validateWeekdays

# checkTime() function takes two arguments “times” and “day” so it can check which times of that day are free to be booked by the user.


def checkTime(times, day):
    # Only show the time of the day that has not been selected before:
    x = []
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1:
            x.append(k)
    return x

# checkEditTime() function is exactly like checkTime() but takes an additional argument “id” (the appointment’s id that the user is trying to edit)
# so the time of that appointment the user is editing would be shown to the user


def checkEditTime(times, day, id):
    # Only show the time of the day that has not been selected before:
    x = []
    appointment = Appointment.objects.get(pk=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x
