from basics import run


if __name__ == '__main__':
    while True:
        text = input('shell> ')
        
        if text == 'quit' or text == 'exit':
            break
        
        res, error = run('<stdin>', text)
        
        if error:
            print(error.as_string())
        else:
            print(res)
