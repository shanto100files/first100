import asyncio
from datetime import datetime, time
from info import ADMINS

async def auto_restart():
    while True:
        now = datetime.now().time()
        # রাত 3টায় রিস্টার্ট
        restart_time = time(3, 0)  
        
        if now.hour == restart_time.hour and now.minute == restart_time.minute:
            restart_msg = "🔄 সিস্টেম অটো রিস্টার্ট হচ্ছে..."
            
            # এডমিনদের নোটিফাই
            for admin in ADMINS:
                try:
                    await Client.send_message(admin, restart_msg)
                except:
                    pass
                    
            # রিস্টার্ট প্রসেস
            os.execl(sys.executable, sys.executable, *sys.argv)
            
        await asyncio.sleep(60)