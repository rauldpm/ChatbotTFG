from typing import Text, List, Any, Dict, Optional
from rasa_sdk.events import SlotSet
from rasa_sdk.interfaces import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
from actions.clases.auxiliar import *

# -----------------------------------------
auxiliar = Auxiliar()
CATEGORIA_MENU = auxiliar.get_categorias_menu()
DATA_PATH = auxiliar.get_data_path()
# -----------------------------------------


class MenuBorrarPlato(Action):
    def name(self):
        return 'MenuBorrarPlato'

    def run(self, dispatcher, tracker, domain):
        print("MenuBorrarPlato")

        menu_plato_id = tracker.get_slot("menu_plato_id")
        menu_bebida_id = tracker.get_slot("menu_bebida_id")
        menu_plato_1_id = tracker.get_slot("menu_plato_1_id")
        menu_plato_2_id = tracker.get_slot("menu_plato_2_id")
        menu_plato_3_id = tracker.get_slot("menu_plato_3_id")

        if menu_plato_1_id is None and menu_plato_2_id is None and menu_plato_3_id is None and menu_bebida_id is None:
            dispatcher.utter_message(text=f'')
            return [SlotSet("menu_hay_plato", False)]

        if menu_plato_id is not None:
            menu_plato_id = menu_plato_id.upper()

            if menu_plato_id == menu_plato_1_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado el plato.')
                if menu_plato_2_id is None and menu_plato_3_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_1_id", None), SlotSet("menu_plato_1_nombre", None), SlotSet("menu_plato_1_precio", None), SlotSet("menu_hay_plato", False)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_1_id", None), SlotSet("menu_plato_1_nombre", None), SlotSet("menu_plato_1_precio", None)]
            elif menu_plato_id == menu_plato_2_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado el plato.')
                if menu_plato_1_id is None and menu_plato_3_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_2_id", None), SlotSet("menu_plato_2_nombre", None), SlotSet("menu_plato_2_precio", None), SlotSet("menu_hay_plato", False)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_2_id", None), SlotSet("menu_plato_2_nombre", None), SlotSet("menu_plato_2_precio", None)]
            elif menu_plato_id == menu_plato_3_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado el plato.')
                if menu_plato_2_id is None and menu_plato_1_id is None and menu_bebida_id is None:
                    return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_3_id", None), SlotSet("menu_plato_3_nombre", None), SlotSet("menu_plato_3_precio", None), SlotSet("menu_hay_plato", False)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_plato_3_id", None), SlotSet("menu_plato_3_nombre", None), SlotSet("menu_plato_3_precio", None)]
            elif menu_plato_id == menu_bebida_id:
                dispatcher.utter_message(
                    text=f'Se ha eliminado la bebida.')
                if menu_plato_1_id is None and menu_plato_2_id is None and menu_plato_3_id is None:
                    return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_bebida_id", None), SlotSet("menu_bebida_nombre", None), SlotSet("menu_bebida_precio", None), SlotSet("menu_hay_plato", False)]
                return [SlotSet("menu_plato_id", None), SlotSet("menu_plato_categoria", None), SlotSet("menu_bebida_id", None), SlotSet("menu_bebida_nombre", None), SlotSet("menu_bebida_precio", None)]
            else:
                dispatcher.utter_message(
                    text=f'Ese plato no esta establecido no esta guardado, comprueba el ID.')
                return [SlotSet("menu_plato_id", None)]

        else:
            dispatcher.utter_message(
                text=f'No se ha establecido un ID de plato.')
            return [SlotSet("menu_plato_id", None)]


class MenuBorrarTodo(Action):
    def name(self):
        return 'MenuBorrarTodo'

    def run(self, dispatcher, tracker, domain):
        print("MenuBorrarTodo")

        dispatcher.utter_message(text=f'Menu restablecido.')
        return [
            SlotSet("menu_plato_1_id", None),
            SlotSet("menu_plato_1_nombre", None),
            SlotSet("menu_plato_1_precio", None),
            SlotSet("menu_plato_2_id", None),
            SlotSet("menu_plato_2_nombre", None),
            SlotSet("menu_plato_2_precio", None),
            SlotSet("menu_plato_3_id", None),
            SlotSet("menu_plato_3_nombre", None),
            SlotSet("menu_plato_3_precio", None),
            SlotSet("menu_bebida_id", None),
            SlotSet("menu_bebida_nombre", None),
            SlotSet("menu_bebida_precio", None),
            SlotSet("menu_establecido", False),
            SlotSet("menu_plato_id", None),
            SlotSet("menu_plato_categoria", None),
            SlotSet("menu_hay_plato", False)
        ]


class MenuGet(Action):
    def name(self):
        return 'MenuGet'

    def get_menu_plato(Action, tipo):
        data = auxiliar.get_data_generic(DATA_PATH+"/data/menu/"+tipo+".json")
        message = tipo.capitalize() + ":" + "\n"
        for it in data[tipo]:
            message += str(it['id']) + ": " + it['nombre'] + \
                " - (" + it['precio'] + ")\n"
        return message

    def get_submenu_botones(Action, tipo):
        data = auxiliar.get_data_generic(DATA_PATH+"/data/menu/"+tipo+".json")
        buttons = []
        for it in data[tipo]:
            buttons.append({"title": "{}".format(
                it['nombre'] + " (" + it['id'] + ")"), "payload": "{}".format(it['id'])})
        return buttons

    def run(self, dispatcher, tracker, domain):
        print("MenuGet")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        intent = tracker.get_intent_of_latest_message()

        if intent == "menu_completo":
            message = ""
            for it in CATEGORIA_MENU:
                data = auxiliar.get_data_generic(
                    DATA_PATH+"/data/menu/"+it+".json")
                message += it.capitalize() + ":\n"
                for d in data[it]:
                    message += "- " + d['nombre'] + \
                        " - (" + d['precio'] + ")\n"
            dispatcher.utter_message(text=message)
            return ""

        if menu_plato_categoria is not None:

            menu_plato_categoria = menu_plato_categoria.lower()
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break
            if menu_plato_categoria in CATEGORIA_MENU:
                message = self.get_menu_plato(menu_plato_categoria)
                dispatcher.utter_message(text=message)
                return [SlotSet("menu_plato_categoria", menu_plato_categoria)]
            else:
                dispatcher.utter_message(text=f'Esa categoria no existe.')
                return [SlotSet("menu_plato_categoria", None)]
        else:
            dispatcher.utter_message(
                text=f'No se ha establecido una categoria')


class MenuGetBotones(Action):
    def name(self):
        return 'MenuGetBotones'

    def get_submenu_botones(Action, tipo):
        data = auxiliar.get_data_generic(DATA_PATH+"/data/menu/"+tipo+".json")
        buttons = []
        for it in data[tipo]:
            buttons.append({"title": "{}".format(
                it['nombre']), "payload": "{}".format(it['id'])})
        return buttons

    def run(self, dispatcher, tracker, domain):
        print("MenuGetBotones")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")

        if menu_plato_categoria is not None:

            menu_plato_categoria = menu_plato_categoria.lower()
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break
            if menu_plato_categoria in CATEGORIA_MENU:
                buttons = self.get_submenu_botones(menu_plato_categoria)
                dispatcher.utter_message(
                    text=f'Selecciona el plato que desees', buttons=buttons)
                return ""
            else:
                dispatcher.utter_message(text=f'Esa categoria no existe.')
                return [SlotSet("menu_plato_categoria", None)]
        else:
            dispatcher.utter_message(
                text=f'No se ha establecido una categoria')


class MenuCheckCategoria(Action):
    def name(self):
        return 'MenuCheckCategoria'

    def run(self, dispatcher, tracker, domain):
        print("MenuCheckCategoria")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_categoria is not None:
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break
            if menu_plato_categoria in CATEGORIA_MENU:
                return [SlotSet("menu_plato_categoria", menu_plato_categoria)]
            else:
                return [SlotSet("menu_plato_categoria", None)]

        else:
            return ""


class MenuGetCategoriasButtons(Action):
    def name(self):
        return 'MenuGetCategoriasButtons'

    def get_categorias_botones(Action):
        buttons = []
        for it in CATEGORIA_MENU:
            buttons.append({"title": "{}".format(
                it.capitalize()), "payload": "{}".format(it)})
        return buttons

    def run(self, dispatcher, tracker, domain):
        print("MenuGetCategoriasButtons")

        buttons = self.get_categorias_botones()
        dispatcher.utter_message(
            "Selecciona una categoria:", buttons=buttons, button_type="vertical")
        return ""


class MenuGetUser(Action):
    def name(self):
        return 'MenuGetUser'

    def run(self, dispatcher, tracker, domain):
        print("MenuGetUser")

        menu_plato_1_id = tracker.get_slot("menu_plato_1_id")
        menu_plato_2_id = tracker.get_slot("menu_plato_2_id")
        menu_plato_3_id = tracker.get_slot("menu_plato_3_id")
        menu_bebida_id = tracker.get_slot("menu_bebida_id")

        message = ''
        if menu_plato_1_id is not None:
            message += "Plato:\n- " + \
                tracker.get_slot("menu_plato_1_id") + ": " + \
                tracker.get_slot("menu_plato_1_nombre") + " - (" + \
                tracker.get_slot("menu_plato_1_precio") + ")\n"
        if menu_plato_2_id is not None:
            message += "Plato:\n- " + \
                tracker.get_slot("menu_plato_2_id") + ": " + \
                tracker.get_slot("menu_plato_2_nombre") + " - (" + \
                tracker.get_slot("menu_plato_2_precio") + ")\n"
        if menu_plato_3_id is not None:
            message += "Plato:\n- " + \
                tracker.get_slot("menu_plato_3_id") + ": " + \
                tracker.get_slot("menu_plato_3_nombre") + " - (" + \
                tracker.get_slot("menu_plato_3_precio") + ")\n"
        if menu_bebida_id is not None:
            message += "Bebida:\n- " + \
                tracker.get_slot("menu_bebida_id") + ": " + \
                tracker.get_slot("menu_bebida_nombre") + " - (" + \
                tracker.get_slot("menu_bebida_precio") + ")\n"

        # if tracker.get_slot("menu_establecido") == False:
        #    message += "Aun no has hecho efectivo tu menu, escribe: 'Finalizar menu' para guardarlo.\n"

        if message == '':
            dispatcher.utter_message(
                text=f"No se ha establecido ningun plato aun. Introduce 'Establecer menu' para añadir un plato.")
        else:
            dispatcher.utter_message(text=message)
        return ''


class MenuResetPlatoID(Action):
    def name(self):
        return 'MenuResetPlatoID'

    def run(self, dispatcher, tracker, domain):
        print("MenuResetPlatoID")
        return [SlotSet("menu_plato_id", None)]


class MenuFinalizar(Action):
    def name(self):
        return 'MenuFinalizar'

    def run(self, dispatcher, tracker, domain):
        print("MenuFinalizar")

        menu_bebida_id = tracker.get_slot("menu_bebida_id")
        menu_plato_1_id = tracker.get_slot("menu_plato_1_id")
        menu_plato_2_id = tracker.get_slot("menu_plato_2_id")
        menu_plato_3_id = tracker.get_slot("menu_plato_3_id")

        if menu_plato_1_id is None and menu_plato_2_id is None and menu_plato_3_id is None:
            dispatcher.utter_message(
                text="No hay un plato establecido, debes establecer minimo un plato y una bebida.")
            return [SlotSet("menu_establecido", False)]

        if menu_bebida_id is None:
            dispatcher.utter_message(
                text="No hay una bebida establecida, debes establecer minimo un plato y una bebida.")
            return [SlotSet("menu_establecido", False)]

        dispatcher.utter_message(text="Se ha guardado el menu elegido.")
        dispatcher.utter_message(text="Tu menu se compone de:")
        MenuGetUser.run(self, dispatcher, tracker, domain)

        return [SlotSet("menu_establecido", True)]


class ValidateMenuPlatoCategoriaForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_menu_plato_categoria_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    async def extract_menu_plato_categoria(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_menu_plato_categoria")

        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_categoria is not None:
            menu_plato_categoria = menu_plato_categoria.lower()
            if menu_plato_categoria in CATEGORIA_MENU:
                return {"menu_plato_categoria": menu_plato_categoria}
        return {"menu_plato_categoria": None}

    def validate_menu_plato_categoria(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_menu_plato_categoria")

        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_categoria is not None:
            menu_plato_categoria = menu_plato_categoria.lower()
        else:
            return {"menu_plato_categoria": None}

        if menu_plato_categoria not in CATEGORIA_MENU:
            buttons = []
            for it in CATEGORIA_MENU:
                buttons.append({"title": "{}".format(
                    it.capitalize()), "payload": "{}".format(it)})
            dispatcher.utter_message(
                "No reconozco esa categoria, elige una de las siguientes:", buttons=buttons, button_type="vertical")
            return {"menu_plato_categoria": None}
        else:
            return {"menu_plato_categoria": menu_plato_categoria}


class ValidateMenuPlatoIDForm(FormValidationAction):
    def name(self) -> Text:
        return 'validate_menu_plato_id_form'

    async def required_slots(
        self, slots_mapped_in_domain: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Optional[List[Text]]:
        print("Required slots menu_plato_id")
        return slots_mapped_in_domain

    async def extract_menu_plato_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        print("extract_menu_plato_id")

        intent = tracker.get_intent_of_latest_message()
        if intent == "stop":
            return {"requested_slot": None, "menu_plato_id": None, "menu_plato_categoria": None}

        menu_plato_id = tracker.get_slot("menu_plato_id")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")

        if menu_plato_categoria is None:
            dispatcher.utter_message(
                text=f'No se ha introducido una categoria, parando el proceso.')
            return {"requested_slot": None, "menu_plato_id": None}

        if menu_plato_id is not None:
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break

            data = auxiliar.get_data_generic(
                DATA_PATH+"/data/menu/"+menu_plato_categoria+".json")
            for it in data[menu_plato_categoria]:
                if it['id'] == str(menu_plato_id):
                    return {"menu_plato_id": menu_plato_id}
            buttons = MenuGet.get_submenu_botones(self, menu_plato_categoria)
            dispatcher.utter_message(
                text=f'No se ha encontrado ese identificador, selecciona uno de los siguientes:', buttons=buttons, button_type="vertical")
            return {"menu_plato_categoria": menu_plato_categoria, "menu_plato_id": None}
        else:
            return {"menu_plato_id": None}

    def validate_menu_plato_id(
        self, slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker, domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_menu_plato_id")
        intent = tracker.get_intent_of_latest_message()
        if intent == "stop":
            return {"requested_slot": None, "menu_plato_id": None, "menu_plato_categoria": None}
        menu_plato_id = tracker.get_slot("menu_plato_id")
        menu_plato_categoria = tracker.get_slot("menu_plato_categoria")
        if menu_plato_id is not None:
            for it in CATEGORIA_MENU:
                if menu_plato_categoria in it:
                    menu_plato_categoria = it
                    break

            data = auxiliar.get_data_generic(
                DATA_PATH+"/data/menu/"+menu_plato_categoria+".json")

            menu_bebida_id = tracker.get_slot("menu_bebida_id")
            menu_plato_1_id = tracker.get_slot("menu_plato_1_id")
            menu_plato_2_id = tracker.get_slot("menu_plato_2_id")
            menu_plato_3_id = tracker.get_slot("menu_plato_3_id")

            if menu_plato_categoria == "bebidas":
                for it in data[menu_plato_categoria]:
                    if it['id'] == str(menu_plato_id):
                        message = "Guardado plato " + menu_plato_categoria + \
                            ":\n- " + it['nombre'] + " (" + it['precio'] + ")"
                        if menu_bebida_id is None:
                            dispatcher.utter_message(text=message)
                            return {"menu_hay_plato": True, "menu_plato_id": menu_plato_id, "menu_bebida_id": menu_plato_id, "menu_bebida_nombre": it['nombre'], "menu_bebida_precio": it['precio']}
                        message = "La bebida ya ha sido seleccionada, si deseas cambiarla elimina la bebida y vuelve a asignarla."
                        dispatcher.utter_message(text=message)
            else:
                for it in data[menu_plato_categoria]:
                    if it['id'] == str(menu_plato_id):
                        message = "Guardado plato " + menu_plato_categoria + \
                            ":\n- " + it['nombre'] + " (" + it['precio'] + ")"
                        if menu_plato_1_id is None:
                            dispatcher.utter_message(text=message)
                            return {"menu_hay_plato": True, "menu_plato_id": menu_plato_id, "menu_plato_1_id": menu_plato_id, "menu_plato_1_nombre": it['nombre'], "menu_plato_1_precio": it['precio']}
                        elif menu_plato_2_id is None:
                            dispatcher.utter_message(text=message)
                            return {"menu_hay_plato": True, "menu_plato_id": menu_plato_id, "menu_plato_2_id": menu_plato_id, "menu_plato_2_nombre": it['nombre'], "menu_plato_2_precio": it['precio']}
                        elif menu_plato_3_id is None:
                            dispatcher.utter_message(text=message)
                            return {"menu_hay_plato": True, "menu_plato_id": menu_plato_id, "menu_plato_3_id": menu_plato_id, "menu_plato_3_nombre": it['nombre'], "menu_plato_3_precio": it['precio']}
                        message = "Ya has seleccionado los tres platos disponibles, si deseas cambiar un plato elimina el plato elegido que desees y vuelve a asignarlo."
                        dispatcher.utter_message(text=message)
        return {"requested_slot": None, "menu_plato_id": None}
