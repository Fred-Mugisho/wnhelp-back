from ..models import *

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "NOTIFICATIONS"
        verbose_name = "Notification"

    def __str__(self):
        return self.message
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
        
class NotificationSerializer(serializers.ModelSerializer):
    user = SimpleCustomUserSerializer()
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        
class MyNotifiacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
        
class NotificationSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['user', 'message']