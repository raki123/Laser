from stream.teststream import TestStream
from evalunit.program import Program
from evalunit.rule import Rule


stream = {
        0:["r(a,b)", "a", "z(a,b,c)",],
        1:["p(c,d)", "b", "z(a,b,c)", "t(a)"],
        2:["b", "e(a,b,c)", "e(a)"],
}
rules = [
        "s(A)   :- t(A)",
        "p(B,C) :- r(B,C) and not(s(C))",
        "q(XX,YY) :- p(XX,YY)",
        "z(Y,X) :- q(X,Y)",
]

s = TestStream(stream, 0,2)
prog = Program(rules, s)

tuples = {}

for i in range(len(stream)-1):
    res, tupl = prog.evaluate(i)
    tuples.update(tupl)

add = lambda x,y: x + y
mult = lambda x,y: x * y
one = 1
zero = 0

print(add(one,one))

class Formula:
    #operators
    BOX = 0
    DIAMOND = 1
    ATT = 2
    TRIANGLE = 3
    AND = 4
    OR = 5
    NEG = 6
    WINDOW = 7
    NONE = -1

    #atom type
    PROP = 0
    NUM = 1

    operator = -1
    basicType = -1
    arguments = []

    def __init__(self, operator, arguments, basicType):
        self.operator = operator
        self.arguments = arguments
        self.basicType = basicType


def evalGroundWeightedQuery(dStream, rules, queryFormula, t):
    s = TestStream(dStream, 0, len(dStream)-1)
    prog = Program(rules, s)

    aStream = None
    for i in range(t+1):
        res, aStream = prog.evaluate(i)
    
    down = True
    formStack = [queryFormula]
    valStack = [None]
    timeStack = [t]
    idxStack = []
    minMaxStack = [(0,len(dStream)-1)]

    while(0 < len(formStack)):
        if(down):
            if(formStack[-1].operator == Formula.BOX):
                print("BOX")
                valStack[-1] = one
                valStack.append(one)
                idxStack.append(0)
                timeStack.append(-1)
                down = False
            elif(formStack[-1].operator == Formula.DIAMOND):
                print("DIAMOND")
                valStack[-1] = zero
                valStack.append(zero)
                idxStack.append(0)
                timeStack.append(-1)
                down = False
            elif(formStack[-1].operator == Formula.ATT):
                print("ATT")
                timeStack.append(formStack[-1].arguments[0])
                formStack.append(formStack[-1].arguments[1])
            elif(formStack[-1].operator == Formula.TRIANGLE):
                print("TRIANGLE")
                formStack.append(formStack[-1].arguments[0])
                minMaxStack.append(minMaxStack[0])
            elif(formStack[-1].operator == Formula.AND):
                print("AND")
                formStack.append(formStack[-1].arguments[0])
                idxStack.append(0)
            elif(formStack[-1].operator == Formula.OR):
                print("OR")
                formStack.append(formStack[-1].arguments[0])
                idxStack.append(0)
            elif(formStack[-1].operator == Formula.NEG):
                print("NEG")
                formStack.append(formStack[-1].arguments[0])
            elif(formStack[-1].operator == Formula.WINDOW):
                print("WINDOW")
                cur = minMaxStack[-1]
                newMin = max(cur[0], timeStack[-1] - formStack[-1].arguments[0])
                newMax = min(cur[1], timeStack[-1] + formStack[-1].arguments[1])
                minMaxStack.append((newMin, newMax))
                formStack.append(formStack[-1].arguments[2])
            elif(formStack[-1].operator == Formula.NONE):
                if(formStack[-1].basicType == Formula.PROP):
                    print("PROP") 
                    if(timeStack[-1] in aStream and timeStack[-1] >= minMaxStack[-1][0] and timeStack[-1] <= minMaxStack[-1][1]):
                        stringRep = formStack[-1].arguments[0]
                        if(len(formStack[-1].arguments) > 1):
                            stringRep += '('
                            args = formStack[-1].arguments[1:]
                            for i in range(len(args)-1):
                                stringRep += args[i]
                                stringRep += ','
                            stringRep += args[-1]
                            stringRep += ')'
                        print(stringRep)
                        valStack[-1] = one if stringRep in aStream[timeStack[-1]] else zero
                    else:
                        valStack[-1] = 0
                    down = False
                elif(formStack[-1].basicType == Formula.NUM):
                    print("NUM") 
                    valStack[-1] = formStack[-1].arguments[0]
                    down = False
        else:
            if(formStack[-1].operator == Formula.BOX):
                print("BOX")
                lastVal = valStack.pop()
                timeStack.pop()
                valStack[-1] = mult(valStack[-1], lastVal)
                minMax = minMaxStack[-1]
                if(idxStack[-1] <= minMax[1] - minMax[0]):
                    down = True
                    formStack.append(formStack[-1].arguments[0])
                    valStack.append(None)
                    timeStack.append(minMax[0] + idxStack[-1])
                    idxStack[-1] += 1
                else:
                    formStack.pop()
                    idxStack.pop()
            elif(formStack[-1].operator == Formula.DIAMOND):
                print("DIAMOND")
                lastVal = valStack.pop()
                timeStack.pop()
                valStack[-1] = add(valStack[-1], lastVal)
                minMax = minMaxStack[-1]
                if(idxStack[-1] <= minMax[1] - minMax[0]):
                    down = True
                    formStack.append(formStack[-1].arguments[0])
                    valStack.append(None)
                    timeStack.append(minMax[0] + idxStack[-1])
                    idxStack[-1] += 1
                else:
                    formStack.pop()
                    idxStack.pop()
            elif(formStack[-1].operator == Formula.ATT):
                print("ATT")
                formStack.pop()
                timeStack.pop()
            elif(formStack[-1].operator == Formula.TRIANGLE):
                print("TRIANGLE")
                formStack.pop()
                minMaxStack.pop()
            elif(formStack[-1].operator == Formula.AND):
                print("AND")
                if(idxStack[-1] == 0):
                    down = True
                    formStack.append(formStack[-1].arguments[1])
                    valStack.append(None)
                    idxStack[-1] = 1
                else:
                    formStack.pop()
                    cVal = valStack.pop()
                    valStack[-1] = mult(valStack[-1], cVal)
                    idxStack.pop()
            elif(formStack[-1].operator == Formula.OR):
                print("OR")
                if(idxStack[-1] == 0):
                    down = True
                    formStack.append(formStack[-1].arguments[1])
                    valStack.append(None)
                    idxStack[-1] = 1
                else:
                    formStack.pop()
                    cVal = valStack.pop()
                    valStack[-1] = add(valStack[-1], cVal)
                    idxStack.pop()
            elif(formStack[-1].operator == Formula.NEG):
                print("NEG")
                valStack[-1] = one if valStack[-1] == zero else zero
                formStack.pop()
            elif(formStack[-1].operator == Formula.WINDOW):
                print("WINDOW")
                formStack.pop()
                minMaxStack.pop()
            elif(formStack[-1].operator == Formula.NONE):
                if(formStack[-1].basicType == Formula.PROP):
                    print("PROP") 
                    formStack.pop()
                elif(formStack[-1].basicType == Formula.NUM):
                    print("NUM")   
                    formStack.pop()
    return valStack.pop()

f1 = Formula(Formula.NONE, ["a"], Formula.PROP)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
f12 = Formula(Formula.AND, [f1, f2], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, f12, 0))

f1 = Formula(Formula.NONE, ["a"], Formula.PROP)
fneg1 = Formula(Formula.NEG, [f1], Formula.NONE)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
fneg12 = Formula(Formula.AND, [fneg1, f2], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, fneg12, 0))

f1 = Formula(Formula.NONE, ["p","a","b"], Formula.PROP)
fneg1 = Formula(Formula.NEG, [f1], Formula.NONE)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
fneg12 = Formula(Formula.OR, [fneg1, f2], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, fneg12, 0))

f1 = Formula(Formula.NONE, ["a"], Formula.PROP)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
f12 = Formula(Formula.OR, [f1, f2], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, f12, 0))

f1 = Formula(Formula.NONE, ["a"], Formula.PROP)
fat = Formula(Formula.ATT, [1, f1], Formula.NONE)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
f12 = Formula(Formula.OR, [fat, f2], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, f12, 0))

f1 = Formula(Formula.NONE, ["p","a","b"], Formula.PROP)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
f12 = Formula(Formula.OR, [f1, f2], Formula.NONE)
forall = Formula(Formula.BOX, [f12], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, forall, 0))

f1 = Formula(Formula.NONE, ["p","a","b"], Formula.PROP)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
f12 = Formula(Formula.OR, [f1, f2], Formula.NONE)
fxsists = Formula(Formula.DIAMOND, [f12], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, fxsists, 0))

f1 = Formula(Formula.NONE, ["p","a","b"], Formula.PROP)
fat = Formula(Formula.ATT, [0, f1], Formula.NONE)
f2 = Formula(Formula.NONE, [16], Formula.NUM)
f12 = Formula(Formula.OR, [fat, f2], Formula.NONE)
fxsists = Formula(Formula.DIAMOND, [f12], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, fxsists, 0))

forall = Formula(Formula.BOX, [f2], Formula.NONE)
fredact = Formula(Formula.TRIANGLE, [forall], Formula.NONE)
fnone = Formula(Formula.WINDOW, [-1, -1, fredact], Formula.NONE)
print(evalGroundWeightedQuery(stream, rules, fnone, 0))

