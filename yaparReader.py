import sys
import time
import pickle

import automatas.shuntingyard as shun
import automatas.dfa_directly as dfa_dir
import automatas.dfa_minimization as dfa_min
import simuladores.simuladorAFD as simAFD
import automatas.arbol as tree
import asciis.ascii_transformer_machines as ascii_machine
import asciis.ascii_transformer as ascii_reg


def main():

    archivo = "slrs/slr-1.yalp"
    Machines = {
        "Commentarios": "\"/*\" *(^*)*\"*/\"",
        "Declaration": "%token ",
        "Token": "['a'-'z''A'-'Z''𝜀']['a'-'z''A'-'Z''|'' ''_''0'-'9''𝜀']*",
        "Ignore": "IGNORE ",
        "Producciones": "%%",
        "Produccion": "['a'-'z''A'-'Z''0'-'9']+:",
        "Producto": "['a'-'z''A'-'Z''|''\n'' ''0'-'9''𝜀']+;",
    }

    start_time = time.time()

    terminales, diccionario, producciones, ignores = readYaparFile(Machines, archivo)

    tokenCheck(terminales)

    print("\n\nTokens: ", terminales)
    print("\n\nDiccionario: ", diccionario)

    producciones.insert(0,[producciones[0][0]+"'", [producciones[0][0]]])

    print("\n\nProducciones: ", producciones)

    noTerminales = []

    for produccion in producciones:
        if produccion[0] not in noTerminales:
            noTerminales.append(produccion[0])
    
    items = []
    items.extend(noTerminales)
    items.extend(terminales)

    produccionesCheck(items, producciones)

    print("Ignores: ", ignores)

    gramatica = {
        "terminales": terminales,
        "noTerminales": noTerminales,
        "producciones": producciones,
        "items": items,
        "ignores": ignores
    }

    with open('Grammar.pickle', 'wb') as f:
        pickle.dump(gramatica, f)

    end_time = time.time()

    time_taken = end_time - start_time

    print(f"Time taken by the operation is {time_taken} seconds")


def tokenCheck(tokens):
    DFAMin = {}

    with open("DFAMin.pickle", "rb") as f:
        DFAMin = pickle.load(f)

    for token in tokens:
        if token not in DFAMin["tokens"] and token != "𝜀":
            print("Error léxico, token no reconocido: ", token)
            sys.exit()


def produccionesCheck(items, producciones):
    for product in producciones:
        if product[0] not in items and product[0] != "𝜀":
            print("Error léxico, token no reconocido: ", product[0])
            sys.exit()
        for elem in product[1]:
            if elem not in items and elem != "𝜀":
                print("Error léxico, token no reconocido: ", elem)
                sys.exit()


def getYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def getMachine(regex, graph=False):
    ascii_regex = ascii_machine.ASCIITransformer(regex)
    postfix_regex = shun.exec(ascii_regex)
    print("Postfix: ", postfix_regex)
    print()
    stack, node_list, alfabeto = tree.exec(postfix_regex)
    estadoscon, alfabetocon, Dtran, estado_inicialcon, estado_finalcon = dfa_dir.exec(stack, node_list, alfabeto)
    estadosAFD = set()
    for i in estadoscon:
        estadosAFD.add(str(i))

    alfabetoAFD = set()
    for i in alfabetocon:
        alfabetoAFD.add(str(i))

    transicionesAFD = set()
    for tran in Dtran:
        trans = ()
        for t in tran:
            trans = trans + (str(t),)
        transicionesAFD.add(trans)

    estado_inicialAFD = {str(estado_inicialcon)}

    estados_aceptacionAFD = set()
    for i in estado_finalcon:
        estados_aceptacionAFD.add(str(i))

    new_states, symbol, new_transitions, newStart_states, newFinal_states = dfa_min.exec(estadosAFD, alfabetoAFD, transicionesAFD, estado_inicialAFD, estados_aceptacionAFD, graph=graph, check=False)
    return new_states, new_transitions, newStart_states, newFinal_states


def readYaparFile(Machines, archivo):
    ascii_comments = Machines['Commentarios']
    print("Generando AFD para comentarios")
    _, comments_transitions, comments_inicial, comments_final = getMachine(ascii_comments)
    print("AFD para comentarios generado")

    ascii_declaration = Machines['Declaration']
    print("Generando AFD para declaration")
    _, declaration_transitions, declaration_inicial, declaration_final = getMachine(ascii_declaration)
    print("AFD para declaration generado")

    ascii_token = Machines['Token']
    print("Generando AFD para tokens")
    _, token_transitions, token_inicial, token_final = getMachine(ascii_token)
    print("AFD para tokens generado")

    ascii_ignore = Machines['Ignore']
    print("Generando AFD para ignore")
    _, ignore_transitions, ignore_inicial, ignore_final = getMachine(ascii_ignore)
    print("AFD para ignore generado")

    ascii_producciones = Machines['Producciones']
    print("Generando AFD para producciones")
    _, producciones_transitions, producciones_inicial, producciones_final = getMachine(ascii_producciones)
    print("AFD para producciones generado")

    ascii_produccion = Machines['Produccion']
    print("Generando AFD para produccion")
    _, produccion_transitions, produccion_inicial, produccion_final = getMachine(ascii_produccion)
    print("AFD para produccion generado")

    ascii_producto = Machines['Producto']
    print("Generando AFD para producto")
    _, producto_transitions, producto_inicial, producto_final = getMachine(ascii_producto)
    print("AFD para producto generado")
    print("\n\n")

    data = getYalexFile(archivo)

    i = 0
    diccionario = {}
    terminales = []
    producciones_temp = []
    producciones = []
    ignores = []
    contador = 0
    length_data = len(data)
    read_tokens = True
    
    while i < length_data:
        bol, num, valores = simAFD.exec(comments_transitions, comments_inicial, comments_final, data, i)
        if bol:
            print("Comentario: " + valores)
            diccionario[contador] = valores
            contador += 1
            i = num
            continue

        if read_tokens:

            bol, num, valores = simAFD.exec(producciones_transitions, producciones_inicial, producciones_final, data, i)
            if bol:
                print("Producciones: " + valores)
                diccionario[contador] = valores
                read_tokens = False
                contador += 1
                i = num
                continue

            bol, num, valores = simAFD.exec(ignore_transitions, ignore_inicial, ignore_final, data, i)
            if bol:
                print("Ignore: " + valores)
                diccionario[contador] = valores
                contador += 1
                i = num

                while True:
                    bol, num, valores = simAFD.exec(token_transitions, token_inicial, token_final, data, i)
                    if bol:
                        print("Token/s: " + valores)
                        diccionario[contador] = valores
                        ignores.append(valores)
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Error lexico en la linea: ", data[i])
                        sys.exit()
                continue


            bol, num, valores = simAFD.exec(declaration_transitions, declaration_inicial, declaration_final, data, i)
            if bol:
                print("Declaracion token: " + valores)
                diccionario[contador] = valores
                contador += 1
                i = num

                while True:
                    bol, num, valores = simAFD.exec(token_transitions, token_inicial, token_final, data, i)
                    if bol:
                        print("Token/s: " + valores)
                        diccionario[contador] = valores
                        listValues = valores.split()
                        for item in listValues:
                            terminales.append(item)
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Error lexico en la linea: ",'i'+data[i]+'i')
                        sys.exit()
                continue

        
        if read_tokens == False:
            bol, num, valores = simAFD.exec(produccion_transitions, produccion_inicial, produccion_final, data, i)
            if bol:
                print("Produccion: " + valores)
                diccionario[contador] = valores
                producciones_temp.append(valores[:-1])
                contador += 1
                i = num

                while True:
                    bol, num, valores = simAFD.exec(producto_transitions, producto_inicial, producto_final, data, i)
                    if bol:
                        print("Producto: " + valores)
                        diccionario[contador] = valores
                        pro = producciones_temp.pop()
                        listValues = valores.split("|")
                        for item in listValues:
                            item = item.replace("\n", "")
                            item = item.strip()
                            if len(item) < 1:
                                continue
                            if item[-1] == ";":
                                item = item[:-1]
                            
                            item = item.split()
                            producciones.append([pro, item])
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        print("Error lexico en la linea: ", data[i])
                        sys.exit()
                continue

        if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
            i += 1
            continue

        else:
            print("Error lexico en la linea: ", data[i])
            sys.exit()

    if terminales == []:
        print("Error léxico, no se encontraron tokens")
        sys.exit()

    return terminales, diccionario, producciones, ignores


main()
