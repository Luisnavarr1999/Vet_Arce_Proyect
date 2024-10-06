from ast import And
from urllib import request
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib import messages
from ambpublica.forms import RutForm
from paneltrabajador.forms import MascotaForm
from paneltrabajador.models import Cliente

# Create your views here.

# Renderiza la página principal
def main(request):
    template = loader.get_template('ambpublica/main.html')
    return HttpResponse(template.render())


