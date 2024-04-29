from kivy.utils import get_color_from_hex as _hex


original={
    "base"                : "#666666",  #gray
    "primary"             : "#fadc2a",  #yellow
    "secondary"           : "#191919",  #dark_gray
    "accent"              : "#00a2ed",  #blue
    "highlight"           : "#f22c2c",  #light_red
    "complement"          : "#64ff64",  #green
    "neutral"             : "#cccccc",  #light_gray
    "additional"          : "#aa0000",  #red
    "dark_shade"          : "#000000",  #black
    "light_tint"          : "#ffffff",  #white
}


selected_palette=original

def palette(role:str,alpha:float=1.0):
    '''`returns` color of `role` from `selected_palette`'''
    if role in selected_palette:
        color=_hex(selected_palette[role])
        color[3]=alpha
        return (color)
    else:
        return(1,1,1,1)

