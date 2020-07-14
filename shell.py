import wow

while True: 
    text = input('Wow > ')
    result, err = wow.run('<stdin>', text)

    if err: print(err.as_string())
    else: print(result)