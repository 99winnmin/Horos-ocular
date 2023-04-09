from datetime import datetime, timezone, timedelta

from django.db import models

# Create your models here.
class Video(models.Model):
    owner = models.ForeignKey("accounts.User",
                               on_delete=models.CASCADE,
                               db_column='owner',null=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    complete = models.SmallIntegerField(default=0, null=True)
    vname = models.CharField(max_length=255, null=True)
    video_url = models.CharField(max_length=255, null=True)
    npz_url = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.vname

    class Meta:
        db_table = 'videos'

    # @property
    # def created_string(self):
    #     time = datetime.now(tz=timezone.utc) - self.date
    #     if time < timedelta(minutes=1):
    #         return '방금 전'
    #     elif time < timedelta(hours=1):
    #         return str(int(time.seconds / 60)) + '분 전'
    #     elif time < timedelta(days=1):
    #         return str(int(time.seconds / 3600)) + '시간 전'
    #     elif time < timedelta(days=7):
    #         time = datetime.now(tz=timezone.utc).date() - self.date.date()
    #         return str(time.days) + '일 전'
    #     else:
    #         return False

class VInfo(models.Model):
    video = models.ForeignKey("horus.Video",
                               on_delete=models.CASCADE,
                               db_column='video',null=True)
    video_info_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.video_info_id

    class Meta:
        db_table = 'vinfo'