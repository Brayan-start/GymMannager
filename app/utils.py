import pytz
from datetime import datetime, date, time

BOLIVIA_TZ = pytz.timezone('America/La_Paz')

def bolivia_now():
    return datetime.now(BOLIVIA_TZ)

def bolivia_date():
    return bolivia_now().date()

def bolivia_time():
    return bolivia_now().time()

DIAS_MAP = {
    0: 'lunes', 1: 'martes', 2: 'miercoles',
    3: 'jueves', 4: 'viernes', 5: 'sabado', 6: 'domingo'
}

def hoy_dia_semana():
    return DIAS_MAP[datetime.now().weekday()]
