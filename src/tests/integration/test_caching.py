import pytest
from httpx import AsyncClient
from redis.asyncio import Redis


class TestPostCaching:
    """Тесты логики кеширования постов."""

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

        # 3. Первый GET — miss
        get_response_1 = await client.get(f"/api/posts/{post_id}")
        assert get_response_1.status_code == 200

        # 4. Проверяем что кэш записался
        cached = await redis.get(f"post:{post_id}")
        assert cached is not None, "Кэш должен быть записан после первого GET"

        # 5. Второй GET — hit
        get_response_2 = await client.get(f"/api/posts/{post_id}")
        assert get_response_2.status_code == 200

        # 6. Данные идентичны
        assert get_response_1.json() == get_response_2.json()
