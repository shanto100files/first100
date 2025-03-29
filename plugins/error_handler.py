import logging
from datetime import datetime
from info import LOG_CHANNEL

async def log_error(client, error_message, error_type="ERROR"):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_msg = f"""
🚫 **নতুন এরর রিপোর্ট**
⏰ Time: {current_time}
📝 Type: {error_type}

```
{error_message}
```
        """
        
        if LOG_CHANNEL:
            await client.send_message(LOG_CHANNEL, log_msg)
            
        # লোকাল লগ ফাইলে সেভ
        logging.error(f"{error_type}: {error_message}")
        
    except Exception as e:
        logging.error(f"এরর লগিং ফেইল: {str(e)}")