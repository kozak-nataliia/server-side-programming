class Recipe:
    
    def __init__(self, title, instructions, **kwargs):
        self.title = title
        self.instructions = instructions
        self.properties = kwargs
        
class Pretty_instructions:
    def init(self):
        self.n = 1

    def step(self, instruction):
        print(f"{self.n}. {instruction}", end=' ')
        self.n += 1
    

class Dessert(Recipe, Pretty_instructions):
    def __init__(self, title, instructions, **kwargs):
        super().__init__(title, instructions, **kwargs)
    
    def cook(self):
        print("\nIt's time for a Dessert")
        print(self.title)
        for key, value in self.properties.items():
            print(f"{key} -> {value}")
        self.init()
        for i in self.instructions:
            self.step(i)
            print("🍰")            

class Main_dish(Recipe, Pretty_instructions):
    def __init__(self, title, instructions, **kwargs):
        super().__init__(title, instructions, **kwargs)
    
    def cook(self):
        print("\nIt's time for a Main_dish")
        print(self.title)
        for key, value in self.properties.items():
            print(f"{key} = {value}")
        self.init()
        for i in self.instructions:
            self.step(i)  
            print("🍜")   

        
        