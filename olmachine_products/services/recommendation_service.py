"""
Service for tracking user category views and generating recommendations.
"""

import logging
from django.db import transaction
from django.utils import timezone
from olmachine_products.models import (
    UserCategoryView,
    Category,
    Product
)
from olmachine_users.models import User

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for user recommendations based on viewing history."""

    MAX_TRACKED_CATEGORIES = 3

    @staticmethod
    def track_category_view(user: User, category: Category):
        """
        Track user's category view. Maintains last 3 categories.

        Args:
            user: User instance
            category: Category instance
        """
        try:
            with transaction.atomic():
                # Get or create the view record
                view, created = UserCategoryView.objects.get_or_create(
                    user=user,
                    category=category,
                    defaults={'viewed_at': timezone.now()}
                )

                if not created:
                    # Update viewed_at if already exists
                    view.viewed_at = timezone.now()
                    view.save()

                # Get all views for this user, ordered by most recent
                all_views = UserCategoryView.objects.filter(
                    user=user
                ).order_by('-viewed_at')

                # Keep only the last MAX_TRACKED_CATEGORIES
                if all_views.count() > RecommendationService.MAX_TRACKED_CATEGORIES:
                    views_to_delete = all_views[
                        RecommendationService.MAX_TRACKED_CATEGORIES:
                    ]
                    UserCategoryView.objects.filter(
                        id__in=[v.id for v in views_to_delete]
                    ).delete()

                logger.info(
                    f"Tracked category view: User {user.id} viewed "
                    f"Category {category.category_code}"
                )

        except Exception as e:
            logger.error(
                f"Error tracking category view: {str(e)}",
                exc_info=True
            )

    @staticmethod
    def get_user_recent_categories(user: User, limit: int = 3):
        """
        Get user's recently viewed categories.

        Args:
            user: User instance
            limit: Number of recent categories to return

        Returns:
            QuerySet: Recent categories ordered by most recent
        """
        try:
            recent_views = UserCategoryView.objects.filter(
                user=user
            ).select_related('category').order_by('-viewed_at')[:limit]

            return [view.category for view in recent_views if view.category.is_active]

        except Exception as e:
            logger.error(
                f"Error getting recent categories: {str(e)}",
                exc_info=True
            )
            return []

    @staticmethod
    def get_recommended_products(user: User, products_per_category: int = 3):
        """
        Get recommended products based on user's viewing history.

        Args:
            user: User instance
            products_per_category: Number of products to return per category

        Returns:
            list: List of dictionaries with category and products
        """
        try:
            recent_categories = (
                RecommendationService.get_user_recent_categories(
                    user,
                    limit=RecommendationService.MAX_TRACKED_CATEGORIES
                )
            )

            if not recent_categories:
                return []

            recommended_data = []
            for category in recent_categories:
                # Get top products from this category
                products = Product.objects.filter(
                    category=category,
                    is_active=True
                ).select_related(
                    'seller',
                    'location'
                ).prefetch_related(
                    'images',
                    'specifications'
                ).order_by('-created_at')[:products_per_category]

                if products.exists():
                    recommended_data.append({
                        'category': category,
                        'products': products
                    })

            return recommended_data

        except Exception as e:
            logger.error(
                f"Error getting recommended products: {str(e)}",
                exc_info=True
            )
            return []

