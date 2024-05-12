import pickle
import pydotplus
import time

from tabulate import tabulate

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
Firsts = {}
Follows = {}

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

    Firsts = firstFunction(producciones, terminales, noTerminales).copy()

    # print("Firsts: ")
    # for f in Firsts:
    #     print(f+":", Firsts[f])


    followFunction(producciones, terminales, noTerminales, Firsts)

    # print("Follows: ")
    # for f in Follows:
    #     print(f+":", Follows[f])

    for state in automatonStates:
        core = automatonStates[state]['nucleo']
        if final in core:
            automatonTransitions.append([state, "$", "accept"])
            break


    Action, Goto = tableConstructor(Follows, terminales)

    print_table(Action, Goto, terminales, noTerminales)

    print("\nEjecutando Simulación...")

    simulate_parsing(Action, Goto, Grammar['tokens'])

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
                    type(currentState)
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


def firstFunction(grammar, terminals, non_terminals):
    firsts = {}

    for non_terminal in non_terminals:
        firsts[non_terminal] = first(grammar, terminals, non_terminals, non_terminal)

    return firsts
    

def first(grammar, terminals, non_terminals, symbol):    
    first_set = set()

    if symbol in terminals:
        first_set.add(symbol)

    elif symbol in non_terminals:
        for simbolo, production in producciones:
            if simbolo != symbol:
                continue

            if production == '𝜀':
                first_set.add('𝜀')
            else:
                for s in production:
                    
                    # ==================================================
                    if s == symbol:
                        continue
                    # ==================================================

                    s_first = first(grammar, terminals, non_terminals, s)

                    if '𝜀' not in s_first:
                        first_set = first_set.union(s_first)
                        break

                    s_first.remove('𝜀')

                    first_set = first_set.union(s_first)
                else:
                    first_set.add('𝜀')

    return first_set


def followFunction(grammar, terminals, non_terminals, firstsList):
    for non_terminal in noTerminales:
        Follows[non_terminal] = follow(grammar, terminals, non_terminals, non_terminal, firstsList)


def follow(grammar, terminals, non_terminals, symbol, firstsList):
    follow_set = set()

    if symbol == producciones[0][0]:
        follow_set.add('$')

    for simbolo, productions in producciones:
        if symbol in productions:
            position = productions.index(symbol)
            if position != len(productions) - 1:
                next_symbol = productions[position + 1]
                if next_symbol in terminals:
                    follow_set.add(next_symbol)
                else:
                    follow_set = follow_set.union(firstsList[next_symbol])

                if next_symbol not in terminals and '𝜀' in firstsList[next_symbol]:
                    follow_set.remove('𝜀')
                    tempSet = Follows[simbolo]
                    follow_set = follow_set.union(tempSet)

            elif position == len(productions) - 1:
                if simbolo != symbol:
                    follow_set = follow_set.union(follow(grammar, terminals, non_terminals, simbolo, firstsList))
    
    return follow_set


def tableConstructor(followsList, terminals):
    Action = {}
    Goto = {}

    for states in automatonStates:
        allTransitions = []
        tempTransitions = list(automatonStates[states].values())
        for i in tempTransitions:
            if len(i) == 1:
                allTransitions.append(i[0])
            else:
                for j in i:
                    allTransitions.append(j)


        for nucleo in allTransitions:
            if '.' in nucleo[1] and nucleo[1].index('.') < len(nucleo[1])-1:
                nextSymbol = nucleo[1][nucleo[1].index('.')+1]
                if nextSymbol in terminals:
                    nextState = ""
                    for tran in automatonTransitions:
                        if states == tran[0] and nextSymbol == tran[1]:
                            nextState = tran[2]
                            Action[(states, nextSymbol)] = "S"+nextState[1:]

            elif nucleo[1].index('.') == len(nucleo[1])-1 and nucleo[0] != producciones[0][0]:
                beforeState = 0
                result = nucleo[1].copy()
                result.remove('.')
                for num, prod in enumerate(producciones):
                    if prod[0] == nucleo[0] and prod[1] == result:
                        beforeState = num
                        break
                for ite in followsList[nucleo[0]]:
                    Action[(states, ite)] = "R"+str(beforeState)
            
            elif nucleo[1].index('.') == len(nucleo[1])-1 and nucleo[0] == producciones[0][0]:
                Action[(states, '$')] = "accept"
        
        for tran in automatonTransitions:
            if tran[1] not in terminals and tran[1] != '$':
                Goto[(tran[0], tran[1])] = tran[2][1:]

    return Action, Goto


def print_table(action, goto, terminals, non_terminals):
    header = ["State"] + terminals + non_terminals

    states = set(state for state, _ in action.keys()).union(set(state for state, _ in goto.keys()))

    rows = []
    for state in sorted(states, key=lambda state: int(state[1:])):
        row = [state]
        for terminal in terminals:
            row.append(action.get((state, terminal), ""))
        for non_terminal in non_terminals:
            row.append(goto.get((state, non_terminal), ""))
        rows.append(row)

    print(tabulate(rows, headers=header, tablefmt="pretty"))


def simulate_parsing(action, goto, input_string):
    stack = [0]

    input_string.append('$')

    symbols = []

    while True:
        state = stack[-1]

        symbol = input_string[0]

        if ('I'+str(state), symbol) in action and action[('I'+str(state), symbol)][0] == "S":

            print("Shift", action[('I'+str(state), symbol)])

            stack.append(action[('I'+str(state), symbol)][1:])

            symbols.append(input_string.pop(0))

        elif ('I'+str(state), symbol) in action and action[('I'+str(state), symbol)][0] == "R":

            nucleo, product = producciones[int(action[('I'+str(state), symbol)][1:])]

            print("Reduce", action[('I'+str(state), symbol)], "with production: ", nucleo + " \u2192 " + ' '.join(product))

            if len(product) == 1 and len(symbols) > 1:
                symbols.insert(symbols.index(product[0]), nucleo)
                symbols.remove(product[0])
                stack.pop()
            elif len(product) == 1 and len(symbols) == 1 and symbols == product:
                symbols.clear()
                symbols.append(nucleo)
                stack.pop()
            elif len(product) > 1 and symbols == product:
                symbols.clear()
                symbols.append(nucleo)
                for i in range (0,len(product)):
                    stack.pop()

            stack.append(goto[('I'+str(stack[-1]), nucleo)])

        elif ('I'+str(state), symbol) in action and action[('I'+str(state), symbol)] == "accept":
            print("Input aceptado")
            return

        else:
            print("Input rechazado")
            print("Error en estado:", 'I'+state, "con simbolo", symbol)
            return
        

def is_sublist(larger, smaller):
    smaller_length = len(smaller)
    for i in range(len(larger)):
        if larger[i:i+smaller_length] == smaller:
            return True
    return False

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