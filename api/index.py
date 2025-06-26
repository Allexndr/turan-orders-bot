import json
import os

def handler(request):
    """Vercel handler for Telegram webhook"""
    
    # Получаем данные
    method = getattr(request, 'method', 'GET')
    
    if method == 'GET':
        return json.dumps({
            "status": "active",
            "message": "Telegram webhook endpoint"
        })
    
    if method == 'POST':
        try:
            # Получаем body
            body = getattr(request, 'data', {})
            if hasattr(request, 'get_json'):
                body = request.get_json() or {}
            
            return json.dumps({
                "status": "received",
                "method": method
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    return json.dumps({"error": "Method not allowed"}) 