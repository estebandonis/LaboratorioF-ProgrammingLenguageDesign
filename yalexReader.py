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


symbol_dict = {
    "!": "exclamation_mark",
    "@": "at_sign",
    "#": "hash",
    "$": "dollar",
    "%": "percent",
    "^": "caret",
    "&": "ampersand",
    "*": "asterisk",
    "(": "open_parenthesis",
    ")": "close_parenthesis",
    "-": "minus",
    "_": "underscore",
    "=": "equals",
    "+": "plus",
    "[": "open_bracket",
    "]": "close_bracket",
    "{": "open_brace",
    "}": "close_brace",
    ";": "semicolon",
    ":": "colon",
    ",": "comma",
    ".": "dot",
    "<": "less_than",
    ">": "greater_than",
    "/": "slash",
    "?": "question_mark",
    "|": "vertical_bar",
    "\\": "backslash",
    "`": "grave_accent",
    "~": "tilde",
    "\"": "double_quote",
    "'": "single_quote"
}


def main():

    archivo = "slrs/slr-1.yal"
    Machines = {
        "Commentarios": "\"(*\" *[' '-'&''+'-'}''á''é''í''ó''ú''ñ''\n''\t']* *\"*)\"",
        "Header": "{ *(^})*}",
        "Declaration": "let +['a'-'z''_']* +=",
        "Variables": "('['(^])*]|^[ \n]*)+",
        "Reglas": "rule *tokens *=",
        "Tokens1": "['&'-'}']+",
        "Tokens2": "'|' *['\"'-'}']*",
        "Returns": "{ *(^})*}",
        "Trailer": "{ *(_)*",
    }

    start_time = time.time()

    values, tokens, tokens_dictionary, diccionario = readYalexFile(Machines, archivo)

    print("\nValues: ", values)
    print("\nTokens: ", tokens)
    print("\ntoken Diccionario: ")
    for dic in tokens_dictionary:
        print(dic, ": ", tokens_dictionary[dic])

    toekns = tokens_dictionary.copy()

    values = setValues(values)

    print("\nValues Final: ")
    for lal in values:
        print(lal, ": ", values[lal])


    print("\nCreando archivo .py")

    imports = """
import pickle
import time

import simuladores.simuladorScanner as simSCAN

"""

    scanner = """
def readYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def getGrammar():
    Grammar = {}
    with open("Grammar.pickle", "rb") as f:
        Grammar = pickle.load(f)
    return Grammar


def main():
    archivo = "string.txt"

    # Leer .txt
    data = readYalexFile(archivo)

    DFAMin = {}
    # Load the data
    with open("DFAMin.pickle", "rb") as f:
        DFAMin = pickle.load(f)

    grammar = getGrammar()
        
    start_time = time.time()

    tokens = readString(data, DFAMin, grammar)

    grammar["tokens"] = tokens

    with open("Grammar.pickle", "wb") as f:
        pickle.dump(grammar, f)

    end_time = time.time()

    time_taken = end_time - start_time

    print(f"\\nTime taken by the operation is {time_taken} seconds")


def readString(data, DFAMin, grammar):
    i = 0
    contador = 0
    tokens = []

    lengthData = len(data)

    while i < lengthData:
        print("\\ni: " + str(i))
        num, valores, temp, error = simSCAN.exec(DFAMin["transitions"], DFAMin["start_states"], DFAMin["returns"], data, i)
        if error:
            print(f"Valor no reconocido: '{temp}'")
            i += 1
            print("m: " + str(i))
            continue
        token = ""
        for key in DFAMin["new_returns"]:
            if valores in DFAMin["new_returns"][key]:
                token = key
                break
                
        if len(grammar["ignores"]) == 1 and token != grammar["ignores"][0]:
            tokens.append(token)
        elif len(grammar["ignores"]) > 1 and token not in grammar["ignores"]:
            tokens.append(token)

        print("m: " + str(num))
        print("Valor: " + temp)
        print("Token: " + token)
        print("Command: " + valores)
        print("Ejecución: ")
        try:
            exec(valores)
        except:
            print("Error al momento de ejecutar el comando")
        contador += 1
        i = num
        continue
    
    print(tokens)
        
    return tokens

if __name__ == "__main__":
    main()

"""

    with open('scan.py', 'w') as f:
        f.write(imports)
        if 'Header' in diccionario:
            f.write(diccionario['Header'][1:-1])
        for value in tokens_dictionary:
            write_value, function = defString(value, tokens_dictionary[value][2:-2])
            tokens_dictionary[value] = f"{{ {function} }}"
            f.write(write_value)

        f.write(scanner)
        if 'Trailer' in diccionario:
            f.write(diccionario['Trailer'][1:-1])

    print("Archivo .py creado\n")

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in values:
            tokens[i] = values[tokens[i]]
        if tok in tokens_dictionary:
                tokens[i] += tokens_dictionary[tok]
        i += 1

    super_string = ''.join(str(i) for i in tokens)

    ascii_super = ascii_reg.ASCIITransformer(super_string)

    for tok in tokens_dictionary:
        print(tok, ": ", tokens_dictionary[tok])    

    super_postfix = shun.exec(ascii_super)
    stack, node_list, alfabeto = tree.exec(super_postfix)

    print("\nCreando DFA Directo")

    estadoscon, alfabetocon, Dtran, estado_inicialcon, estado_finalcon = dfa_dir.exec(stack, node_list, alfabeto)

    print("DFA Directo terminado\n")

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

    print("Creando DFA Minimizacion")

    new_states, symbols, new_transitions, newStart_states, newFinal_states = dfa_min.exec(estadosAFD, alfabetoAFD, transicionesAFD, estado_inicialAFD, estados_aceptacionAFD, False, True)

    print("DFA Minimizado terminado\n")

    tempdiccionario = tokens_dictionary.copy()
    for ret in tempdiccionario:
        if ret[0] == '"' and ret[-1] == '"':
            new_string = ret.replace('"', '')
            tokens_dictionary[new_string] = tokens_dictionary.pop(ret)[2:-2]
        else:
            tokens_dictionary.pop(ret)

    DFAMin = {
        "states": new_states,
        "transitions": new_transitions,
        "symbols": symbols,
        "start_states": newStart_states,
        "final_states": newFinal_states,
        "returns": tokens_dictionary,
        "new_returns": tempdiccionario,
        "tokens": toekns
    }

    with open('DFAMin.pickle', 'wb') as f:
        pickle.dump(DFAMin, f)

    print("DFA Minimizado guardado en DFAMin.pickle\n")

    end_time = time.time()

    time_taken = end_time - start_time

    print(f"Time taken by the operation is {time_taken} seconds")


def defString(name, valor):
    name = name.replace('"', '')
    name = name.replace('\'', '')
    if len(name) == 1:
        if name in symbol_dict:
            name = symbol_dict[name]
            return f"\ndef {name}():\n\t{valor}\n", f"{name}()"
        return f"\ndef n{ord(name)}():\n\t{valor}\n", f"n{ord(name)}()"

    return f"\ndef {name.upper()}():\n\t{valor}\n", f"{name.upper()}()"



def getYalexFile(file):
    with open(file, 'r') as file:
        data = file.read()
    return data


def getMachine(regex, graph=False):
    ascii_regex = ascii_machine.ASCIITransformer(regex)
    postfix_regex = shun.exec(ascii_regex)
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

    new_states, symbols, new_transitions, newStart_states, newFinal_states = dfa_min.exec(estadosAFD, alfabetoAFD, transicionesAFD, estado_inicialAFD, estados_aceptacionAFD, graph=graph, check=False)
    return new_states, new_transitions, newStart_states, newFinal_states


def setValues(values):
    for val in values:
        valor = values[val]

        if 'let ' in valor:
            print("Error léxico, no se cerro el corchete ", valor.split()[0])
            sys.exit()

        for valo in reversed(values):
            first = valor.find(valo)
            last = 0
            if first != -1:
                last = first + len(valo)

            if first != -1:
                if first - 1 >= 0 and valor[first - 1] == '\'' and last < len(valor) and valor[last] == '\'':
                    continue
                new_string = valor[:first] + values[valo] + valor[last:]
                valor = new_string
                values[val] = new_string

            while first != -1:

                first = valor.find(valo)
                if first != -1:
                    last = first + len(valo)

                if first != -1:
                    if first - 1 >= 0 and valor[first - 1] == '\'' and last < len(valor) and valor[last] == '\'':
                        continue
                    new_string = valor[:first] + values[valo] + valor[last:]
                    valor = new_string
                    values[val] = new_string
    
    return values


def readYalexFile(Machines, archivo):
    ascii_comments = Machines['Commentarios']
    print("Generando AFD para comentarios")
    comments_states, comments_transitions, comments_inicial, comments_final = getMachine(ascii_comments)
    print("AFD para comentarios generado")

    ascii_headers = Machines['Header']
    print("Generando AFD para header")
    headers_states, headers_transitions, headers_inicial, headers_final = getMachine(ascii_headers)
    print("AFD para comentarios generado")

    ascii_declaration = Machines['Declaration']
    print("Generando AFD para declaration")
    declaration_states, declaration_transitions, declaration_inicial, declaration_final = getMachine(ascii_declaration)
    print("AFD para declaration generado")

    ascii_variables = Machines['Variables']
    print("Generando AFD para variables")
    variables_states, variables_transitions, variables_inicial, variables_final = getMachine(ascii_variables)
    print("AFD para variables generado")

    ascii_rules = Machines['Reglas']
    print("Generando AFD para reglas")
    rules_states, rules_transitions, rules_inicial, rules_final = getMachine(ascii_rules)
    print("AFD para reglas generado")

    ascii_tokens1 = Machines['Tokens1']
    print("Generando AFD para tokens1")
    tokens1_states, tokens1_transitions, tokens1_inicial, tokens1_final = getMachine(ascii_tokens1)
    print("AFD para tokens1 generado")

    ascii_tokens2 = Machines['Tokens2']
    print("Generando AFD para tokens2")
    tokens2_states, tokens2_transitions, tokens2_inicial, tokens2_final = getMachine(ascii_tokens2)
    print("AFD para tokens2 generado")

    ascii_returns = Machines['Returns']
    print("Generando AFD para returns")
    returns_states, returns_transitions, returns_inicial, returns_final = getMachine(ascii_returns)
    print("AFD para returns generado")

    ascii_trailer = Machines['Trailer']
    print("Generando AFD para trailer")
    trailer_states, trailer_transitions, trailer_inicial, trailer_final = getMachine(ascii_trailer)
    print("AFD para returns generado\n\n")

    data = getYalexFile(archivo)

    i = 0
    diccionario = {}
    variables = []
    values = {}
    tokens = []
    temp_tokens = []
    tokens_dictionary = {}
    contador = 0
    length_data = len(data)
    read_tokens = False
    header_bool = False
    token1_bool = False
    numToken = 1
    
    while i < length_data:
        bol, num, valores = simAFD.exec(comments_transitions, comments_inicial, comments_final, data, i)
        if bol:
            print("Comentario: " + valores)
            diccionario[contador] = valores
            contador += 1
            i = num
            continue

        if header_bool == False:
            bol, num, valores = simAFD.exec(headers_transitions, headers_inicial, headers_final, data, i)
            if bol and header_bool == False:
                print("Header: " + valores)
                diccionario['Header'] = valores
                contador += 1
                i = num
                header_bool = True

                if "let " in valores:
                    print("Error léxico, no se cerro la llave en el header")
                    sys.exit()
                continue

        bol, num, valores = simAFD.exec(rules_transitions, rules_inicial, rules_final, data, i)
        if bol:
            print("Rules: " + valores)
            diccionario[contador] = valores
            contador += 1
            read_tokens = True
            i = num
            if variables != []:
                print("Error léxico, existe un id sin definición")
                print(variables)
                print(values)
                sys.exit()
            continue

        if read_tokens == False:
            bol, num, valores = simAFD.exec(declaration_transitions, declaration_inicial, declaration_final, data, i)
            if bol:
                print("Declaration: " + valores)
                diccionario[contador] = valores
                listValues = valores.split()
                variables.append(listValues[1])
                contador += 1
                i = num
                continue

            bol, num, valores = simAFD.exec(variables_transitions, variables_inicial, variables_final, data, i)
            if bol:
                print("Variables: " + valores)
                diccionario[contador] = valores
                if variables != [] and len(variables) < 2:
                    values[variables.pop()] = valores
                else:
                    print("Error léxico, existe un id sin definición")
                    print("valores: ", valores)
                    print(variables)
                    print(values)
                    sys.exit()
                contador += 1
                i = num
                continue
        
        bol, num, valores = simAFD.exec(trailer_transitions, trailer_inicial, trailer_final, data, i)
        if bol:
            print("Trailer: " + valores)
            diccionario['Trailer'] = valores
            contador += 1
            i = num

            if '}' not in valores[-3:]:
                print("Error léxico, no se cerro la llave en el trailer")
                sys.exit()

            continue

        if read_tokens:

            bol, num, valores = simAFD.exec(tokens2_transitions, tokens2_inicial, tokens2_final, data, i)
            if bol:
                print("Token: " + valores)
                diccionario[contador] = valores
                listValues = valores.split()

                if listValues[1] in values:
                    newToken = listValues[1]
                else:
                    newToken = 'TOKON'+str(numToken)
                    values[newToken] = listValues[1]
                    numToken += 1
                print("ListValues: ", listValues)
                if tokens == []:
                    tokens.append(newToken)
                else:
                    tokens.append(listValues[0])
                    tokens.append(newToken)
                temp_tokens.append(newToken)
                contador += 1
                i = num

                while True:
                    bol, num, valores = simAFD.exec(returns_transitions, returns_inicial, returns_final, data, i)
                    if bol:
                        print("Return: " + valores)
                        diccionario[contador] = valores
                        if temp_tokens != []:
                            tokens_dictionary[temp_tokens.pop()] = valores
                        else:
                            print("Error léxico, no existe un token para el siguiente return")
                            sys.exit()
                        contador += 1
                        i = num
                        break

                    if data[i] == ' ' or data[i] == '\t':
                        i += 1
                        continue

                    else:
                        break
                continue

            if token1_bool == False:
                bol, num, valores = simAFD.exec(tokens1_transitions, tokens1_inicial, tokens1_final, data, i)
                if bol:
                    print("Token: " + valores)
                    diccionario[contador] = valores
                    print("Valores: ", valores)

                    if valores in values:
                        newToken = valores
                    else:
                        newToken = 'TOKON'+str(numToken)
                        values[newToken] = valores
                        numToken += 1
                    
                    tokens.append(newToken)
                    temp_tokens.append(newToken)
                    contador += 1
                    i = num
                    token1_bool = True
                    
                    while True:
                        bol, num, valores = simAFD.exec(returns_transitions, returns_inicial, returns_final, data, i)
                        if bol:
                            print("Return: " + valores)
                            diccionario[contador] = valores
                            if temp_tokens != []:
                                tokens_dictionary[temp_tokens.pop()] = valores
                            else:
                                print("Error léxico, no existe un token para el siguiente return")
                                sys.exit()
                            contador += 1
                            i = num
                            break

                        if data[i] == ' ' or data[i] == '\t':
                            i += 1
                            continue

                        else:
                            break
                    continue

        if data[i] == ' ' or data[i] == '\n' or data[i] == '\t':
            i += 1
            continue

        else:
            print("Error lexico en la linea: ", data[i])
            sys.exit()

    if tokens == []:
        print("Error léxico, no se encontraron tokens")
        sys.exit()

    if temp_tokens != []:
        for tok in temp_tokens:
            tokens_dictionary[tok] = "{ print() }"
    

    return values, tokens, tokens_dictionary, diccionario


main()
