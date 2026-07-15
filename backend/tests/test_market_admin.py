import pytest
from datetime import date


@pytest.mark.asyncio
async def test_seed_and_check_holiday(async_client):
    # seed a holiday (ALLOW_DEV_INIT is true in test env)
    items = [{'date': '2030-01-26', 'name': 'Test Republic Day'}]
    r = await async_client.post('/market/admin/seed-holidays', json=items)
    assert r.status_code == 200

    r2 = await async_client.get('/market/holiday', params={'date': '2030-01-26'})
    assert r2.status_code == 200
    data = r2.json()
    assert data['closed'] is True
    assert 'Republic' in data['reason']
