class Mail:
    def __init__(self):
        self.id = 0
        self.group = None
        self.subject = ""
        self.text = ""


def loadFile(filename):
    mail = Mail()
    f = open(filename, 'r')
    for line in f:
 #parse = line.split(':',2) => verifier syntaxe
 #ca va retourner un tableau 
 #uutiliser un bool pour savoir si on est tjs danns le header
 #checker la partie gauche retournée par le split pour voir si c un de ceux qui nous itéressent
 #si on arrive à une ligne vide : on a fini le header, la suite c du texte
