
def quot(s):
    return "'"+s+"'" if "'" not in s else '"'+s+'"'

def arg_convert(s):
    return s.replace('$1', "'+arg[0][0]+'").replace('$2', "'+arg[1][0]+'").replace('$3', "'+arg[2][0]+'")
