from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models


# Create your models here.

class CommentManager(models.Manager):
    """
        Custom Comment manager

        Extends models.Manager
    """
    def all(self):
        """
            override all()

            return the root comments (that do not have a parent comment) : comments that are not replies
        """
        qs = super(CommentManager, self).filter(parent_id=None)
        return qs

    def filter_by_instance(self, instance):
        """
            Filtering  using the given instance
            It filters comments by instance content type and instance object id
            It returns only root comments (that do not have a parent comment) comments that are not replies
        """
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent_id=None)
        return qs

    def count_instance_comments(self, instance):
        """
            Counts the number of comments of the object instance.
        """
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        count = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).count()
        return count

    def create_by_model_type(self, model_type, slug, content, author, parent_obj=None):
        """
            Creates a new comment (contains some extra operations due to the use of content type)
        """
        model_qs = ContentType.objects.filter(model = model_type)
        if model_qs.exists():
            SomeModel = model_qs.first().model_class()
            obj_qs = SomeModel.objects.filter(slug=slug)
            if obj_qs.exists() and obj_qs.count() == 1:
                instance = self.model()
                instance.author = author
                instance.content_type = model_qs.first()
                instance.object_id = obj_qs.first().id
                if parent_obj:
                    instance.parent_id = parent_obj
                instance.content = content
                instance.save()
                return instance
        return None


class Comment(models.Model):
    """
        Comment model
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()  # Id of the post where the comment was written. it's ('content_type',
    #  'object_id') that link a comment to a post where content_type is the content type of the post (in this
    #  case it's post) and the object_id is the id of the post
    content_object = GenericForeignKey('content_type', 'object_id') # see GenericForeignKey in
    # https://docs.djangoproject.com/fr/1.11/ref/contrib/contenttypes/
    parent_id = models.ForeignKey("self", null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


    objects = CommentManager()

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return str(self.author.username)

    def __str__(self):
        return str(self.author.username)


    def children(self):
        """
            Return comment that are replies to the current comment (self)
        """
        return Comment.objects.filter(parent_id=self).order_by('timestamp')

    @property
    def is_parent(self):
        """
            define a property which is True if the comment is a parent, False if not.
        """
        if self.parent_id is None:
            return True
        return False



