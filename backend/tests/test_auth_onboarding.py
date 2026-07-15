import pytest


@pytest.mark.asyncio
async def test_signup_onboarding_and_portfolio(async_client):
    # signup
    r = await async_client.post('/auth/signup', json={'email': 'bob@example.com', 'password': 'pass1234'})
    assert r.status_code == 200
    # client should now have cookies set (httpx client stores cookies)
    # perform onboarding
    # read csrf cookie
    csrf = None
    for cookie in async_client.cookies.jar:
        if cookie.name == 'csrf_token':
            csrf = cookie.value
    assert csrf is not None

    payload = {
        'full_name': 'Bob Test',
        'employment_status': 'Salaried',
        'annual_salary': 500000,
        'objectives': ['Wealth Creation', 'Learning Basics'],
        'risk_profile': 'Moderate',
        'starting_capital': 100000
    }
    headers = {'x-csrf-token': csrf}
    r2 = await async_client.post('/onboarding/complete', json=payload, headers=headers)
    assert r2.status_code == 200

    # portfolio summary should reflect starting capital
    r3 = await async_client.get('/portfolio/summary')
    assert r3.status_code == 200
    data = r3.json()
    assert data['cash'] == 100000 or float(data['cash']) == 100000.0
