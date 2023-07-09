from basics import run


if __name__ == '__main__':
    while True:
        text = input('shell> ')
        if text.strip() == '': continue
        
        if text == 'quit' or text == 'exit':
            break
                
        res, error = run('<stdin>', text)
        
        if error:
            print(error.as_string())
        elif res:
            if len(res.elements) == 1:
                print(repr(res.elements[0]))
            else:
                print(repr(res))
