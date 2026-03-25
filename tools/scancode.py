import keyboard as kb



def callback(event):
    print(event.scan_code)



def main():
    kb.on_release(callback=callback)
    kb.wait("esc")




if __name__ == "__main__":
    main()