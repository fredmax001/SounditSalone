import requests
import json

BASE = 'http://localhost:8000/api/v1'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc2OTg2MzkyLCJ0eXBlIjoiYWNjZXNzIn0.iz86EkI5tbar6aPgv79Z3OY8nyiEMBjdp42dezYU4CY'
HEADERS = {'Authorization': f'Bearer {TOKEN}'}

endpoints = [
    # Auth
    ('GET', '/admin/auth/logout', None),
    
    # Dashboard
    ('GET', '/admin/super/dashboard', None),
    ('GET', '/admin/dashboard', None),
    
    # Users
    ('GET', '/admin/users', None),
    ('GET', '/admin/users?role=organizer', None),
    ('GET', '/admin/users?status=active', None),
    ('PATCH', '/admin/users/1/suspend', {'reason': 'test'}),
    ('PATCH', '/admin/users/1/activate', None),
    ('POST', '/admin/users/1/suspend', {'reason': 'test'}),
    ('POST', '/admin/users/1/activate', None),
    ('POST', '/admin/users/1/freeze', None),
    ('POST', '/admin/users/1/unfreeze', None),
    
    # Events
    ('POST', '/admin/events/1/approve', None),
    ('POST', '/admin/events/1/reject', {'reason': 'test'}),
    ('POST', '/admin/events/1/disable', None),
    ('POST', '/admin/events/1/enable', None),
    ('POST', '/admin/events/1/feature', None),
    ('GET', '/admin/featured-events', None),
    ('GET', '/admin/disabled-events', None),
    
    # Finance
    ('GET', '/admin/finance/transactions', None),
    ('GET', '/admin/finance/payouts', None),
    ('PATCH', '/admin/finance/payouts/1/approve', None),
    ('PATCH', '/admin/finance/payouts/1/reject', {'reason': 'test'}),
    
    # Payout aliases
    ('GET', '/admin/payouts', None),
    ('POST', '/admin/payouts/1/approve', None),
    ('POST', '/admin/payouts/1/reject', {'reason': 'test'}),
    ('POST', '/admin/payouts/1/release', None),
    
    # Config
    ('GET', '/admin/config', None),
    ('PUT', '/admin/config/test_key', {'value': 'test'}),
    
    # Activity logs
    ('GET', '/admin/activity-logs', None),
    
    # Verifications
    ('GET', '/admin/verifications', None),
    ('POST', '/admin/verifications/1/approve', None),
    ('POST', '/admin/verifications/1/reject', {'reason': 'test'}),
    
    # Commission & flags
    ('GET', '/admin/commission-rates', None),
    ('GET', '/admin/commission-rates/freetown', None),
    ('PUT', '/admin/commission-rates/freetown', {'rate': 15.0}),
    ('GET', '/admin/system-flags', None),
    ('GET', '/admin/system-flags/maintenance', None),
    ('PUT', '/admin/system-flags/maintenance', {'enabled': True}),
    
    # Escrow
    ('GET', '/admin/escrow-stats', None),
    
    # Stubs
    ('GET', '/admin/activities', None),
    ('GET', '/admin/bookings', None),
    ('GET', '/admin/financials', None),
    ('GET', '/admin/transactions', None),
    ('GET', '/admin/pending-actions', None),
    ('GET', '/admin/roles', None),
    ('GET', '/admin/permissions', None),
    ('GET', '/admin/admins', None),
    ('GET', '/admin/settings/commissions', None),
    ('PUT', '/admin/settings/commissions', {'global_rate': 8.0}),
    ('GET', '/admin/settings/flags', None),
    ('PUT', '/admin/settings/flags', {'flags': []}),
    ('POST', '/admin/system/cache/reset', None),
    ('GET', '/admin/security/logs', None),
    ('GET', '/admin/security/stats', None),
    ('GET', '/admin/withdrawals', None),
    ('POST', '/admin/withdrawals/1/approve', None),
    ('POST', '/admin/users/invite', {'email': 'test@test.com'}),
    ('POST', '/admin/broadcast', {'message': 'test'}),
    ('POST', '/admin/payouts/1/process', None),
    ('GET', '/admin/events', None),
    ('GET', '/admin/events/1', None),
    
    # Enterprise (expected to all 404)
    ('GET', '/admin/enterprise/roles', None),
    ('GET', '/admin/enterprise/admins', None),
    ('GET', '/admin/enterprise/plans', None),
    ('GET', '/admin/enterprise/features', None),
    ('GET', '/admin/enterprise/withdrawals', None),
    ('GET', '/admin/enterprise/analytics/overview', None),
    ('GET', '/admin/enterprise/audit-logs', None),
    ('GET', '/admin/enterprise/support/tickets', None),
    ('GET', '/admin/enterprise/system/health', None),
    ('POST', '/admin/enterprise/init', None),
]

results = []
for method, path, body in endpoints:
    url = BASE + path
    try:
        if method == 'GET':
            resp = requests.get(url, headers=HEADERS, timeout=5)
        elif method == 'POST':
            resp = requests.post(url, json=body, headers=HEADERS, timeout=5)
        elif method == 'PUT':
            resp = requests.put(url, json=body, headers=HEADERS, timeout=5)
        elif method == 'PATCH':
            resp = requests.patch(url, json=body, headers=HEADERS, timeout=5)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=HEADERS, timeout=5)
        else:
            continue
        
        status = resp.status_code
        try:
            data = resp.json()
            preview = json.dumps(data)[:80]
        except:
            preview = resp.text[:80]
        
        results.append((method, path, status, preview))
    except Exception as e:
        results.append((method, path, 'ERROR', str(e)[:80]))

print("METHOD  PATH                                               STATUS   RESPONSE")
print("-" * 120)
for method, path, status, preview in results:
    if status == 200:
        icon = "PASS"
    elif status in [201, 202, 204]:
        icon = "OK  "
    elif status == 404:
        icon = "MISS"
    elif status == 422:
        icon = "VAL "
    elif status == 500:
        icon = "ERR "
    elif status == 403:
        icon = "FORB"
    elif status == 401:
        icon = "AUTH"
    else:
        icon = "WARN"
    print(f"{icon} {method:<6} {path:<50} {str(status):<8} {preview}")
