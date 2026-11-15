def test_unconfigured_feed_never_fabricates_prices(client, auth):
    assert client.get('/api/v1/stocks/DEMO', headers=auth).status_code == 503
    response = client.get('/api/v1/zakat/metal-prices', headers=auth).json()
    assert response['prices'] is None
    assert response['is_live'] is False
    assert response['source'] == 'manual_entry_required'
