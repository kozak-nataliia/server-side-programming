import random
class Cookbook:
    __random_seed = 47
    @staticmethod
    def print_motivational_quote():
        random.seed(Cookbook.__random_seed)
        print()
        print(random.choice(["A recipe has no soul. You as the cook must bring soul to the recipe.", "Real cooking is more about following your heart than following recipes.", "Cooking demands attention, patience, and above all, a respect for the gifts of the earth. It is a form of worship, a way of giving thanks."]))
        Cookbook.__random_seed += 1
        
    def __init__(self, name):
        self.name = name
        self.recipes = {}
        
    def add_recipe(self, recipe):
        self.recipes[recipe.title] = recipe
        
    def delete_recipe(self, title):
        self.recipes.pop(title, None)
        
    def show_recipe(self, title):
        if(not self.recipes.get(title)):
            print("\nThere is no such recipe")
        else:
            self.recipes.get(title).cook()

