#! /usr/bin/python
from gimpfu import *
import os
def rotacao_em_massa (diretorio):
    for arquivo in os.listdir (diretorio):
        nome = os.path.join (diretorio, arquivo)
        imagem = pdb.gimp_file_load (nome, nome)
        pdb.gimp_image_rotate (imagem, ROTATE_270)
        tmp = arquivo.split(".")
        novo_nome = os.path.join (diretorio, tmp[0] + "R" + tmp[1])
        pdb.gimp_file_sabe (imagem, imagem.layers[0], 
		            novo_nome, novo_nome)
register(
        "rotacao_em_massa",
        "Rotaciona as imagens em um diretório",
        "rotacao_em_massa (diretorio) -> None",
        "Joao S. O. Bueno Calligaris",
        "(k) All rites reversed - reuse whatever you like- JS",
        "2005",
        "<Xtns>/Python-Fu/Rotacionar em Massa",
        "*",
        [(PF_FILE, "diretorio", "diretorio a transformar",""),
        ],
        [],
        rotacao_em_massa)
main()
