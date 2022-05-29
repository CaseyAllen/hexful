import sys






def getArgs():
    argObj = {
        "argList": []
    }
    args = sys.argv[1:]

    nextTag=None
    for arg in args:
        if nextTag:
            argObj[nextTag] = arg
            nextTag = None
            continue

        if arg.startswith("--"):
            nextTag = arg[2:]
            if nextTag == "argList": raise Exception("Illegal argument 'argList'")
        elif arg.startswith("-"):
            # Boolean Argument
            name = arg[1:]
            if name == "argList": raise Exception("Illegal argument 'argList'")
            argObj[name] = True
        else:
            argObj["argList"].append(arg)
    return argObj



