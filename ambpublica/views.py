from ast import And
from urllib import request
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib import messages
from ambpublica.forms import BuscarMascotaForm, CitaForm, MascotaSelectForm, RutForm
from paneltrabajador.forms import ClienteForm, MascotaForm
from paneltrabajador.models import Cita, Cliente, Mascota

# Create your views here.

# Renderiza la página principal
def main(request):
    template = loader.get_template('ambpublica/main.html')
    return HttpResponse(template.render())


def consulta_mascota(request):
    """
    Maneja la consulta de una mascota a través de un formulario.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de búsqueda o los resultados de la búsqueda.
    """

    # Si la solicitud es de tipo POST (es decir, el formulario fue enviado), valida un formulario (BuscarMascotaForm).
    if request.method == 'POST':
        # Pasamos los datos de la peticion al formulario
        form = BuscarMascotaForm(request.POST)

        # Si el formulario es válido, realiza una búsqueda de la mascota en la base de datos y muestra los resultados en el template.
        if form.is_valid():

            #
            rut = form.cleaned_data['rut']
            id_mascota = form.cleaned_data['id_mascota']

            # Intenta obtener los objetos. Al no existir estos causan una excepcion que manejaremos aquí.
            # Si el cliente o la mascota no existen, redirecciona a la página de consulta con un mensaje de error.
            try:
                cliente = Cliente.objects.get(rut=rut)
                mascota = Mascota.objects.get(cliente=cliente, id_mascota=id_mascota)
                return render(request, 'ambpublica/consulta_mascota/ficha.html', {'mascota': mascota})
            except Cliente.DoesNotExist:
                messages.error(request, 'Cliente con Rut {} no encontrado.'.format(rut))
                return redirect('ambpublico_consulta')
            except Mascota.DoesNotExist:
                messages.error(request, 'Mascota con ID {} no encontrada para el cliente con Rut {}.'.format(id_mascota, rut))
                return redirect('ambpublico_consulta')
    else:
        # Obtener el formulario y mostrarlo.
        form = BuscarMascotaForm()
        return render(request, 'ambpublica/consulta_mascota/form.html', {'form': form})

# Maneja un flujo de pasos para la reserva de una cita.
# Utiliza la sesión para almacenar el estado del proceso de reserva.
def reserva_hora(request):
    """
    Maneja un flujo de pasos para la reserva de una cita.
    Utiliza la sesión para almacenar el estado del proceso de reserva.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario correspondiente al paso actual o redirige a otras vistas.
    """

    # Definicion de variables por defecto
    titulo = "Por favor, ingrese su RUT."

    # Verificamos si el usuario ya está en algún paso y lo asignamos a la variable
    if request.session.has_key('reserva_step'):
        step = request.session['reserva_step']
    else:
        step = ''

    # Los pasos incluyen la creación de un cliente, una mascota, la selección de una mascota existente o la finalización del proceso.
    # Renderiza diferentes formularios y vistas según el paso actual.

    if step == "crear_cliente":
        titulo = "Por favor, ingrese sus datos."

        # Formulario fue enviado
        if request.method == 'POST':
            # Pasamos los datos de la peticion al formulario
            form = ClienteForm(request.POST)

            # Formulario es válido, crea el cliente y lo inserta, pasa al siguiente paso
            if form.is_valid():
                request.session['reserva_c_rut'] = form.cleaned_data['rut']
                form.save()
                messages.success(request, "Se ha creado el cliente correctamente.")
                request.session['reserva_step'] = "select_mascota"
                return redirect('ambpublico_reserva')
        else:
            # Definimos el formulario para ser usado más abajo en la renderizacion del template
            form = ClienteForm()
            # Le damos el valor del RUT ingresado en el primer paso
            form.fields['rut'].initial = request.session['reserva_c_rut']
    elif step == "crear_mascota":
        titulo = "Por favor, ingrese los datos de su mascota."

        # Verificamos si el cliente que nos dieron anteriormente existe
        try:
            cliente = Cliente.objects.get(rut=request.session['reserva_c_rut'])

        # Nos engañaron, el cliente no existe, cancelar todo
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('ambpublico_reserva_cancelar')
        # Error generico
        except:
            messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')

        # Todo bien arriba, entonces procedemos

        # Se envia el formulario
        if request.method == 'POST':

            # Pasamos los datos de la peticion al formulario
            # es_reserva nos permite para más seguridad eliminar los campos cliente e historial médico los cuales
            # solo el personal de la clinica puede manejar
            form = MascotaForm(request.POST, es_reserva=True)

            # Formulario OK, insertar la mascota, asignamos el objeto cliente que viene desde el paso anterior, vamos al siguiente paso
            if form.is_valid():
                obj = form.save(commit=False)
                obj.cliente = cliente
                obj.save()
                messages.success(request, "Se ha agregado la mascota correctamente.")
                request.session['reserva_step'] = "select_mascota"
                return redirect('ambpublico_reserva')
        else:
            # Definimos el formulario para ser usado más abajo en la renderizacion del template
            form = MascotaForm(es_reserva=True)

    elif step == "select_mascota":
        titulo = "Por favor, seleccione su mascota o agregue una nueva."

        # Debe el usuario crear una mascota antes de poder seleccionar?
        crear_mascota = False

        # Verificamos que existan ambos
        try:
            cliente = Cliente.objects.get(rut=request.session['reserva_c_rut'])
            mascotas = Mascota.objects.filter(cliente=cliente)

        # Nos engañaron, el cliente no existe, cancelar todo
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('ambpublico_reserva_cancelar')
        # Error generico
        except:
            messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')

        # Cliente no tiene mascotas, debe crear una nueva para seguir
        if not mascotas.exists():
            crear_mascota = True

        # Obtenemos parametros (?crear_mascota=true) desde la URL en caso de que el cliente desee ingresar otra mascota
        # Ya teniendo una existente
        param_crea_mascota = request.GET.get('crear_mascota')
        if param_crea_mascota is not None and param_crea_mascota == "true":
            crear_mascota = True

        # Debemos ir a crear mascota entonces?
        if crear_mascota == True:
            request.session['reserva_step'] = "crear_mascota"
            return redirect('ambpublico_reserva')

        # Ok, no vamos a ir a crear mascota, seguimos con la seleccion

        # Cargamos proceso de seleccion para el final
        # Definimos el formulario para ser usado más abajo en la renderizacion del template
        # Usamos queryset para obtener los objetos en el modelo y mostrarlos en el select del formulario
        form = MascotaSelectForm(queryset=mascotas)

        # Se envia el formulario
        if request.method == 'POST':
            # Pasamos los datos de la peticion al formulario
            # Usamos queryset para obtener los objetos en el modelo y mostrarlos en el select del formulario
            # Es necesario hacerlo nuevamente para la validacion del formulario
            form = MascotaSelectForm(request.POST, queryset=mascotas)
            # Formulario es válido, guardamos el ID de la mascota, vamos al paso final
            if form.is_valid():
                request.session['reserva_m_id'] = form.cleaned_data['mascota']
                request.session['reserva_step'] = "final"
                return redirect('ambpublico_reserva')
    elif step == "final":
        # Intentamos obtener el cliente y la mascota
        try:
            cliente = Cliente.objects.get(rut=request.session['reserva_c_rut'])
            # La mascota debe pertenecer al Cliente, si no, nos ingresaron cualquier cosa
            mascota = Mascota.objects.get(cliente=cliente, id_mascota=request.session['reserva_m_id'])
        # Nos engañaron, el cliente o la mascota no existe, cancelar todo
        except (Cliente.DoesNotExist, Mascota.DoesNotExist):
            messages.error(request, 'No se ha encontrado la información ingresada. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')
        # Error generico
        except:
            messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')

        # Se envia el formulario
        if request.method == 'POST':
            # Pasamos los datos de la peticion al formulario
            form = CitaForm(request.POST)

            # Todo OK
            if form.is_valid():
                # Obtener el valor de la nueva cita
                n_cita = form.cleaned_data['n_cita']

                # Verificamos que la cita ingresada sea real, ingresamos los datos del cliente y la mascota a ella
                try:
                    cita = Cita.objects.get(n_cita=n_cita)
                    cita.estado = '1'
                    cita.cliente = cliente
                    cita.mascota = mascota
                    cita.save()
                # Error generico
                except:
                    messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
                    return redirect('ambpublico_reserva_cancelar')

                # Eliminamos el paso para que se devuelva al inicio
                try:
                    del request.session['reserva_step']
                except:
                    pass

                # Todo OK, nos devolvemos
                messages.success(request, '¡Se ha reservado su hora exitosamente!')
                return redirect('ambpublico_reserva')

        # Definimos el formulario para ser usado más abajo en la renderizacion del template
        form = CitaForm()

        # Contexto distinto para mostrar toda la información en el resumen ya que es el paso final
        context = {'form': form, 'step': step, 'mascota': mascota, 'cliente': cliente}

        # Hacemos return aquí para que no se cargue el contexto de más abajo
        return render(request, 'ambpublica/reserva_horas/form.html', context)
    else:
        # Obtenemos la lista de todas las citas
        citas = Cita.objects.filter(estado='0')

        # Si no hay citas, entonces le asignamos al formulario un contexto personalizado
        # Para mostrar que no hay citas
        if not citas.exists():
            return render(request, 'ambpublica/reserva_horas/form.html', {'step': 'nohours'})
        else:
            # Se envia el formulario
            if request.method == 'POST':
                # Pasamos los datos de la peticion al formulario
                form = RutForm(request.POST)
                # Verificamos que todo este bien
                if form.is_valid():
                    # Obtenemos la información sanitizada por seguridad
                    rut = form.cleaned_data['rut']

                    # Obtenemos el cliente
                    cliente = Cliente.objects.filter(rut=rut).first()

                    # Existe el cliente, ir directamente a la seleccion de mascotas
                    if cliente:
                        request.session['reserva_c_rut'] = cliente.rut
                        request.session['reserva_step'] = "select_mascota"
                        return redirect('ambpublico_reserva')

                    # No existe, tendrá que ingresar sus datos entonces
                    else:
                        request.session['reserva_c_rut'] = rut
                        request.session['reserva_step'] = "crear_cliente"
                        return redirect('ambpublico_reserva')

            # Definimos el formulario para ser usado más abajo en la renderizacion del template
            form = RutForm()

    # Definimos las diferentes variables mediante el contexto Django
    context = {'titulo': titulo, 'form': form, 'step': step}
    return render(request, 'ambpublica/reserva_horas/form.html', context)

# Funcion simple para eliminar la variable de sesion para cancelar el proceso de reserva
def reserva_hora_cancelar(request):
    """
    Cancela el proceso de reserva eliminando la variable de sesión.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que redirige a la vista de reserva.
    """
    try:
        del request.session['reserva_step']
    except:
        pass
    messages.success(request, "El proceso de reserva ha sido cancelado.")
    return redirect('ambpublico_reserva')
