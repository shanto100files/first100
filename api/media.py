import logging
from aiohttp import web
from database.ia_filterdb import col, sec_col
from bson.errors import InvalidId

logger = logging.getLogger(__name__)

@routes.get('/health')
async def health_check(request):
    try:
        # ডাটাবেস কানেকশন চেক
        await col.find_one({})
        await sec_col.find_one({})
        
        return web.json_response({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return web.json_response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

@routes.get('/files')
async def get_all_files(request):
    try:
        files = []
        
        # First database
        try:
            cursor1 = col.find({})
            async for file in cursor1:
                try:
                    files.append({
                        'file_id': str(file.get('_id', '')),
                        'file_name': file.get('file_name', 'Untitled'),
                        'file_size': file.get('file_size', 0),
                        'mime_type': file.get('mime_type', 'application/octet-stream')
                    })
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error accessing first database: {str(e)}")

        # Second database            
        try:
            cursor2 = sec_col.find({})
            async for file in cursor2:
                try:
                    files.append({
                        'file_id': str(file.get('_id', '')),
                        'file_name': file.get('file_name', 'Untitled'),
                        'file_size': file.get('file_size', 0),
                        'mime_type': file.get('mime_type', 'application/octet-stream')
                    })
                except Exception as e:
                    logger.error(f"Error processing file: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error accessing second database: {str(e)}")

        if not files:
            return web.json_response({
                'files': [],
                'message': 'No files found'
            })

        return web.json_response({
            'files': files,
            'total': len(files)
        })
        
    except Exception as e:
        logger.error(f"Global error in get_all_files: {str(e)}")
        return web.json_response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)


