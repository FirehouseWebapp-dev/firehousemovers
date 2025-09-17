# Analytics Dashboard Caching

This document describes the caching implementation for the analytics dashboard to improve performance for senior managers.

## Overview

The analytics dashboard contains pre-computed data that doesn't change frequently, making it an ideal candidate for caching. The implementation includes:

- **View-level caching**: Caches the entire dashboard response for 30 minutes
- **Template fragment caching**: Caches expensive template sections
- **Cache invalidation**: Automatically invalidates cache when evaluation data changes
- **Cache warming**: Pre-computes analytics data for better performance

## Cache Configuration

### Settings

The caching is configured in `settings.py` with two cache backends:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default
    },
    'analytics': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'analytics-cache',
        'TIMEOUT': 1800,  # 30 minutes for analytics data
    }
}
```

### Production Configuration

In production, the cache automatically switches to Redis:

```python
if APP_ENV == "production":
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
    CACHES['analytics'] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/2'),
    }
```

## Implementation Details

### View-Level Caching

The `senior_manager_analytics_dashboard` view includes intelligent caching:

```python
@login_required
@require_senior_management_access
def senior_manager_analytics_dashboard(request):
    # Create cache key based on user and date
    cache_key = f"analytics_dashboard_{request.user.id}_{today_date}"
    
    # Try to get cached data first
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, "template.html", cached_data)
    
    # Compute expensive analytics data...
    # Cache the result for 30 minutes
    cache.set(cache_key, context_data, timeout=1800)
```

### Template Fragment Caching

Expensive template sections are cached using Django's template fragment caching:

```django
{% cache 1800 department_performance_section today %}
<!-- Department Performance Section -->
<div class="analytics-section mb-8">
    <!-- Expensive department analytics content -->
</div>
{% endcache %}
```

### Cache Invalidation

Cache is automatically invalidated when evaluation data changes:

```python
@receiver(post_save, sender=DynamicEvaluation)
def invalidate_cache_on_evaluation_save(sender, instance, created, **kwargs):
    invalidate_analytics_cache()
```

## Management Commands

### Warm Analytics Cache

Pre-compute analytics data for all senior managers:

```bash
python manage.py warm_analytics_cache
```

Warm cache for a specific user:

```bash
python manage.py warm_analytics_cache --user-id 123
```

### Manage Analytics Cache

Clear all analytics cache:

```bash
python manage.py manage_analytics_cache clear
```

Warm analytics cache:

```bash
python manage.py manage_analytics_cache warm
```

Check cache status:

```bash
python manage.py manage_analytics_cache status
```

## Cache Keys

The caching system uses the following key patterns:

- **View cache**: `analytics_dashboard_{user_id}_{date}`
- **Template fragments**: `department_performance_section`, `teams_performance_section`, `manager_effectiveness_section`

## Performance Benefits

### Before Caching
- Complex database queries for each request
- Multiple N+1 query problems
- Template rendering for expensive sections
- Response time: ~2-5 seconds

### After Caching
- Cached data served from memory/Redis
- No database queries for cached requests
- Pre-rendered template fragments
- Response time: ~50-200ms

## Cache Invalidation Strategy

The cache is invalidated in the following scenarios:

1. **Evaluation Creation/Update**: When a `DynamicEvaluation` is saved
2. **Evaluation Deletion**: When a `DynamicEvaluation` is deleted
3. **Manager Evaluation Changes**: When a `DynamicManagerEvaluation` is modified
4. **Manual Invalidation**: Via management commands

## Monitoring and Maintenance

### Cache Hit Rate Monitoring

Monitor cache performance using Django's cache framework:

```python
from django.core.cache import cache

# Check cache statistics
stats = cache.get_stats()
print(f"Cache hit rate: {stats.get('hit_rate', 'N/A')}")
```

### Scheduled Cache Warming

Set up a cron job to warm the cache periodically:

```bash
# Warm cache every 15 minutes
*/15 * * * * cd /path/to/project && python manage.py warm_analytics_cache
```

### Cache Size Monitoring

Monitor cache size to prevent memory issues:

```python
# Check cache size (Redis)
redis-cli info memory
```

## Troubleshooting

### Cache Not Working

1. Check cache configuration in `settings.py`
2. Verify cache backend is running (Redis in production)
3. Check cache permissions and connectivity

### Stale Data

1. Verify cache invalidation signals are working
2. Check if evaluation models are properly connected
3. Manually clear cache: `python manage.py manage_analytics_cache clear`

### Performance Issues

1. Monitor cache hit rates
2. Check cache size and memory usage
3. Verify cache warming is working
4. Consider adjusting cache timeout values

## Best Practices

1. **Cache Warming**: Run cache warming during low-traffic periods
2. **Monitoring**: Set up alerts for cache hit rates and performance
3. **Cleanup**: Regularly clear old cache entries
4. **Testing**: Test cache invalidation in development
5. **Documentation**: Keep cache keys and strategies documented

## Future Enhancements

1. **Cache Compression**: Compress large cache entries
2. **Distributed Caching**: Use Redis Cluster for high availability
3. **Cache Analytics**: Implement detailed cache performance monitoring
4. **Smart Invalidation**: More granular cache invalidation based on data changes
5. **Cache Preloading**: Preload cache based on user access patterns
