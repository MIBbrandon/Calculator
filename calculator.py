import tkinter as tk

win = tk.Tk()

win.title("Calculator")
win.geometry("250x300")

def checkParenthesis(expList):
	expression = expList[0]
	balance = 0
	ok = True
	index = 0
	while(index < len(expression)):
		if(index != 0 and expression[index-1]=="(" and expression[index]==")"): #Detects "()", which is invalid
			ok = False
			break
		if(index != 0 and ((expression[index-1] in "0123456789" and expression[index]=="(") or (expression[index-1]==")" and expression[index] in "0123456789"))):
			expression = expression[:index] + "*" + expression[index:]
		if(index != 0 and expression[index-1]==")" and expression[index]=="("): #Inserts multiplication when ")(" is found
			expression = expression[:index] + "*" + expression[index:]
		#We now check the balance of parentheses. This must be checked AFTER modifying the expression since we could double-count and get the wrong balance
		if(expression[index]=="("): 
			balance += 1
		elif(expression[index]==")"): 
			balance -= 1 #Balance should be 0 if parentheses come in pairs
		index += 1
	if(balance != 0): 
		ok = False
	#Relation between operators and parentheses is dealt with in checkOperators
	expList[0] = expression
	return ok

def checkChars(expList):
	expression = expList[0]
	for char in expression:
		if(not(char in "1234567890.*/+-()")): #Check that all characters are valid
			return False
	return True #Returns True if every character is valid

def checkOperators(expList):
	expression = expList[0]
	#Operator at the end of the expression is always wrong
	#Multiplication or division at the start of an expression is always wrong
	if((expression[-1] in "*/+-") or (expression[0] in "*/")): return False 
	if(expression[0]=="+"): expression = expression[1:] #Remove unnecessary "+" at the start

	for index in range(1, len(expression)):
		#Operators with other operators
		if((expression[index-1]=="+" and expression[index]=="-") or (expression[index-1]=="-" and expression[index]=="+")):
			expression = expression[:index-1] + "-" + expression[index+1:]
			index = 0 #Check the whole expression again
		if((expression[index-1] in "*/") and (expression[index] in "*/")): return False #"*" and "/" right beside each other is invalid
		if((((expression[index-1]=="-") and (expression[index]=="-")) or (index != 0 and (expression[index-1]=="+") and (expression[index]=="+")))): 
			expression = expression[:index-1] + "+" + expression[index+1] #Turning a double negative or positive into a positive
		if((expression[index-1] in "*/") and (expression[index]=="+")):
			expression = expression[:index] + expression[index+1:] #Skips the unnecessary "+"
			index = 0 #Check the whole expression again
		if((expression[index-1] in "+-") and (expression[index] in "*/")): return False
		#Operators and parenthesis
		if(((expression[index-1]=="(") and (expression[index] in "*/")) or ((expression[index-1] in "*/+-") and (expression[index]==")"))): 
			return False 
	expList[0] = expression
	return True

def checkDecimalPoint(expList):
	expression = expList[0]
	index = 0
	DecimalAllowedAgain = True #Makes sure that only one decimal per number is allowed. More details further down
	if(expression[0]=="." or expression[-1]=="."): return False
	for char in expression: #Checking conditions that decimal points should comply with
		if(expression[index] in "*/+-()"): #If we come across an operator or parenthesis, a new number emerges, allowing it to have a decimal
			DecimalAllowedAgain = True #We will come across a new number, so a new decimal may exist
		elif(DecimalAllowedAgain and expression[index]=="."):
			DecimalAllowedAgain = False #This blocks any new decimal until we come across an operator or parenthesis
			if((index != len(expression)-1) and (not(expression[index-1] in "0123456789" and expression[index+1] in "0123456789"))):
				return False
		index +=1
	return True

#CALCULATIONS
def result(expression): #Finds the result of the expression on the display
	clearInvalidInput()
	#First, check input is valid
	expList = [expression] #Putting it into a list so that the functions can modify it as they check it
	valid = checkChars(expList) and checkDecimalPoint(expList) and checkParenthesis(expList) and checkOperators(expList)
	expression = expList[0] #Making expression turn into its checked version
	print("Validity: " + str(valid))
	for char in expression:
		print("Char: " + char)
	#Then, find most inner parenthesis expressions and solve them
	clearDisplay() #Clearing the display to later display whatever we want
	if(valid):
		display.insert(tk.END, findConAndSolve(expression))
	else:
		display.insert(tk.END, "Invalid input")

def findConAndSolve(expression):
	print("Expression to solve: " + expression)
	toReturn = expression
	start = 0
	stop = len(toReturn) #If no parenthesis, we take the whole expression
	parFound = False
	ignition = True
	while (parFound or ignition):
		ignition = False #Used for simulating a do-while, we turn it off now
		#Reset start and stop
		start = 0
		stop = len(toReturn) #If no parenthesis, we take the whole expression
		for index in range(0, len(toReturn)):
			if(toReturn[index]=="("):
				start = index + 1
				parFound = True
			elif(toReturn[index]==")"):
				stop = index
				break
		beginning = toReturn[:start-1]
		end = toReturn[stop+1:]
		if(start==0): beginning = ""
		if(stop==len(toReturn)): end = ""
		if(start==0 and stop==len(toReturn)): parFound = False
		toReturn = beginning + str(solve(toReturn[start:stop])) + end
		print("	" + toReturn)
	print(toReturn)
	return toReturn

def solve(content):
	#First, multiplication and division from left to right
	start = 0
	stop = 0
	primeOPfound = False
	OPindex = 0
	print("	Content to solve: " + content)
	for index in range(1, len(content)):
		#Skips + and -, start is placed at the beginning of the first number to operate, if there even is a mul or div to do
		if(not(primeOPfound) and content[index] in "+-"): start = index+1
		elif(not(primeOPfound) and content[index] in "*/"):
			OPindex = index #Locating where the operator is
			primeOPfound = True
		elif(primeOPfound and (index-1 != OPindex) and content[index] in "*/+-"): #Careful of + or - right after a * or /
			stop = index
			break
		elif(primeOPfound):
			stop = index + 1

	betaOPfound = False
	if(not(primeOPfound)): #In case no mul or div is found, we do plus and minus, from left to right
		start = 0
		for index in range(1, len(content)):
			if(not(betaOPfound) and content[index] in "+-"):
				OPindex = index
				betaOPfound = True
			elif(betaOPfound and content[index] in "+-"):
				stop = index
				break
			elif(betaOPfound):
				stop = index + 1

	if(not(primeOPfound or betaOPfound)):
		print("		Base case reached or No operator found in content. Returning: " + content)
		return str(content) #BASE CASE FOR RECURSION, no operators left

	solvedBasic = solveBasic(content[start:stop], OPindex-start)
	#Check if decimal point is necessary
	if(int(solvedBasic)==float(solvedBasic)): solvedBasic = int(solvedBasic) #Get rid of decimal part if it's not necessary
	solvedContent = str(solve(content[:start] + str(solvedBasic) + content[stop:])) #Recursion until no operators are left
	print("		Solved Content: " + solvedContent)
	return solvedContent

def solveBasic(basic, OPindex):
	print("			Basic: " + basic)
	print("			OPindex: " + str(OPindex))
	if(basic[OPindex]=="*"):
		return ((float(basic[:OPindex]))*(float(basic[OPindex+1:])))
	elif(basic[OPindex]=="/"):
		return ((float(basic[:OPindex]))/(float(basic[OPindex+1:])))
	elif(basic[OPindex]=="+"):
		return ((float(basic[:OPindex]))+(float(basic[OPindex+1:])))
	elif(basic[OPindex]=="-"):
		return ((float(basic[:OPindex]))-(float(basic[OPindex+1:])))

#-------------------------------------------------------------------------------------------------------------

#CLEAR DISPLAY
def clearDisplay():
	display.delete("1.0","end")

def clearInvalidInput():
	if(display.get("1.0", "end-1c")=="Invalid input"): clearDisplay()

#DELETE LAST INPUT
def deleteLast():
	display.delete("%s-1c" % tk.INSERT, tk.INSERT)

#OPERATIONS
def plus():
	clearInvalidInput()
	display.insert(tk.END, "+")
def minus():
	clearInvalidInput()
	display.insert(tk.END, "-")
def multiply():
	clearInvalidInput()
	display.insert(tk.END, "*")
def divide():
	clearInvalidInput()
	display.insert(tk.END, "/")

#Parenthesis
def leftPar():
	clearInvalidInput()
	display.insert(tk.END, "(")
def rightPar():
	clearInvalidInput()
	display.insert(tk.END, ")")

#Decimal Point
def decimalPoint():
	clearInvalidInput()
	display.insert(tk.END, ".")

#Insert number
def insertChar(char):
	clearInvalidInput()
	display.insert(tk.END, str(char))

#BUTTONS
#This display will show what has been inputted and the result of said input
display = tk.Text(win, height=1,font=(12))
display.grid(row=0, column=0, sticky="nsew")
win.grid_rowconfigure(0, weight=1)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)

#This frame allows us to have buttons right under the display, so it's like
#having a grid within a grid
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

#Now we can make buttons that insert numbers into the display
#First, the numbers
bwidth=8
bheight=3 #Dimensions of the number buttons
b1 = tk.Button(buttons_frame,text="1", command=lambda: insertChar(1))
b1.grid(row=1, column=0, sticky="nsew")
b2 = tk.Button(buttons_frame,text="2", command=lambda: insertChar(2))
b2.grid(row=1, column=1, sticky="nsew")
b3 = tk.Button(buttons_frame,text="3", command=lambda: insertChar(3))
b3.grid(row=1, column=2, sticky="nsew")
b4 = tk.Button(buttons_frame,text="4", command=lambda: insertChar(4))
b4.grid(row=2, column=0, sticky="nsew")
b5 = tk.Button(buttons_frame,text="5", command=lambda: insertChar(5))
b5.grid(row=2, column=1, sticky="nsew")
b6 = tk.Button(buttons_frame,text="6", command=lambda: insertChar(6))
b6.grid(row=2, column=2, sticky="nsew")
b7 = tk.Button(buttons_frame,text="7", command=lambda: insertChar(7))
b7.grid(row=3, column=0, sticky="nsew")
b8 = tk.Button(buttons_frame,text="8", command=lambda: insertChar(8))
b8.grid(row=3, column=1, sticky="nsew")
b9 = tk.Button(buttons_frame,text="9", command=lambda: insertChar(9))
b9.grid(row=3, column=2, sticky="nsew")
b0 = tk.Button(buttons_frame,text="0", command=lambda: insertChar(0))
b0.grid(row=4, column=0, sticky="nsew")

#Decimal point
bdecp = tk.Button(buttons_frame, text=".", command=lambda: insertChar("."))
bdecp.grid(row=0, column=0, sticky="nsew")

#Now a button to remove the last thing inserted
bdel = tk.Button(buttons_frame, text="DEL", command=deleteLast)
bdel.grid(row=1, column=3, sticky="nsew")

#We need to have operations
bplus = tk.Button(buttons_frame, text="+", command=lambda: insertChar("+"))
bplus.grid(row=2, column=3, sticky="nsew")
bminus = tk.Button(buttons_frame, text="-", command=lambda: insertChar("-"))
bminus.grid(row=3, column=3, sticky="nsew")
bmul = tk.Button(buttons_frame, text="*", command=lambda: insertChar("*"))
bmul.grid(row=4, column=1, sticky="nsew")
bdiv = tk.Button(buttons_frame, text="/", command=lambda: insertChar("/"))
bdiv.grid(row=4, column=2, sticky="nsew")
#Equal sign is a little different, since it will change the display to the result
bequal = tk.Button(buttons_frame, text="=", command=lambda: result(display.get("1.0", "end-1c")))
bequal.grid(row=4, column=3, sticky="nsew")

#Parenthesis
bLPar = tk.Button(buttons_frame, text="(", command=lambda: insertChar("("))
bLPar.grid(row=0, column=1, sticky="nsew")
bRPar = tk.Button(buttons_frame, text=")", command=lambda: insertChar(")"))
bRPar.grid(row=0, column=2, sticky="nsew")

#Clear the display
bC = tk.Button(buttons_frame, text="C", command=clearDisplay)
bC.grid(row=0, column=3, sticky="nsew")

win.mainloop()