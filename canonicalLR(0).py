import pickle
import pydotplus
import time

Grammar = {}
with open("Grammar.pickle", "rb") as f:
    Grammar = pickle.load(f)

terminales = Grammar['terminales']
noTerminales = Grammar['noTerminales']
producciones = Grammar['producciones']
items = Grammar['items']
automatonStates = {}
automatonTransitions = []
count = 0
State = "I0"
usedStates = []

def main(producciones, items):
    start_time = time.time()

    first = [producciones[0][0], producciones[0][1].copy()]
    first[1].insert(0, ".")

    G = []
    G = closure([first])
    prod = [stat for stat in G if stat != first]
    automatonStates["I"+str(count)] = {"nucleo": [first], "producciones": prod}
    C = [G]

    added = True
    while added == True:
        added = False
        for it in C:
            I = []
            for item in it:
                newItem = [item[0], item[1].copy()]
                I.append(newItem)
            for gram in items:
                go = goto(I, gram)
                if go != [] and go not in C:
                    added = True
                    C.append(go)

    final = [producciones[0][0], producciones[0][1].copy()]
    final[1].append(".")
    print("Final: ", final)

    for state in automatonStates:
        core = automatonStates[state]['nucleo']
        if final in core:
            automatonTransitions.append([state, "$", "accept"])
            break

    for state in automatonStates:
        print("\n")
        print(state)
        print("nucleo:, ")
        for n in automatonStates[state]['nucleo']:
            print(n)
        print("\nproducciones:, ")
        for p in automatonStates[state]['producciones']:
            print(p)

    print("\n\n")
    for transition in automatonTransitions:
        print(transition)


    pydotplus.find_graphviz()

    graph = graph_automaton()

    # Save or display the graph
    png_file_path = "automaton_graph.png"
    graph.write_png(png_file_path)  # Save PNG file

    end_time = time.time()

    time_taken = end_time - start_time

    print(f"Time taken by the operation is {time_taken} seconds")


def closure(I):
    J = []
    J.extend(I)
    global producciones, noTerminales
    added = True
    while added == True:
        added = False
        for item in J:
            if "." in item[1] and item[1].index('.') != len(item[1])-1:
                nextItem = item[1][item[1].index('.')+1]
                if nextItem in noTerminales:
                    for production in producciones:
                        if production[0] == nextItem:
                            pro = [production[0], production[1].copy()]
                            pro[1].insert(0, ".")
                            if pro not in J:
                                J.append(pro)
                                added = True
    return J    


def goto(I, X):
    A = []
    lista = []
    for item in I:
        if "." in item[1] and item[1].index('.') != len(item[1])-1:
            if item[1][item[1].index('.')+1] == X:
                for key in automatonStates:
                    tempState = automatonStates[key]

                    if item in tempState['nucleo'] and [item[0], item[1].copy(), key] not in usedStates:
                        currentState = key
                        break
                    
                    if item in tempState['producciones'] and [item[0], item[1].copy(), key] not in usedStates:
                        currentState = key
                        break

                try:
                    print(currentState)
                except:
                    break

                used = [item[0], item[1].copy(), currentState]
                usedStates.append(used)
                newItem = [item[0], item[1].copy()]
                index = newItem[1].index('.')
                newItem[1][index] = newItem[1][index+1]
                newItem[1][index+1] = '.'
                temp = closure([newItem])
                for stat in temp:
                    if stat != newItem and stat not in A:
                        A.append(stat)
                addAutomaton(newItem, A, X, currentState)
                newList = []
                if A == []:
                    newList = [newItem + A]
                else:
                    newList = [newItem] + A
                for li in newList:
                    if li not in lista:
                        lista.append(li)

    return lista


def addAutomaton(nucleo, product, X, currentState):
    global count, automatonStates, State
    alreadyExists = False
    nextState = ""

    for key in automatonTransitions:
        if currentState == key[0] and X == key[1]:
            alreadyExists = True
            nextState = key[2]
            break

    if alreadyExists == False:
        for key in automatonStates:
            tempState = automatonStates[key]
            if nucleo == tempState['nucleo'][0]:
                alreadyExists = True
                nextState = key
                break
        

    if alreadyExists == False:
        count += 1
        print("Creating state: I"+str(count))
        automatonStates["I"+str(count)] = {"nucleo": [nucleo], "producciones": product}

        automatonTransitions.append([currentState, X, "I"+str(count)])
        State = "I"+str(count)

    else:
        if nucleo not in automatonStates[nextState]['nucleo']:
            automatonStates[nextState]['nucleo'].append(nucleo)

        add = False
        for tran in automatonTransitions:
            if currentState == tran[0] and X == tran[1]:
                add = True
                break

        if add == False:
            automatonTransitions.append([currentState, X, nextState])
    
    for state in automatonStates:
        print("\n")
        print(state)
        print("nucleo:, ")
        for n in automatonStates[state]['nucleo']:
            print(n)
        print("\nproducciones:, ")
        for p in automatonStates[state]['producciones']:
            print(p)

    print("\n\n")
    for transition in automatonTransitions:
        print(transition)


def graph_automaton():

    # Create a DOT format representation of the DFA
    dot = pydotplus.Dot()
    dot.set_rankdir("TB")  # Use 'TB' for top to bottom layout
    dot.set_prog("neato")

    state_nodes = {}
    num = 0
    for state in automatonStates:
        allStringNucleo = ""
        for n in automatonStates[state]['nucleo']:
            allStringNucleo += n[0] + " \u2192 " + ' '.join(n[1]) + "\n"

        allStringNucleo = allStringNucleo.replace('\n', '<BR/>')
        
        if automatonStates[state]['producciones'] != []:
            allStringProduct = ""
            for p in automatonStates[state]['producciones']:
                allStringProduct += p[0] + " \u2192 " + ' '.join(p[1]) + "\n"
        
            allStringProduct = allStringProduct.replace('\n', '<BR/>')
        
            node_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
    <TR><TD>{state}</TD></TR>        
    <TR><TD>{allStringNucleo}</TD></TR>
    <TR><TD BGCOLOR="lightgrey">{allStringProduct}</TD></TR>
    </TABLE>>'''
        
        else:
            node_label = f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
    <TR><TD>{state}</TD></TR>        
    <TR><TD>{allStringNucleo}</TD></TR>
    </TABLE>>'''

        node = pydotplus.Node(state, label=node_label, shape="none")    
        state_nodes[state] = node
        dot.add_node(node)

        num += 1

    # Add transitions as edges
    for (source, symbol, target) in automatonTransitions:
        if str(source) in state_nodes and str(target) == "accept":
            edge = pydotplus.Edge(state_nodes[str(source)], str(target), label=symbol)
            dot.add_edge(edge)
        elif (str(source) in state_nodes and str(target) in state_nodes):
            edge = pydotplus.Edge(state_nodes[str(source)], state_nodes[str(target)], label=symbol)
            dot.add_edge(edge)

    return dot


if __name__ == "__main__":
    main(producciones, items)