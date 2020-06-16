from django.db import models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels


class AdAzStatus(models.Model):
    status = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "وضعیت های آزمایش"

    def __str__(self):
        return str(self.status)


class AdReqStatus(models.Model):
    status = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "وضعیت های درخواست"

    def __str__(self):
        return str(self.status)


class AdAccStatus(models.Model):
    status = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "سلسله مراتب حسابها"

    def __str__(self):
        return str(self.status)


class AdTestType0(models.Model):  # class
    type = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "نوع آزمایش"

    def __str__(self):
        return str(self.type)


class AdTestType(models.Model):  # class
    type = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "کلاس تست"

    def __str__(self):
        return str(self.type)


class AdTestType1(models.Model):  # bf/cf ac/dc
    type = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "کلاس تست 2"

    def __str__(self):
        return str(self.type)


class Country(models.Model):
    name = models.TextField(verbose_name='نام کشور')

    class Meta:
        verbose_name_plural = "کشور ها"

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.TextField(verbose_name='نام استان')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='نام کشور')
    eng_name = models.TextField(verbose_name='نام انگلیسی استان')

    class Meta:
        verbose_name_plural = "استان ها"

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='نام استان')
    name = models.TextField(verbose_name='نام شهر')
    eng_name = models.TextField(verbose_name='نام انگلیسی شهر')

    class Meta:
        verbose_name_plural = "شهر ها"

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.TextField(verbose_name='نام بخش')
    eng_name = models.TextField(verbose_name='نام انگلیسی بخش')

    class Meta:
        verbose_name_plural = "بخش های بیمارستان"

    def __str__(self):
        return self.name


class Parameters(models.Model):
    name = models.TextField()
    value = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "پارامتر ها"

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='شناسه کاربر')
    avatar = models.ImageField(
        upload_to='avatar/', verbose_name='تصویر کاربر')
    signature = models.ImageField(
        upload_to='signature/', null=True, blank=True, verbose_name='تصویر امضا')
    status = models.ForeignKey(AdAccStatus, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "1_مشخصات کاربران"

    def __str__(self):
        return self.user.first_name


class Hospital(models.Model):
    name = models.TextField(verbose_name='نام بیمارستان')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='شهر')
    address = models.TextField(verbose_name='آدرس بیمارستان')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='شناسه کاربری بیمارستان')

    class Meta:
        verbose_name_plural = "2_بیمارستان ها"

    def __str__(self):
        return str(self.name) + ' ' + str(self.city.name)


class Company(models.Model):
    name = models.TextField(verbose_name='نام شرکت')
    en_name = models.TextField(verbose_name='نام انگلیسی شرکت')
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='کشور')

    class Meta:
        verbose_name_plural = "شرکت های سازنده"

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    name = models.TextField(verbose_name='نوع دستگاه')

    class Meta:
        verbose_name_plural = "نوع دستگاه ها"

    def __str__(self):
        return self.name


class Device(models.Model):
    name = models.TextField(verbose_name='اسم مدل دستگاه')
    type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, verbose_name='نوع دستگاه')
    creator = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='شرکت سازنده')

    class Meta:
        verbose_name_plural = "لیست دستگاه"

    def __str__(self):
        return self.name


class CalDevice(models.Model):
    name = models.TextField(verbose_name='نام دستگاه کالیبره')
    type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, verbose_name='نوع دستگاه')
    creator = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='شرکت سازنده')
    serial = models.CharField(max_length=30, verbose_name='سریال دستگاه کالیبره')
    calibration_date = models.DateField(verbose_name='تاریخ شروع کالیبراسیون')
    calibration_Expire_date = models.DateField(verbose_name='تاریخ اتمام کالیبراسیون')

    class Meta:
        verbose_name_plural = "4_دستگاه های کنترل کیفی"

    def __str__(self):
        return self.name


class AllDevice(models.Model):
    name = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='نام مدل دستگاه')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, verbose_name='نام بیمارستان')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name='نام بخش')
    serial_number = models.TextField(null=True, blank=True, verbose_name='شماره سریال دستگاه')
    property_number = models.IntegerField(null=True, blank=True, verbose_name='شماره اموال دستگاه')

    class Meta:
        verbose_name_plural = "3_دستگاه های ثبت شده"

    def __str__(self):
        return str(self.name) + ' - ' + str(self.hospital.name) + ' - ' + str(self.serial_number)


class Request(models.Model):
    date = jmodels.jDateField(verbose_name='تاریخ میلادی دستگاه')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, verbose_name='نام بیمارستان')
    number = models.IntegerField(verbose_name='شماره درخواست')
    status = models.ForeignKey(
        AdReqStatus, on_delete=models.CASCADE, default=1, verbose_name='وضعیت درخواست')

    class Meta:
        verbose_name_plural = "5_لیست درخواست ها"

    def __str__(self):
        return str(self.number)


class Record(models.Model):
    number = models.IntegerField(primary_key=True, verbose_name='شماره رکورد')

    class Meta:
        verbose_name_plural = "شماره رکورد"

    def __str__(self):
        return str(self.number)


class Licence(models.Model):
    number = models.IntegerField(verbose_name='شماره گواهی')

    class Meta:
        verbose_name_plural = "شماره گواهی"

    def __str__(self):
        return str(self.number)


class Accessory(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام لوازم جانبی')
    type = models.ForeignKey(DeviceType, on_delete=models.PROTECT, verbose_name='نوع لوازم جانبی')
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name='شرکت سازنده')

    class Meta:
        verbose_name_plural = "لوازم جانبی"

    def __str__(self):
        return str(self.name)


class AdExcelArg(models.Model):
    arg = models.TextField()

    class Meta:
        verbose_name_plural = "آرگومان اکسل"

    def __str__(self):
        return self.arg


class Comment(models.Model):
    comment = models.CharField(max_length=50, verbose_name='شرح توضیح')

    class Meta:
        verbose_name_plural = "توضیحات"

    def __str__(self):
        return str(self.comment)
