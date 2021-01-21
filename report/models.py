from django.db import models
import acc.models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels


# Create your models here.
class Encode(models.Model):
    hospital = models.ForeignKey(acc.models.Hospital, on_delete=models.CASCADE, related_name='el')
    name = models.CharField(max_length=32)


class Report(models.Model):
    tt = models.ForeignKey(acc.models.AdTestType0, on_delete=models.PROTECT)
    device = models.ForeignKey(acc.models.AllDevice, on_delete=models.PROTECT)
    has_pdf = models.BooleanField(default=False)
    request = models.ForeignKey(acc.models.Request, on_delete=models.PROTECT)
    date = jmodels.jDateTimeField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    record = models.ForeignKey(acc.models.Record, on_delete=models.CASCADE, related_name='rr')
    ref_record = models.ForeignKey(acc.models.Record, on_delete=models.CASCADE, related_name='rrr')
    licence = models.ForeignKey(acc.models.Licence, on_delete=models.CASCADE, related_name='rl')
    status = models.ForeignKey(acc.models.AdAzStatus, on_delete=models.PROTECT)
    totalcomment = models.TextField(null=True, blank=True)
    is_done = models.BooleanField(default=False)
    is_recal = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "سابقه گزارشات"

    def __str__(self):
        return ' - '.join(('report', str(self.tt), str(self.licence)))
