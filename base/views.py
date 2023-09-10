from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
#rooms =[
#    {'id':1, 'name':'pythonnn'},
#    {'id':2, 'name':'haha'},
#    {'id':3, 'name':'heyy'},
#]

def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) 
    #case insensitive and if contain keyword q in the string
    topics=Topic.objects.all()[:5]
    room_count=rooms.count()
    total_room_count=Room.objects.count()
    room_messages=Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )[:5]

    context= {
        'rooms':rooms, 
        'topics':topics,
        'room_count':room_count,
        'room_messages':room_messages,
        'total_room_count':total_room_count,
        }

    
    return render(request, 'base/home.html',context)

def room(request, pk):
    room=Room.objects.get(id=pk)
    room_messages= room.message_set.all().order_by('-created')
    participants=room.participants.all()

    if (request.method=="POST" and request.POST.get('message')):
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('message')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id) # reload the page, cos it is in POST, may cos issue to other function
    
    context={
        'room':room,
        'room_messages':room_messages,
        'participants': participants
             }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user= User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics=Topic.objects.all()
    context={'user':user,
             'rooms':rooms,
             'room_messages':room_messages,
             'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login') #use login require decorator to check before user execute function, else redirect to /login
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)
        room=Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')   
        )
        room.participants.add(request.user)
        return redirect('home')

    context={
        'form':form, 
        'topics':topics
        }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/login') 
def updateRoom(request, pk):
    room =Room.objects.get(id=pk)
    form=RoomForm(instance=room) # will be prefilled
    topics=Topic.objects.all()

    if request.user !=room.host:
        return HttpResponse('You are not allowed to update!')
    
    if request.method =='POST':
        topic_name=request.POST.get('topic')
        topic,created=Topic.objects.get_or_create(name=topic_name)

        room.name=request.POST.get('name')
        room.description=request.POST.get('description')
        room.topic=topic
        room.save()
        return redirect('home')
    
    context={
        'form':form,
        'topics':topics,
        'room':room
        }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login') 
def deleteRoom(request, pk):
    room=Room.objects.get(id=pk)

    if request.user !=room.host:
        return HttpResponse('You are not allowed to delete!')
    
    if request.method =='POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='/login') 
def deleteMessage(request, pk):
    message=Message.objects.get(id=pk)
    room=Room.objects.get(message=message)

    if request.user !=message.user:
        return HttpResponse('You are not allowed to delete!')
    
    if request.method =='POST':
        message.delete()
        return redirect('room', room.id)
    return render(request, 'base/delete.html', {'obj':message})

def loginPage(request):
    page ='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        #username=request.POST.get('username').lower()
        email=request.POST.get('email').lower()
        password=request.POST.get('password')

        try:
            user=User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist!') # get from google: django flash

        user=authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist!')

    context={'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request) # delete token
    return redirect('home')


def registerPage(request):
    form= MyUserCreationForm() #UserCreationForm()
    context={'form':form}
    if request.method =="POST":
        form= MyUserCreationForm(request.POST) #UserCreationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False) #save the form but freeze it, for further process purpose
            user.username =user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registeration!')
    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)

    if request.method=='POST':
        form= UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return(redirect('user-profile', pk=user.id))
    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    topics=Topic.objects.filter(name__icontains=q)
    total_room_count=Room.objects.count()
    context={
        'topics':topics,
        'total_room_count': total_room_count
        }
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages=Message.objects.all()
    context={
        'room_messages':room_messages
             }
    return render(request, 'base/activity.html', context)

def likeRoom(request):
    
    if request.method=='GET':
        room_id=request.GET['room_id']
        room=Room.objects.get(id=room_id)
        
        if room.likeroom.all().contains(request.user):
            room.likeroom.remove(request.user)          
            like="""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="-9 -7 32 32" fill="none" stroke="#71c6dd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>"""
        else:
            room.likeroom.add(request.user)
            like="""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="-9 -7 32 32" fill="#71c6dd" stroke="#71c6dd" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-heart">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>"""

        likecount=room.likeroom.count()
        data={
            'likecount':likecount,
            'liked_room':like
        }
        
        return JsonResponse(data)
    
def likeMessage(request):
    
    if request.method=='GET':
        message_id=request.GET['message_id']
        message=Message.objects.get(id=message_id)
        
        if message.likemessage.all().contains(request.user):
            message.likemessage.remove(request.user)          
            like='Like'
        else:
            message.likemessage.add(request.user)
            like="""Unlike"""

        likecount=message.likemessage.count()
        data={
            'likecount':likecount,
            'liked_message':like
        }
        
        return JsonResponse(data)
    