from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, HttpResponseRedirect, redirect


from .forms import LoginForm, RegisterForm
from .models import MyUser


# Create your views here.
def auth_login(request):
    form = LoginForm(request.POST or None)
    next_url = request.GET.get('next')
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        #print(username, password)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)    #using login function imported at the top
            if next_url is not None:
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect("/")


    context = {
        "form": form,
    }
    return render(request, 'login.html', context)


def auth_logout(request):
    logout(request)   #imported function
    return HttpResponseRedirect('/')


def auth_register(request):

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password2']
        MyUser.objects.create_user(username=username, email=email, password=password)

        # ADD message for success
        return redirect('login')


    context = {
        "form": form,
        "action_value": "",
        "submit_btn_value": "Register",

    }
    return render(request, 'accounts/register_form.html', context)


