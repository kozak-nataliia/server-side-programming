from django.db import models
from django.utils import timezone
# verbose_name - зрозумілий людині опис поля
# primary_key - ознака первинного ключа
# unique - ознака унікальності поля
# blank - ознака того, що поле може бути порожнім
# null - ознака того, що поле може мати значення NULL
# default - значення поля за замовчуванням
# db_index - в б.д. створиться індекс для цього поля

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IngredientCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RecipeCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Unit(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=16, blank=True, null=True, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.symbol or self.name


class Ingredient(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(
        IngredientCategory, on_delete=models.PROTECT, related_name="ingredients"
    )

    class Meta:
        indexes = [models.Index(fields=["name"])]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Recipe(TimeStampedModel):
    title = models.CharField(max_length=200, default="recipe_title")
    category = models.ForeignKey(
        RecipeCategory, on_delete=models.SET_NULL, blank=True, null=True, related_name="recipes"
    )
    instructions = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["title"]
        unique_together = [("title", "category")]

    def __str__(self) -> str:
        return self.title


class RecipeItem(TimeStampedModel):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="items")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT, related_name="used_in")
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        unique_together = [("recipe", "ingredient")]
        indexes = [
            models.Index(fields=["recipe"]),
            models.Index(fields=["ingredient"]),
        ]
        ordering = ["recipe_id", "id"]

    def __str__(self) -> str:
        u = f" {self.unit}" if self.unit else ""
        return f"{self.quantity}{u} {self.ingredient} for {self.recipe}"
