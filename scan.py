
import pickle
import time

import simuladores.simuladorScanner as simSCAN


print("header")

def WS():
	WS

def ID():
	ID

def TOKON1():
	print()

def TOKON2():
	print()

def TOKON3():
	print()

def TOKON4():
	print()

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

    print(f"\nTime taken by the operation is {time_taken} seconds")


def readString(data, DFAMin, grammar):
    i = 0
    contador = 0
    tokens = []

    lengthData = len(data)

    while i < lengthData:
        print("\ni: " + str(i))
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
        if grammar["ignores"] != []:        
            if len(grammar["ignores"]) == 1 and token != grammar["ignores"][0]:
                tokens.append(token)
            elif len(grammar["ignores"]) > 1 and token not in grammar["ignores"]:
                tokens.append(token)
        else:
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


print("trailer")
