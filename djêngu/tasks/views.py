from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Task
from .forms import TaskForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import schedule
import threading
import time

@login_required
def taskList(request):

    search = request.GET.get('search')
    filter = request.GET.get('filter')

    if search: 
        tasks = Task.objects.filter(title__icontains=search, user=request.user)

    elif filter:
        tasks = Task.objects.filter(done=filter, user=request.user)

    else:
        tasks_list = Task.objects.all().order_by('-created_at').filter(user=request.user)
        paginator = Paginator(tasks_list, 3)
        page = request.GET.get('page')
        tasks = paginator.get_page(page)
        if tasks_list:
            do_send(request)

    return render(request, 'tasks/list.html', {'tasks': tasks})

@login_required
def taskView(request, id):

    task = get_object_or_404(Task, pk=id)
    return render(request, 'tasks/task.html', {'task': task})

@login_required
def newTask(request):

    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.done = 'doing'
            task.user = request.user
            task.save()
            to_email = request.user.email
            send_mail('Nova Tarefa', 
                      f'Você adicionou a tarefa: {task.title} em seu gerenciador, lembre-se de realiza-lá!', 
                      'fernando_radunz1@hotmail.com', 
                      [to_email])
            return redirect('/')
    else:

        form = TaskForm()
        return render(request, 'tasks/addtask.html', {'form': form})

@login_required
def changeStatus(request, id):

    task = get_object_or_404(Task, pk=id)

    if (task.done) == 'doing':
        task.done = 'done'

    else:
        task.done = 'doing'

    task.save()

    return redirect('/')

@login_required
def editTask(request, id):

    task = get_object_or_404(Task, pk=id)
    form = TaskForm(instance=task)

    if(request.method == 'POST'):
        form = TaskForm(request.POST, instance=task)

        if (form.is_valid()):
            task.save()
            return redirect('/')
        
        else:
            return render(request, 'tasks/edittask.html', {'form': form, 'task': task})
        
    else:
        return render(request, 'tasks/edittask.html', {'form': form, 'task': task})

@login_required
def deleteTask(request, id):

    task = get_object_or_404(Task, pk=id)
    task.delete()
    
    messages.info(request, 'Tarefa deletada com sucesso.')

    return redirect('/')

def reminder(to_email):
    send_mail('Lembrete', 
              'Lembre-se de realizar suas tarefas pendentes!', 
              'fernando_radunz1@hotmail.com', 
              [to_email])

def send(email):

    schedule.every(15).minutes.do(reminder, email)

def run():
    while True:
        schedule.run_pending()
        time.sleep(1)

@login_required
def do_send(request):
    email = request.user.email
    send(email)
    threading.Thread(target=run, daemon=True).start()