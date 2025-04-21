# from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models, transaction
from django.db.models import Count, F, Q
from django.core.cache import cache
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from apps.category.enums import StatusChoices
from commons.mixins import ModelMixin


# User = get_user_model()

# Create your models here.
class Category(ModelMixin):
    name = models.CharField(max_length=255, unique=True)
    image = CloudinaryField('image', null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.STATUS_PENDING
    )
    
    is_predefined = models.BooleanField(
        default=False,
        help_text="If True, this category was added by an admin."
    )
    
    requested_by = models.ForeignKey(
        'accounts.CustomUser', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_categories'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        # If the category is predefined, ensure it's approved
        if self.is_predefined:
            self.status = StatusChoices.STATUS_APPROVED
        super().save(*args, **kwargs)

    @classmethod
    def get_fields(cls):
        """
        Returns the fields of the Category model.
        """
        return [
            "id",
            "name",
            "image",
            "status",
            # "requested_by__username",
            "is_predefined",
            "created_at"
        ]
    
    @classmethod
    def list_categories(cls):
        """
        Returns all categories ordered alphabetically.
        """
        categories = cls.objects.all().order_by("name")
        print("listed categories=======", categories)
        return categories.values(*cls.get_fields())
    
    @classmethod
    def create_category(cls, **kwargs):
        """
        Creates a new category if it does not already exist.
        """
        category = cls.objects.create(**kwargs)
        return category
    
    @classmethod
    def update_category(cls, category_id, **kwargs):
        """
        Updates an existing category's details.
        """
        return cls.objects.filter(id=category_id).update(**kwargs)
    
    @classmethod
    def delete_category(cls, category_id):
        """
        Deletes a category by its ID.
        """
        return cls.objects.filter(id=category_id).delete()[0] > 0
    
    @classmethod
    def get_experts_for_category(cls, category_name):
        """
        Retrieves all experts who have a specific category.
        """
        try:
            category = cls.objects.prefetch_related('experts__user').get(name__iexact=category_name)
            return category.experts.all()  # Prefetched in one query
        except cls.DoesNotExist:
            return []
    
    @classmethod
    def most_popular_categories(cls, limit=10):
        """
        Returns the most popular categories based on the number of experts who have them via skills.
        """
        return (
            cls.objects
            .annotate(expert_count=Count('skills__experts', distinct=True))
            .values('id', 'name', 'image', 'expert_count', 'status', 'is_predefined')
            .order_by('-expert_count')[:limit]
        )
    


class Skill(ModelMixin):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    code = models.CharField(max_length=10, unique=True, db_index=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="skills"
    )

    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.STATUS_PENDING
    )

    requested_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_skills'
    )

    is_predefined = models.BooleanField(
        default=False,
        help_text="If True, this skill was added by an admin."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        # If the skill is predefined, ensure it's approved
        if self.is_predefined:
            self.status = StatusChoices.STATUS_APPROVED
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"
    

    @classmethod
    def get_fields(cls):
        """
        Returns the fields of the Skill model.
        """
        return [
            "id",
            "name",
            "code",
            "category__name",
            "category__id",
            "status",
            # "requested_by__username",
            "is_predefined",
            "created_at"
        ]
    
    @classmethod
    def list_skills(cls):
        """
        Returns all skills ordered alphabetically.
        """
        skills = cls.objects.select_related("category").all().order_by("name")
        return skills.values(*cls.get_fields())
    

    @classmethod
    def create_skill(cls, **kwargs):
        """
        Creates a new skill if it does not already exist.
        """
        skill = cls.objects.create(**kwargs)
        return skill
    

    @classmethod
    def update_skill(cls, skill_id, **kwargs):
        """
        Updates an existing skill's details.
        """
        return cls.objects.filter(id=skill_id).update(**kwargs)
    
    @classmethod
    def list_all_skills(cls):
        """
        Returns all skills ordered alphabetically
        """
        return cls.objects.all().order_by("name").values("id", "name", "code")

    @classmethod
    def delete_skill(cls, skill_id):
        """
        Deletes a skill by its ID.
        """
        return cls.objects.filter(id=skill_id).delete()[0] > 0

    

    # @classmethod
    # def most_popular_skills(cls, limit=10):
    #     """
    #     Returns the most popular skills
    #     """
    #     cache_key = f"popular_skills_{limit}"
    #     popular_skills = cache.get(cache_key)

    #     if not popular_skills:
    #         popular_skills = (
    #             cls.objects
    #             .annotate(expert_count=Count('experts', distinct=True))
    #             .values_list('name', 'code', 'expert_count')
    #             .order_by('-expert_count')[:limit]
    #         )
    #         cache.set(cache_key, popular_skills, timeout=3600)  # Cache for 1 hour

    #     return popular_skills