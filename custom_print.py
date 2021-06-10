MIN_PRINT_LEVEL=0

f=open("log.txt","a")

# reduce clutter by defining print levels
def custom_print(data,level):
    if(level>=MIN_PRINT_LEVEL):
        print(data)
        f.write(str(data)+"\n")