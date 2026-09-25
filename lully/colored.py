import colorama

def colored(txt: str, fore: str = '', back: str = '', style: str = '') -> str:
    fore = fore and getattr(colorama.Fore, fore.upper())
    back = back and getattr(colorama.Back, back.upper())
    style = style and getattr(colorama.Style, style.upper())
    return fore+back+style + txt + colorama.Style.RESET_ALL
