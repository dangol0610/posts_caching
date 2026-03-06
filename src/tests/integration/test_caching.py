import asyncio

import pytest
from httpx import AsyncClient
from redis.asyncio import Redis


class TestPostCaching:
    """Интеграционные тесты логики кеширования постов."""

    @pytest.mark.asyncio
    async def test_cache_miss_then_hit(self, client: AsyncClient, redis: Redis):
        """
        Первый GET — miss (данные из БД, записываются в кэш).
        Второй GET — hit (данные из кэша).
        """
        # 1. Создаём пост
        create_response = await client.post(
            "/api/posts/",
            json={"title": "Test Post", "content": "Test Content"},
        )
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]

        # 2. Очищаем кэш (гарантируем miss)
        await redis.delete(f"post:{post_id}")

        # 3. Проверяем, что кэш пуст ПЕРЕД первым GET
        assert await redis.get(f"post:{post_id}") is None

        # 4. Первый GET — miss
        get_response_1 = await client.get(f"/api/posts/{post_id}")
        assert get_response_1.status_code == 200

        # 5. Проверяем что кэш записался
        cached = await redis.get(f"post:{post_id}")
        assert cached is not None

        # 6. Второй GET — hit
        get_response_2 = await client.get(f"/api/posts/{post_id}")
        assert get_response_2.status_code == 200

        # 7. Данные идентичны
        assert get_response_1.json() == get_response_2.json()

    @pytest.mark.asyncio
    async def test_cache_updated_on_update(self, client: AsyncClient, redis: Redis):
        """
        При обновлении поста кэш должен быть обновлен.
        """
        # 1. Создаём пост
        create_response = await client.post(
            "/api/posts/",
            json={"title": "Test Post", "content": "Test Content"},
        )
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]

        # 2. Очищаем кэш (гарантируем miss)
        await redis.delete(f"post:{post_id}")

        # 3. Проверяем, что кэш пуст ПЕРЕД первым GET
        assert await redis.get(f"post:{post_id}") is None

        # 4. Первый GET — miss
        get_response_1 = await client.get(f"/api/posts/{post_id}")
        assert get_response_1.status_code == 200

        # 5. Проверяем что кэш записался
        cached = await redis.get(f"post:{post_id}")
        assert cached is not None

        # 6. Обновляем пост
        update_response = await client.patch(
            f"/api/posts/{post_id}",
            json={"title": "Updated Title", "content": "Updated Content"},
        )
        assert update_response.status_code == 200

        # 7. Кэш должен быть обновлён после обновления
        updated_cached = await redis.get(f"post:{post_id}")
        assert updated_cached != cached

    @pytest.mark.asyncio
    async def test_cache_invalidated_on_delete(self, client: AsyncClient, redis: Redis):
        """
        При удалении поста кэш должен быть очищен.
        """
        # 1. Создаём пост
        create_response = await client.post(
            "/api/posts/",
            json={"title": "Test Post", "content": "Test Content"},
        )
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]

        # 2. Очищаем кэш (гарантируем miss)
        await redis.delete(f"post:{post_id}")

        # 3. Проверяем, что кэш пуст ПЕРЕД первым GET
        assert await redis.get(f"post:{post_id}") is None

        # 4. Первый GET — miss
        get_response_1 = await client.get(f"/api/posts/{post_id}")
        assert get_response_1.status_code == 200

        # 5. Проверяем что кэш записался
        cached = await redis.get(f"post:{post_id}")
        assert cached is not None

        # 6. Удаляем пост
        delete_response = await client.delete(f"/api/posts/{post_id}")
        assert delete_response.status_code == 200

        # 7. Кэш должен быть очищен после удаления
        assert await redis.get(f"post:{post_id}") is None

    @pytest.mark.asyncio
    async def test_cache_ttl(self, client: AsyncClient, redis: Redis):
        """
        Кэш должен иметь TTL.
        """
        # 1. Создаём пост
        create_response = await client.post(
            "/api/posts/",
            json={"title": "Test Post", "content": "Test Content"},
        )
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]

        # 2. Первый GET — miss
        get_response_1 = await client.get(f"/api/posts/{post_id}")
        assert get_response_1.status_code == 200

        # 3. Проверяем что кэш записался
        cached = await redis.get(f"post:{post_id}")
        assert cached is not None

        # 4. Проверяем TTL
        ttl = await redis.ttl(f"post:{post_id}")
        assert ttl == 3600

    @pytest.mark.asyncio
    async def test_cache_ttl_expired(self, client: AsyncClient, redis: Redis):
        """
        Кэш должен быть очищен после срока жизни.
        """
        # 1. Создаём пост
        create_response = await client.post(
            "/api/posts/",
            json={"title": "Test Post", "content": "Test Content"},
        )
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]

        # 2. Первый GET — miss
        get_response_1 = await client.get(f"/api/posts/{post_id}")
        assert get_response_1.status_code == 200

        # 3. Проверяем что кэш записался
        cached = await redis.get(f"post:{post_id}")
        assert cached is not None

        # 4. Проверяем TTL
        ttl = await redis.ttl(f"post:{post_id}")
        assert ttl == 2

        # 4. Ждём срока жизни
        await asyncio.sleep(2)

        # 6. Проверяем что кэш очищен
        cached = await redis.get(f"post:{post_id}")
        assert cached is None
