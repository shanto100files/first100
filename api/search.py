from aiohttp import web
from database.ia_filterdb import col, sec_col
import re
import logging

logger = logging.getLogger(__name__)

async def search_files(query):
    files = []
    
    # Clean and prepare search query
    clean_query = re.sub(r'[^\w\s]', '', query.lower())
    words = clean_query.split()
    
    # Build search pattern
    pattern = '.*'.join(map(re.escape, words))
    regex = re.compile(pattern, re.IGNORECASE)

    # Search in first database
    try:
        cursor1 = col.find({
            'file_name': {'$regex': pattern, '$options': 'i'}
        })
        async for file in cursor1:
            files.append({
                'file_id': str(file['_id']),
                'file_name': file['file_name'],
                'file_size': file.get('file_size', 0),
                'mime_type': file.get('mime_type', 'application/octet-stream')
            })
    except Exception as e:
        logger.error(f"Error searching first database: {str(e)}")

    # Search in second database
    try:
        cursor2 = sec_col.find({
            'file_name': {'$regex': pattern, '$options': 'i'}
        })
        async for file in cursor2:
            files.append({
                'file_id': str(file['_id']),
                'file_name': file['file_name'],
                'file_size': file.get('file_size', 0),
                'mime_type': file.get('mime_type', 'application/octet-stream')
            })
    except Exception as e:
        logger.error(f"Error searching second database: {str(e)}")

    # Sort results by relevance
    files.sort(key=lambda x: len(re.findall(pattern, x['file_name'].lower())))
    
    return files

async def handle_search(request):
    try:
        query = request.query.get('q', '').strip()
        
        if not query:
            return web.json_response({
                'files': [],
                'total': 0
            })

        files = await search_files(query)
        
        # Make sure each file has the required fields
        formatted_files = [{
            'file_id': str(file.get('file_id', '')),
            'file_name': str(file.get('file_name', '')),
            'file_size': int(file.get('file_size', 0))
        } for file in files]
        
        return web.json_response({
            'files': formatted_files,
            'total': len(formatted_files)
        })

    except Exception as e:
        logger.error(f"Search handler error: {str(e)}")
        return web.json_response({
            'error': 'Search failed',
            'message': str(e)
        }, status=500)

# Add to your routes
app.router.add_get('/api/search', handle_search)
