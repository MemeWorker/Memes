#Using and calling functions
def addNumbers(num1,num2):
    sum = num1 + num2
    print(sum)
    return
addNumbers(2,3)
addNumbers(9,4)
#Function Parameters
def print_max(a, b):
#Using the if statement to determine whether a is greater than b
    if a > b:
        print(a, " is maximum")
        return
#using the elif statement to determine if a is equal to b
    elif a == b:
        print(a, ' is equal to ', b)
        return
#using the else state if the first two statements are false
    else:
        print(b, ' is maximum')
        return
    return
#In this function were going to test the global statement
number = 45

x = 50
def func():
    global x
    #global statement is used to define outermost block in this case 2
    print('x is ', x)
    x = 2
    print('Now it changed x from 50 to ', x)
    return
func()
print('Value of x is ', x)
