import recipe, cookbook

cookbook.Cookbook.print_motivational_quote()
cookbook.Cookbook.print_motivational_quote()

cake = recipe.Dessert("Cake", ("mix all ingredients", "bake for 1 hour"), complexity=3, portions=5)
soup = recipe.Main_dish("Soup", ["boil everything"])
rizotto = recipe.Main_dish("Rizotto", ("put everything into a multicooker", "mix and add seasoning", "choose rizotto program"), equipment = "multicooker")

my_recipes = cookbook.Cookbook("My_recipes")
my_recipes.add_recipe(cake)
my_recipes.add_recipe(rizotto)

my_recipes.show_recipe("pancakes")
my_recipes.show_recipe("Cake")
my_recipes.delete_recipe("Cake")
my_recipes.show_recipe("Cake")

for r in soup, rizotto:
    r.cook()
