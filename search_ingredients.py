import base64
import json
from tkinter import *
import aiohttp
import asyncio
from matplotlib.pyplot import margins
import requests
from PIL import Image, ImageTk
from io import BytesIO

from numpy import pad
import urllib.request


class SearchIngredients:
    def __init__(self) -> None:
        self.ingredients = []
        self.recipes = []
        self.root = Tk()
        self.root.iconbitmap("mealgen.ico")
        self.root.title("MealGenerator - A meal in your fridge")
        self.loop = asyncio.get_event_loop()

    async def find_recipes(self, recipes_list: Listbox):
        found_recipes = []
        async with aiohttp.ClientSession() as session:
            for ing in self.ingredients:
                async with session.get(
                        "https://www.themealdb.com/api/json/v1/1/filter.php?i={}".format(ing)) as res:
                    recipes = await res.json()
                    if recipes['meals']:
                        recipes_set = {json.dumps(reci)
                                       for reci in recipes['meals']}
                        found_recipes.append(recipes_set)
        if found_recipes:
            matching_recipes = found_recipes[0].intersection(
                *found_recipes[1:])
            for recipe_str in matching_recipes:
                recipe_dict = json.loads(recipe_str)
                if recipe_dict:
                    recipes_list.insert(END, recipe_dict["strMeal"])
                    self.recipes.append(recipe_dict)

    def add_ingredient(self, entry: Entry, listbox: Listbox):
        new_ingredient = entry.get()
        if not new_ingredient:
            return
        self.ingredients.append(new_ingredient)
        listbox.insert(END, new_ingredient)
        entry.delete(0, END)

    def clear_ingredients(self, listbox: Listbox):
        self.ingredients = []
        listbox.delete(0, END)

    async def select_recipe(self, listbox: Listbox):
        curr_selection = listbox.get(ANCHOR)
        if not curr_selection:
            self.recipe_title.config(text="No recipes selected.")
            self.recipe_instructions.config(state=NORMAL, height=0)
            self.recipe_instructions.delete("1.0", END)
            self.recipe_instructions.config(state=DISABLED)
            return
        recipe_data = next(
            recipe for recipe in self.recipes if recipe["strMeal"] == curr_selection)
        if not recipe_data:
            return False
        res = requests.get(
            f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={recipe_data['idMeal']}"
        )
        recipe_json = res.json()
        recipe_details = recipe_json["meals"][0]
        if not recipe_details:
            return False

        with urllib.request.urlopen(recipe_details["strMealThumb"]) as u:
            raw_data = u.read()
        loaded_image_data = Image.open((BytesIO(raw_data)))
        self.recipe_image = ImageTk.PhotoImage(
            loaded_image_data.resize(size=(200, 200)))

        self.recipe_title.config(text=recipe_details["strMeal"])
        self.recipe_instructions.config(state=NORMAL, height=15)
        self.recipe_instructions.delete("1.0", END)
        self.recipe_instructions.insert("1.0", "\t\t\t")
        self.recipe_instructions.image_create(
            '4.0', image=self.recipe_image, align="center")
        self.recipe_instructions.insert(END, "\n\n")
        self.recipe_instructions.insert(
            END, recipe_details["strInstructions"])
        self.recipe_instructions.config(state=DISABLED)

    def create_screen(self):
        header = Label(self.root, text="MealGenerator", font='Arial 19 bold')
        inst_label = Label(
            self.root, text="Please type all the ingredients you have")
        ingredients_entry = Entry(self.root, width=70)
        ingredients_header = Label(self.root, text="Ingredients:")
        ingredients_list = Listbox(
            self.root, height=5, width=75)
        recipes_header = Label(self.root, text="Recipes:")
        recipes_list = Listbox(
            self.root, height=5, width=75)
        clear_all_ingredients_button = Button(
            self.root, text="Clear ingredients",
            fg="#fafafa", bg="#d14",
            command=lambda: self.clear_ingredients(ingredients_list))
        get_instructions = Button(text="Get instructions for recipe",
                                  fg="#fafafa", bg="#f77f00",
                                  command=lambda: self.loop.run_until_complete(self.select_recipe(recipes_list)))
        add_ingredient_button = Button(
            self.root, text="Add ingredient",
            bg="#52b788", fg="#fafafa",
            command=lambda: self.add_ingredient(ingredients_entry, ingredients_list))
        find_recipes_button = Button(
            self.root, text="Find all recipes", fg="#fafafa", bg="#11d",
            command=lambda: self.loop.run_until_complete(self.find_recipes(recipes_list)))
        self.recipe_title = Label(
            self.root, text="No recipes selected.", font='Arial 9 bold')
        m = Message(self.root)
        self.recipe_instructions = Text(self.root, relief="flat", background=m.cget("background"),
                                        borderwidth=0, state="disabled", font='Arial 8', height=0,
                                        wrap=WORD, spacing1=2, padx=15, pady=15)
        m.destroy()
        header.grid(row=0, column=0, columnspan=4)
        inst_label.grid(row=1, column=0, columnspan=2)
        ingredients_entry.grid(row=2, column=0)
        add_ingredient_button.grid(row=2, column=1)
        clear_all_ingredients_button.grid(row=2, column=2, columnspan=4)
        find_recipes_button.grid(row=3, column=0, columnspan=4)
        ingredients_header.grid(row=5, column=0, columnspan=4)
        ingredients_list.grid(row=6, column=0, columnspan=4)
        recipes_header.grid(row=11, column=0, columnspan=4)
        recipes_list.grid(row=12, column=0, columnspan=4)
        get_instructions.grid(row=17, column=0, columnspan=4)
        self.recipe_title.grid(row=18, column=0, columnspan=3)
        self.recipe_instructions.grid(row=19, column=0, columnspan=3)
        self.root.mainloop()
