from django.db import models

# Create your models here.


class Sex(models.TextChoices):
    MALE = "Male"
    FEMALE = "Female"
    # NOT_INFORMED = "Not Informed"
    DEFAULT = "Not Informed"


class Pet(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    weight = models.FloatField()
    sex = models.CharField(
        max_length=20,
        choices=Sex.choices,
        default=Sex.DEFAULT,
    )

    group = models.ForeignKey(
        "groups.Group", on_delete=models.PROTECT, related_name="pets"
    )

    def __repr__(self) -> str:
        return f"<Pet ({self.id}) - {self.name}>"
