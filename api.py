import enum
from typing import Annotated
from livekit.agents import llm
import logging
import csv


logger = logging.getLogger("temperature-control")
logger.setLevel(logging.INFO)


def format_list(items):
    if not items:
        return ""  # Return an empty string for an empty list
    if len(items) == 1:
        return items[0]  # Return the single item directly
    if len(items) == 2:
        return " and ".join(items)  # Join two items with " and " without a comma
    return ", ".join(items[:-1]) + ", and " + items[-1]


class Pantry(enum.Enum):
    PANTRY = 'pantry'


class Zone(enum.Enum):
    TOP_SHELF = "top_shelf"
    MIDDLE_SHELF = "middle_shelf"
    BOTTOM_SHELF = "bottom_shelf"
    TOP_FREEZER_DRAWER = "top_freezer_drawer"
    BOTTOM_FREEZER_DRAWER = "bottom_freezer_drawer"


class DESTINATION(enum.Enum):
    WORK = "work"
    GYM = "gym"
    BANK = "bank"
    DOWNTOWN = "downtown"
    AIRPORT = "airport"
    GROCERY_STORE = "gorcery_store"


class APPS(enum.Enum):
    HOMESCREEN = "homescreen"
    REMINDERS = "reminders"
    GROCERY_LIST = "grocery_list"
    CALENDAR = "calendar"
    NEWS = "news"
    YOUTUBE = "youtube"
    CLOCK = "clock"




class AssistantFnc(llm.FunctionContext):
    def __init__(self) -> None:
        super().__init__()


        self._temperature = {
            Zone.TOP_SHELF: 40,
            Zone.MIDDLE_SHELF: 37,
            Zone.BOTTOM_SHELF: 35,
            Zone.TOP_FREEZER_DRAWER: 1,
            Zone.BOTTOM_FREEZER_DRAWER: 0,
        }


        # Inventory data
        self._inventory = {
            Zone.TOP_SHELF: ['ricotta', 'eggs', 'milk', 'jam'],
            Zone.MIDDLE_SHELF: ['soup', 'ground_beef', 'bacon'],
            Zone.BOTTOM_SHELF: ['strawberries', 'apples', 'pears'],
            Zone.TOP_FREEZER_DRAWER: [],
            Zone.BOTTOM_FREEZER_DRAWER: ['ice_cream'],
        }


        # Inventory data
        self._pantryinventory = {
            Pantry.PANTRY: ['cereal', 'flour', 'sugar', 'canned_garbanzo_beans'],
        }
        # commute data
        self._commute = {
            DESTINATION.WORK: 23,
            DESTINATION.GYM: 12,
            DESTINATION.BANK: 17,
            DESTINATION.DOWNTOWN: 43,
            DESTINATION.AIRPORT: 37,
            DESTINATION.GROCERY_STORE: 15
        }


        # current screen data
        self._screen = {
            APPS.HOMESCREEN: True,
            APPS.REMINDERS: False,
            APPS.GROCERY_LIST: False,
            APPS.CALENDAR: False,
            APPS.NEWS: False,
            APPS.YOUTUBE: False,
            APPS.CLOCK: False,
        }


    def save_to_csv(self, filename: str):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)


            # Save temperature data
            writer.writerow(['Zone', 'Temperature'])
            for key, value in self._temperature.items():
                writer.writerow([key, value])
            writer.writerow([])  # Empty row for separation


            # Save inventory data
            writer.writerow(['Zone', 'Items'])
            for key, items in self._inventory.items():
                writer.writerow([key, ', '.join(items)])
            writer.writerow([])


            # Save pantry inventory data
            writer.writerow(['Location', 'Items'])
            for key, items in self._pantryinventory.items():
                writer.writerow([key, ', '.join(items)])
            writer.writerow([])


            # Save commute data
            writer.writerow(['Destination', 'Time (minutes)'])
            for key, value in self._commute.items():
                writer.writerow([key, value])
            writer.writerow([])


            # Save screen data
            writer.writerow(['App', 'Is Active'])
            for key, value in self._screen.items():
                writer.writerow([key, value])
            writer.writerow([])
   
    def set_all_apps_to_false(self):
        # Set all values in the _screen dictionary to False
        for key in self._screen:
            self._screen[key] = False
        print("All APPS set to False")


    ## temperature methods
    @llm.ai_callable(description="get the temperature of the refrigerator section")
    def get_temperature(
        self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]
    ):
        logger.info("get temp - zone %s", zone)
        temp = self._temperature[Zone(zone)]
        self.save_to_csv('assistant_data.csv')
        return f"The temperature in the {zone} is {temp}F"


    @llm.ai_callable(description="set the temperature in one of the refrigerator section")
    def set_temperature(
        self,
        zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
        temp: Annotated[int, llm.TypeInfo(description="The temperature to set")],
    ):
        logger.info("set temo - zone %s, temp: %s", zone, temp)
        self._temperature[Zone(zone)] = temp
        self.save_to_csv('assistant_data.csv')
        return f"The temperature in the {zone} is now {temp}F"
   
    #inventory methods
    @llm.ai_callable(description="Get the inventory list of a refrigerator section")
    def get_inventory(
        self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]
    ):
        logger.info("get inventory - zone %s", zone)
        inventory = self._inventory[Zone(zone)]
        if not inventory:
            return f"The {zone} is empty."
        return f"The inventory in the {zone} includes: {format_list(inventory)}"
   
   


    @llm.ai_callable(description="Add an item to the inventory of a refrigerator section")
    def add_to_inventory(
        self,
        zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
        item: Annotated[str, llm.TypeInfo(description="The item to add to the inventory")],
    ):
        logger.info("add to inventory - zone %s, item: %s", zone, item)
        self._inventory[Zone(zone)].append(item)
        self.save_to_csv('assistant_data.csv')
        return f"{item} has been added to the {zone} inventory."
   
   
    @llm.ai_callable(description="Remove an item from the inventory of a refrigerator section")
    def remove_from_inventory(
        self,
        zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
        item: Annotated[str, llm.TypeInfo(description="The item to remove from the inventory")],
    ):
        logger.info("remove from inventory - zone %s, item: %s", zone, item)
        inventory = self._inventory[Zone(zone)]
        if item in inventory:
            inventory.remove(item)
            self.save_to_csv('assistant_data.csv')
            return f"{item} has been removed from the {zone} inventory."
        return f"{item} is not in the {zone} inventory."
   
    #inventory methods
    @llm.ai_callable(description="Get the pantry inventory list. These are not refrigerated")
    def get_pantry_inventory(
        self, pantry: Annotated[Pantry, llm.TypeInfo(description="The pantry area")]
    ):
        logger.info("get pantry inventory - pantry %s", pantry)
        pantryinventory = self._pantryinventory[Pantry(pantry)]
        self.save_to_csv('assistant_data.csv')
        if not pantryinventory:
            return f"The {pantry} is empty."
        return f"The inventory in the {pantry} includes: {format_list(pantryinventory)}"
   
   


    @llm.ai_callable(description="Add an item to the pantry")
    def add_to_pantry_inventory(
        self,
        pantry: Annotated[Pantry, llm.TypeInfo(description="The pantry area")],
        item: Annotated[str, llm.TypeInfo(description="The item to add to the pantry")],
    ):
        logger.info("add to pantry - pantry %s, item: %s", pantry, item)
        self._pantryinventory[Pantry(pantry)].append(item)
        self.save_to_csv('assistant_data.csv')
        return f"{item} has been added to the {pantry}."
   
   
    @llm.ai_callable(description="Remove an item from the pantry")
    def remove_from_pantry_inventory(
        self,
        pantry: Annotated[Pantry, llm.TypeInfo(description="The pantry area")],
        item: Annotated[str, llm.TypeInfo(description="The item to remove from the pantry")],
    ):
        logger.info("remove from pantry - pantry %s, item: %s", pantry, item)
        pantryinventory = self._pantryinventory[Pantry(pantry)]
        if item in pantryinventory:
            pantryinventory.remove(item)
            self.save_to_csv('assistant_data.csv')
            return f"{item} has been removed from the {pantry}."
        return f"{item} is not in the {pantry}."
       
   
    #commute methods
    @llm.ai_callable(description="Get the commute time to a given destination")
    def get_commute(
        self, destination: Annotated[DESTINATION, llm.TypeInfo(description="The specific destination")]
    ):
        logger.info("get commute - destination %s", destination)
        commute = self._commute[DESTINATION(destination)]


        return f"The commute time to the {destination} is: {commute} minutes."
   
    #screen methods
    @llm.ai_callable(description="Check if an app is displayed on the screen")
    def get_screen(
        self, app: Annotated[APPS, llm.TypeInfo(description="The specific app to check if displayed on the screen")]
    ):
        logger.info("get current app - app %s", app)
        screen = self._screen[APPS(app)]
        if screen:
            return f"{app} is currently showing on the screen."
        else:
            return f"{app} is currently not showing on the screen"


'''
    @llm.ai_callable(description="Change the screen to a given app")
    def change_app(
        self,
        apps: Annotated[APPS, llm.TypeInfo(description="Apps on the smart fridge available for viewing on the screen")],
        status: Annotated[bool, llm.TypeInfo(description="The status to switch the app to")],
    ):
        logger.info("swithcing apps %s, status: %s", apps, status)
        app_on_screen = self._screen[APPS(pantry)]
        if item in pantryinventory:
            pantryinventory.remove(item)
            self.save_to_csv('assistant_data.csv')
            return f"{item} has been removed from the {pantry}."
        return f"{item} is not in the {pantry}."


        '''
