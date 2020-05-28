import tkinter as tk

win = tk.Tk()

win.title("Calculator")
win.geometry("250x300")
win.iconbitmap('./calculatorIcon.ico')


def checkParenthesis(expList):
    """
    Checks that the parenthesis are properly placed. Additionally, it corrects any assumptions of multiplication
    expressions
    :param expList	List which the function takes as parameter so that it can directly modify the expression inside
    :return: 		True if all parentheses are correctly placed, False if not (so empty parenthesis "()" or unbalanced)
    """
    expression = expList[0]
    balance = 0
    index = 0
    while (index < len(expression)):
        if (index > 0):
            if (expression[index - 1] == "(" and expression[index] == ")"):  # Detects "()", which is invalid
                return False
            if (((expression[index - 1] in "0123456789" and expression[index] == "(") or (expression[index - 1] == ")"
                                                                                          and expression[index]
                                                                                          in "0123456789"))):
                expression = expression[:index] + "*" + expression[index:]
            if (expression[index - 1] == ")" and expression[index] == "("):  # Inserts multiplication when ")(" is found
                expression = expression[:index] + "*" + expression[index:]
        # We now check the balance of parentheses. This must be checked AFTER modifying the expression since we could
        # double-count and get the wrong balance
        if (expression[index] == "("):
            balance += 1
        elif (expression[index] == ")"):
            balance -= 1  # Balance should be 0 if parentheses come in pairs
        index += 1
    if (balance != 0):
        return False
    # Relation between operators and parentheses is dealt with in checkOperators
    expList[0] = expression
    return True


def checkChars(expList):
    """
    Simply checks that all the characters inserted are valid symbols
    :param expList	List which the function takes as parameter so that it can directly modify the expression inside
    :return: 		True if all characters are valid symbols, False if not
    """
    expression = expList[0]
    for char in expression:
        if (not (char in "1234567890.*/+-()")):
            return False
    return True


def checkOperators(expList):
    """
    Checks that the operators are legally placed in the expression
    :param expList	List which the function takes as parameter so that it can directly modify the expression inside
    :return: 		True if all operators are correctly placed, False if not
    """
    expression = expList[0]
    # Operator at the end of the expression is always wrong
    # Multiplication or division at the start of an expression is always wrong
    if ((expression[0] in "*/") or (expression[-1] in "*/+-")):
        return False
    if (expression[0] == "+"):
        expression = expression[1:]  # Remove unnecessary "+" at the start

    for index in range(1, len(expression)):
        # Operators with other operators
        if ((expression[index - 1] == "+" and expression[index] == "-") or
                (expression[index - 1] == "-" and expression[index] == "+")):
            # Negative and positive symbol right beside each other results in just a negative symbol
            expression = expression[:index - 1] + "-" + expression[index + 1:]
            index = 0  # Check the whole expression again

        elif ((((expression[index - 1] == "-") and (expression[index] == "-")) or
               ((expression[index - 1] == "+") and (expression[index] == "+")))):
            # Turning a double negative or positive into a positive
            expression = expression[:index - 1] + "+" + expression[index + 1]

        elif ((expression[index - 1] in "+-*/") and (expression[index] in "*/")):
            return False

        elif ((expression[index - 1] in "*/") and (expression[index] == "+")):
            expression = expression[:index] + expression[index + 1:]  # Skips the unnecessary "+"
            index = 0  # Check the whole expression again

        # Operators and parenthesis
        if (((expression[index - 1] == "(") and (expression[index] in "*/")) or (
                (expression[index - 1] in "*/+-") and (expression[index] == ")"))):
            # Checks that operators aren't illegally placed around the parentheses symbols
            return False

    expList[0] = expression
    return True


def checkDecimalPoint(expList):
    """
    Checks that the decimal points are placed properly
    :param expList	List which the function takes as parameter so that it can directly modify the expression inside
    :return: 		True if all decimal points are correctly placed, False if not
    """
    expression = expList[0]
    index = 0
    DecimalAllowedAgain = True  # Makes sure that only one decimal per number is allowed. More details further down
    #No decimal point at the start or end of the entire expression
    if (expression[0] == "." or expression[-1] == "."):
        return False
    for char in expression:
        # If we come across an operator or parenthesis, a new number emerges, allowing it to have a decimal
        if (expression[index] in "*/+-()"):
            DecimalAllowedAgain = True  # We will come across a new number, so a new decimal may exist
        elif (DecimalAllowedAgain and expression[index] == "."):
            DecimalAllowedAgain = False  # This blocks any new decimal until we come across an operator or parenthesis
            if ((index != len(expression) - 1) and
                    (not (expression[index - 1] in "0123456789" and expression[index + 1] in "0123456789"))):
                return False
        index += 1
    return True


# CALCULATIONS
def result(expression):
    """
    Begins the result of finding the expression on the display
    :param expression String which contains the expression we want to solve. It is what appears in the "display" of the
    screen
    """
    clearInvalidInput() #Clears the screen of the text "Invalid input" in the case that it is there right now
    # First, check input is valid
    expList = [expression]  # Putting it into a list so that the functions can modify it as they check it
    valid = checkChars(expList) and checkDecimalPoint(expList) and checkParenthesis(expList) and checkOperators(expList)
    expression = expList[0]  # Making expression turn into its checked version
    print("Validity: " + str(valid))
    for char in expression:
        print("Char: " + char)
    # Then, find most inner parenthesis expressions and solve them
    clearDisplay()  # Clearing the display to later display whatever we want
    if (valid):
        display.insert(tk.END, findConAndSolve(expList))
    else:
        display.insert(tk.END, "Invalid input")


def findConAndSolve(expList):
    """
    Most important part of the calculator. It finds content (parts of the expression which is between parenthesis) and
    reinserts the result of that content back into the original expression without the parenthesis. It will go from left
    to right, looking for the innermost parenthesis and working its way out.
    :param expList  List which the function takes as parameter so that it can directly modify the expression inside
    :return: Returns the final answer to the expression initially inputted
    """
    expression = expList[0]
    print("Expression to solve: " + expression)
    toReturn = expression
    parFound = False
    ignition = True
    # While-loop runs whilst there are still parentheses to be solved
    while (parFound or ignition):
        ignition = False  # Used for simulating a do-while, so we turn it off now
        # Reset start and stop (these indicate the beginning and end of the content to be solved)
        start = 0
        stop = len(toReturn)  # If no parenthesis, we take the whole expression
        """
        Notice how the following for-loop works: it resets the position of the index "start" to whatever "(" is found, 
        and the loop is broken once we find the corresponding ")". We can be sure that this works properly thanks to the
        checkParenthesis() function that was previously used.
        """
        for index in range(0, len(toReturn)):
            if (toReturn[index] == "("):
                start = index + 1
                parFound = True
            elif (toReturn[index] == ")"):
                stop = index
                break
        # We want to save the parts of the expression that came before and after to later reattach them
        beginning = toReturn[:start - 1]
        end = toReturn[stop + 1:]
        if (start == 0):
            beginning = ""
        if (stop == len(toReturn)):
            end = ""
        if (start == 0 and stop == len(toReturn)):
            parFound = False
        toReturn = beginning + str(solve(toReturn[start:stop])) + end
        print("Result after parenthesis solved: " + toReturn)
    print("Final Result: " + toReturn)
    return toReturn


def solve(content):
    """
    Receiving a string with just numbers and operators (no parenthesis), we can now apply the order of operations. That
    of course mean that multiplication and division go first, then addition and subtraction. It will return the solution
    to the content so that it can be reinserted into the expression without the parentheses.
    :param content          String which holds the content of the parenthesis to be solved
    :return: solvedContent  String which is the entire content solved
    """
    # First, multiplication and division from left to right
    start = 0
    stop = 0
    alphaOPfound = False # Signal for when the first "*" or "/" operator to be applied is found (Alpha Operator)
    OPindex = 0
    contentArray = [content] # Putting the content into an array so that checkOperators() can alter the string
    checkOperators(contentArray)  # Just to clear up whenever +- or -+ pops up from previous resolutions
    content = contentArray[0]
    print("	Content to solve: " + content)
    for index in range(1, len(content)):
        # Skips + and -, start is placed at the beginning of the first number to operate,
        # if there even is a mul or div to do
        if(not alphaOPfound):
            if (content[index] in "+-"):
                start = index + 1
            elif (content[index] in "*/"):
                OPindex = index  # Locating where the operator is
                alphaOPfound = True
        elif ((index - 1 != OPindex) and content[index] in "*/+-"):
            # Careful of + or - right after a * or /
            stop = index
            break
        else:
            stop = index + 1

    betaOPfound = False # Signal for when the first "+" or "-" operator to be applied is found (Beta Operator)
    if (not (alphaOPfound)):  # In case no mul or div is found, we do plus and minus, from left to right
        start = 0
        for index in range(1, len(content)):
            if(not betaOPfound):
                if(content[index] in "+-"):
                    OPindex = index
                    betaOPfound = True

            elif (content[index] in "+-"):
                stop = index
                break
            else:
                stop = index + 1

    if (not (alphaOPfound or betaOPfound)):
        print("		Base case reached or No operator found in content. Returning: " + content)
        return str(content)  # BASE CASE FOR RECURSION, no operators left

    # Giving the basic operation to solveBasic()
    solvedBasic = solveBasic(content[start:stop], OPindex - start)

    # Check if decimal point is necessary
    if (int(solvedBasic) == float(solvedBasic)):
        solvedBasic = int(solvedBasic)  # Get rid of decimal part if it's not necessary

    # Recursion until no operators are left
    solvedContent = str(solve(content[:start] + str(solvedBasic) + content[stop:]))
    print("		Solved Content: " + solvedContent)
    return solvedContent


def solveBasic(basic, OPindex):
    """
    Solves the simple operation identified by solve() and returns the solution.
    :param basic    String which contains the first number concatenated with the operator and the second number
    :param OPindex  Indicates where in the string is the operator in order to properly separate the two numbers and
    apply the appropriate operation
    :return:        The result of this basic operation
    """
    print("			Basic: " + basic)
    print("			OPindex: " + str(OPindex))
    if (basic[OPindex] == "*"):
        return ((float(basic[:OPindex])) * (float(basic[OPindex + 1:])))
    elif (basic[OPindex] == "/"):
        return ((float(basic[:OPindex])) / (float(basic[OPindex + 1:])))
    elif (basic[OPindex] == "+"):
        return ((float(basic[:OPindex])) + (float(basic[OPindex + 1:])))
    elif (basic[OPindex] == "-"):
        return ((float(basic[:OPindex])) - (float(basic[OPindex + 1:])))


# -------------------------------------------------------------------------------------------------------------

# CLEAR DISPLAY
def clearDisplay():
    display.delete("1.0", "end")


def clearInvalidInput():
    if (display.get("1.0", "end-1c") == "Invalid input"): clearDisplay()


# DELETE LAST INPUT
def deleteLast():
    display.delete("%s-1c" % tk.INSERT, tk.INSERT)

# Insert character
def insertChar(char):
    clearInvalidInput()
    display.insert(tk.END, str(char))


# BUTTONS
# This display will show what has been inputted and the result of said input
display = tk.Text(win, height=1, font=(12))
display.grid(row=0, column=0, sticky="nsew")
win.grid_rowconfigure(0, weight=1)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)

# This frame allows us to have buttons right under the display, so it's like
# having a grid within a grid
buttons_frame = tk.Frame(win)
buttons_frame.grid(row=1, column=0, sticky="nsew")
buttons_frame.grid_rowconfigure(0, weight=1)
buttons_frame.grid_rowconfigure(1, weight=1)
buttons_frame.grid_rowconfigure(2, weight=1)
buttons_frame.grid_rowconfigure(3, weight=1)
buttons_frame.grid_rowconfigure(4, weight=1)
buttons_frame.grid_columnconfigure(0, weight=1)
buttons_frame.grid_columnconfigure(1, weight=1)
buttons_frame.grid_columnconfigure(2, weight=1)
buttons_frame.grid_columnconfigure(3, weight=1)

# Now we can make buttons that insert numbers into the display
# First, the numbers
bwidth = 8
bheight = 3  # Dimensions of the number buttons
b1 = tk.Button(buttons_frame, text="1", command=lambda: insertChar(1))
b1.grid(row=1, column=0, sticky="nsew")
b2 = tk.Button(buttons_frame, text="2", command=lambda: insertChar(2))
b2.grid(row=1, column=1, sticky="nsew")
b3 = tk.Button(buttons_frame, text="3", command=lambda: insertChar(3))
b3.grid(row=1, column=2, sticky="nsew")
b4 = tk.Button(buttons_frame, text="4", command=lambda: insertChar(4))
b4.grid(row=2, column=0, sticky="nsew")
b5 = tk.Button(buttons_frame, text="5", command=lambda: insertChar(5))
b5.grid(row=2, column=1, sticky="nsew")
b6 = tk.Button(buttons_frame, text="6", command=lambda: insertChar(6))
b6.grid(row=2, column=2, sticky="nsew")
b7 = tk.Button(buttons_frame, text="7", command=lambda: insertChar(7))
b7.grid(row=3, column=0, sticky="nsew")
b8 = tk.Button(buttons_frame, text="8", command=lambda: insertChar(8))
b8.grid(row=3, column=1, sticky="nsew")
b9 = tk.Button(buttons_frame, text="9", command=lambda: insertChar(9))
b9.grid(row=3, column=2, sticky="nsew")
b0 = tk.Button(buttons_frame, text="0", command=lambda: insertChar(0))
b0.grid(row=4, column=0, sticky="nsew")

# Decimal point
bdecp = tk.Button(buttons_frame, text=".", command=lambda: insertChar("."))
bdecp.grid(row=0, column=0, sticky="nsew")

# Now a button to remove the last thing inserted
bdel = tk.Button(buttons_frame, text="DEL", command=deleteLast)
bdel.grid(row=1, column=3, sticky="nsew")

# We need to have operations
bplus = tk.Button(buttons_frame, text="+", command=lambda: insertChar("+"))
bplus.grid(row=2, column=3, sticky="nsew")
bminus = tk.Button(buttons_frame, text="-", command=lambda: insertChar("-"))
bminus.grid(row=3, column=3, sticky="nsew")
bmul = tk.Button(buttons_frame, text="*", command=lambda: insertChar("*"))
bmul.grid(row=4, column=1, sticky="nsew")
bdiv = tk.Button(buttons_frame, text="/", command=lambda: insertChar("/"))
bdiv.grid(row=4, column=2, sticky="nsew")
# Equal sign is a little different, since it will change the display to the result
bequal = tk.Button(buttons_frame, text="=", command=lambda: result(display.get("1.0", "end-1c")))
bequal.grid(row=4, column=3, sticky="nsew")

# Parenthesis
bLPar = tk.Button(buttons_frame, text="(", command=lambda: insertChar("("))
bLPar.grid(row=0, column=1, sticky="nsew")
bRPar = tk.Button(buttons_frame, text=")", command=lambda: insertChar(")"))
bRPar.grid(row=0, column=2, sticky="nsew")

# Clear the display
bC = tk.Button(buttons_frame, text="C", command=clearDisplay)
bC.grid(row=0, column=3, sticky="nsew")

win.mainloop()
