from django.db import models

# Create your models here.
class CSVData(models.Model):
    #university
    column1 = models.CharField(max_length=400)
    #program
    column2 = models.CharField(max_length=400)
    #average
    column3 = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)
    #return the stuff as a tuple
    def as_tuple(self):
        return (self.column1, self.column2, self.column3)