import math
import time

async def progress_bar(current, total, status_msg, message, start):
    if not total:
        return
    if current >= total:
        return
    now = time.time()
    diff = now - start
    if diff < 1:
        return
    
    speed = current / diff
    percentage = current * 100 / total
    time_to_completion = round((total - current) / speed)
    
    progress = "[{0}{1}]".format(
        ''.join(["●" for _ in range(math.floor(percentage / 5))]),
        ''.join(["○" for _ in range(20 - math.floor(percentage / 5))])
    )
    
    current_message = f"""
{status_msg}
{progress} {percentage:.1f}%

⚡️ Speed: {humanbytes(speed)}/s
📊 Progress: {humanbytes(current)} / {humanbytes(total)}
⏱ Time Left: {TimeFormatter(time_to_completion)}"""
    
    try:
        await message.edit(current_message)
    except:
        pass

def TimeFormatter(seconds: float) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return ((str(days) + "d, ") if days else "") + \
           ((str(hours) + "h, ") if hours else "") + \
           ((str(minutes) + "m, ") if minutes else "") + \
           ((str(seconds) + "s") if seconds else "")
