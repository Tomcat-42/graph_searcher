from random import *
import string
from tkinter import *
import time 
# para o grafo_plot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

############funções
def nova_janela():
    janela.destroy()
    time.sleep(0.3)
    janela2= Tk()
    janela2.title("Grafo")
    janela2.geometry("490x700+500+153")
    janela2.configure(background='#FFFF7F')
    n= randint(7,20)
    vertice = ''.join(choices(string.ascii_letters+string.digits, k = n)) 
    connect = ''.join(choices(vertice, k = n))
    dados_grafo = list(zip(vertice,connect)) 
    termo = Label(janela2, text="Dados aleatorizados", background="#008",foreground="#fff",font=("X",15))
    termo.place(x=0,y=10,width=700,height=40)
    grafo_e = Label(janela2, text=dados_grafo, background="#008",foreground="#fff",font=("X",15))
    grafo_e.place(x=0,y=50,width=700,height=40)
    #################################################
    ######### criando espaço para gráfico
    figura= plt.Figure(figsize=(8,4),dpi=60)
    ax=figura.add_subplot(111)
    canva = FigureCanvasTkAgg(figura, janela2)
    canva.get_tk_widget().place(x=0,y=100,width=500,height=200)
    
    # make the data
    np.random.seed(3)
    x = 4 + np.random.normal(0, 2, 24)
    y = 4 + np.random.normal(0, 2, len(x))
    # size and color:
    sizes = np.random.uniform(15, 80, len(x))
    colors = np.random.uniform(15, 80, len(x))

    ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100)

    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
        ylim=(0, 8), yticks=np.arange(1, 8))
    ###############################################
    ###############################################
    texto1 = Label(janela2, text="Estado inicial:", background="#008",foreground="#fff",font=("X",15))
    texto1.place(x=1,y=350,width=200,height=40)
    inicio = Entry(janela2,justify='center',font=("X",15),width=100, 
                   highlightthickness=1,relief='solid')
    inicio.place(x=201,y=350,width=100,height=40)
    
    texto2 = Label(janela2, text="Estado final:  ", background="#008",foreground="#fff",font=("X",15))
    texto2.place(x=1,y=400,width=200,height=40)
    fim = Entry(janela2,justify='center',font=("X",15),width=100, 
                   highlightthickness=1,relief='solid')
    fim.place(x=201,y=400,width=100,height=40)
    
    botaoM= Button(janela2, text="Busca em largura",command=nova_janela,font=("X",15))
    botaoM.place(x=50,y=450)

    botaoB= Button(janela2, text="Busca com limite superior",command=entrada_grafo,font=("X",15))
    botaoB.place(x=230,y=450)


def entrada_grafo():
    janela.destroy()
    time.sleep(0.3)
    janela3= Tk()
    janela3.title("Entrada")
    janela3.geometry("490x560+400+153")
    janela3.configure(background='#FFFF7F')

    
#################################

janela = Tk()
janela.title("")
janela.geometry("500x300")
janela.configure(background='#FFFF7F')

#####################

texto = Label(janela, text="Escolha a forma da inserção dos dados:", background="#008",foreground="#fff",font=("X",15))
texto.place(x=1,y=100,width=500,height=40)

botao1= Button(janela, text="Aleatório",command=nova_janela,font=("X",12))
botao1.place(x=150,y=150)

botao2= Button(janela, text="Arquivo",command=entrada_grafo,font=("X",12))
botao2.place(x=250,y=150)


janela.mainloop()
