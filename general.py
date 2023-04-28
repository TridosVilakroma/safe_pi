import os
def Convert_time(n):
    day = int(n // (24 * 3600))
    n = n % (24 * 3600)
    hour = int(n // 3600)
    n %= 3600
    minutes = int(n // 60)
    m_plural="s" if minutes>1 else""
    m=f"{minutes} Minute{m_plural}" if minutes else ""
    delimiter_2="   ||   " if minutes and hour or minutes and day else ""
    h_plural="s" if hour>1 else""
    h=f"{hour} Hour{h_plural}" if hour else ""
    delimiter_1="   ||   " if hour and day else ""
    d_plural="s" if day>1 else""
    d=f"{day} Day{d_plural}" if day else ""
    product=f"{d}{delimiter_1}{h}{delimiter_2}{m}" if day or hour or minutes else "Run time less than a minute"
    return product

def file_or_dir(path):
    if os.path.isdir(path):
        return 'folder'
    if os.path.isfile(path):
        return 'file'
    return ''

def pin_decode(pin_number):
    index={8:14,10:15,11:17,12:18,
           13:27,15:22,16:23,18:24,
           19:10,21:9,22:25,23:11,
           32:12,33:13,35:19,36:16,
           37:26,38:20,40:21}
    return f'Board: {int(pin_number)} <> BCM: {int(index[pin_number])}'