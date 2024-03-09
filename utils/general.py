import os,re,logging

logger=logging.getLogger('logger')

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
    '''return str representation of pin.

    str will have both board and bcm modes'''

    pin_number=int(pin_number)

    index={8:14,10:15,11:17,12:18,
           13:27,15:22,16:23,18:24,
           19:10,21:9,22:25,23:11,
           32:12,33:13,35:19,36:16,
           37:26,38:20,40:21,
           #advanced pins below
           3:2,5:3,7:4,24:8,26:7,
           27:0,28:1,29:5,31:6}

    if pin_number in index:
         bcm_conversion=index[pin_number]
    else:bcm_conversion=pin_number

    return f'Board: {pin_number} <> BCM: {bcm_conversion}'

def pin_translate(pin_number):
    '''return board numbering from bcm numbered pin'''

    pin_number=int(pin_number)

    index={ 9:21,10:19,11:23,12:32,
           13:33,14:8 ,15:10,16:36,
           17:11,18:12,19:35,20:38,
           21:40,22:15,23:16,24:18,
           25:22,26:37,27:13,
           #advanced pins below
            0:27, 1:28, 2:3 , 3:5 ,4:7,
            5:29, 6:31, 7:26, 8:24}

    if pin_number in index:
        return index[pin_number]
    else:
        logger.debug(f'Could not translate {pin_number}')
        return 0

def stripargs(func,*args,**kwargs):
    '''Strips `*args` and `**kwargs`

    For use when a function is used as a callback
    that does not accept any arguments.
    Wrap `stripargs` in `partial` with `func` as
    the argument'''
    return func()

def strip_markup(text):
        '''Return text with all the markup split::

            >>> text='[b]Hello world[/b]'
            >>> returns ('[b]', 'Hello world', '[/b]')

        '''
        s = re.split(r'(\[.*?\])', text)
        s = [x for x in s if x != '']
        s = ''.join([x for x in s if '[' not in x])
        return s

def pad_str(_string,_length):
    '''returns _string with padding
    
    texture size is not uniform for all chars,
    white space being the big offender at roughly
    half the  width once a texture is created.
    `pad_str` calculates necessary white space
    to fill in the same visual width of missing chars.
    '''
    padding=_length-len(_string)
    return _string+' '*int(padding*2)

def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, 'rb') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            # remove file's last "\n" if it exists, only for the first buffer
            if remaining_size == file_size and buffer[-1] == ord('\n'):
                buffer = buffer[:-1]
            remaining_size -= buf_size
            lines = buffer.split('\n'.encode())
            # append last chunk's segment to this chunk's last line
            if segment is not None:
                lines[-1] += segment
            segment = lines[0]
            lines = lines[1:]
            # yield lines in this chunk except the segment
            for line in reversed(lines):
                # only decode on a parsed line, to avoid utf-8 decode error
                yield line.decode()
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment.decode()
