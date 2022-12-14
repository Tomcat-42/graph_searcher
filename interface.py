import random
import string

from tkinter import *
import time 

############funções
def nova_janela():
    n= int(ent_numero.get())
    janela.destroy()
    time.sleep(0.3)
    janela2= Tk()
    janela2.title("Grafo")
    janela2.geometry("490x560+400+153")
    vertice = ''.join(random.choices(string.ascii_letters+string.digits, k = n)) 
    connect = ''.join(random.choices(vertice, k = n))
    dados_grafo = list(zip(vertice,connect)) 
    termo = Label(janela2, text="Dados aleatorizados", background="#008",foreground="#fff",font=("X",15))
    termo.place(x=0,y=10,width=500,height=40)
    grafo_e = Label(janela2, text=dados_grafo, background="#008",foreground="#fff",font=("X",15))
    grafo_e.place(x=0,y=50,width=500,height=40)

def entrada_grafo():
    janela.destroy()
    time.sleep(0.3)
    janela3= Tk()
    janela3.title("Entrada")
    janela3.geometry("490x560+400+153")

    
#################################

janela = Tk()
janela.title("")
janela.geometry("500x300")
janela.configure(background='#FFFF7F')

#####################
numeros = Label(janela, text="Quantos elementos de vértices existem?", background="#008",foreground="#fff",font=("X",15))
numeros.place(x=0,y=10,width=500,height=40)

ent_numero = Entry(janela,justify='center',font=("X",15),width=100, 
                   highlightthickness=1,relief='solid')
ent_numero.place(x=1,y=60,width=500,height=40)

texto = Label(janela, text="Escolha a forma da inserção dos dados:", background="#008",foreground="#fff",font=("X",15))
texto.place(x=1,y=200,width=500,height=40)

botao1= Button(janela, text="Aleatório",command=nova_janela,font=("X",12))
botao1.place(x=150,y=250)

botao2= Button(janela, text="Arquivo",command=entrada_grafo,font=("X",12))
botao2.place(x=250,y=250)


janela.mainloop()
