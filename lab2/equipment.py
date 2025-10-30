class Grater:
    @staticmethod
    def grate(ingredient):
        print("grating", ingredient)

class Blender:
    @staticmethod
    def blend(ingredient):
        print("blending", ingredient)
        
class Combiner(Grater, Blender):
    @staticmethod
    def chop(ingredient):
        print("chopping", ingredient)

