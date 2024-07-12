def read_message(filename='message.txt'):
    try:
        with open(filename, 'r') as file:
            message = file.read()
        return message
    except FileNotFoundError:
        return "No message found."

if __name__ == "__main__":
    message = read_message()
    print(f"Message received: '{message}'")
