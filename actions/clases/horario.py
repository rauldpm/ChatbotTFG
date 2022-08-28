from typing import Text, List, Any, Dict, Optional
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Action
import unidecode  # acentos
import datetime
from actions.clases.auxiliar import *

# -----------------------------------------
auxiliar = Auxiliar()
DIAS_SEMANA = auxiliar.get_dias_semana()
HORARIO = auxiliar.get_horario()
# -----------------------------------------


class HorarioGet(Action):
    def name(self):
        return 'HorarioGet'

    def run(self, dispatcher, tracker, domain):
        print("HorarioGet")
        intent = tracker.get_intent_of_latest_message()
        if intent == "horario" or intent == "apertura" or intent == "cierre":
            dispatcher.utter_message(response="utter_horario")
        message = ""
        if intent == "horario":
            for dia in DIAS_SEMANA:
                if HORARIO["horario"][dia][0] == "cerrado" and HORARIO["horario"][dia][1] == "cerrado":
                    message += dia.capitalize() + ": " + \
                        (HORARIO["horario"][dia][0]).capitalize() + "." + "\n"
                else:
                    message += dia.capitalize() + ": " + \
                        HORARIO["horario"][dia][0] + " - " + \
                        HORARIO["horario"][dia][1] + "." + "\n"
        elif intent == "apertura" or intent == "cierre":
            value = 0 if intent == "apertura" else 1
            for dia in DIAS_SEMANA:
                if HORARIO["horario"][dia][0] == "cerrado" and HORARIO["horario"][dia][1] == "cerrado":
                    message += dia.capitalize() + ": " + \
                        (HORARIO["horario"][dia][0]).capitalize() + "." + "\n"
                else:
                    message += dia.capitalize() + ": " + \
                        HORARIO["horario"][dia][value] + "." + "\n"
        elif intent == "horario_concreto":
            dia = tracker.get_slot("dia")
            if dia is not None:
                dia = dia.lower()

                if dia == "hoy":
                    now = datetime.datetime.now()
                    dia = now.strftime("%A")
                elif dia == "mañana":
                    now = (datetime.datetime.now() +
                           datetime.timedelta(1)).strftime("%A")
                    dia = now
                elif dia == "pasado mañana":
                    now = (datetime.datetime.now() +
                           datetime.timedelta(2)).strftime("%A")
                    dia = now
                dia = unidecode.unidecode(dia)

            if dia not in DIAS_SEMANA:
                message = "Ese dia de la semana es incorrecto."
                dispatcher.utter_message(message)
            elif HORARIO["horario"][dia][0] == "cerrado":
                message = "El " + dia + " estamos cerrados por descanso del personal."
            else:
                message = "El " + dia + " abrimos a las " + \
                    HORARIO["horario"][dia][0] + " y cerramos a las " + \
                    HORARIO["horario"][dia][1] + "."
        dispatcher.utter_message(message)
        return [SlotSet("dia", None)]
