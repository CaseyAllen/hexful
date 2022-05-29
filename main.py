
import os
import sys
from typing import List

DIRECTIVES = [
    "include",
    "repeat",
    "declare"
]

UNCLOSED_DIRECTIVES = [
    "include",
    "declare"
]


# The Declarations made globally using the @declare directive
GLOBAL_DECLARATIONS = {

}


def parseHexChar(char: str):
    char = char.lower()
    if ord(char) >= 48 and ord(char) <= 57:  # within decimal range
        return ord(char)-48
    elif ord(char) >= 97 and ord(char) <= 102:  # within letter range
        return ord(char)-87
    else:
        raise Exception(f"Unable to parse character '{char}'")


class Directive:
    name: str
    args: str
    body: List[str]

    def __init__(self) -> None:
        self.body = []

    def resolve(self):
        value = processDirectives(self.body)
        args = self.args.split(" ")
        # Apply transformations to the data
        if self.name == "repeat":
            times = int(args[0])
            initialValue = value.copy()
            newValue = []
            for _ in range(times):
                newValue.extend(initialValue)
            value = newValue
        elif self.name == "include":
            filepath = args[0]
            data = getLines(getAbsPath(filepath))
            value = data
        elif self.name == "declare":
            decName = args[0]
            content = " ".join(args[1:])
            GLOBAL_DECLARATIONS[decName] = content
        else:
            raise Exception(f"Unknown directive '{self.name}'")
        complete = ""
        for v in value:
            complete += v
        return complete

    def __repr__(self) -> str:
        return f"""
        Directive {self.name} ({self.args})
        {self.body}
        """


def getAbsPath(relative: str) -> str:
    targetPath = os.path.abspath(relative)
    return targetPath


def trimLine(line: str) -> str:
    line = line.strip()
    if not line or line.isspace():
        return None
    elif line.startswith("@"):
        # Embedded Instructions, i.e repeat
        return line
    goodText = ""
    isSubBlock = False
    for char in line:
        if char == "#":
            # comments
            break
        if char == "/":
            isSubBlock = not isSubBlock
        elif char.isspace():
            if not isSubBlock:
                continue
        goodText += char
    return goodText


def trimLines(file: List[str]) -> List[str]:
    """
    Remove the comments and reduntant whitespace from an array
    """
    fileLines = []
    for line in file:
        trimmed = trimLine(line)
        if trimmed:
            fileLines.append(trimmed)
    return fileLines


def makeSubstitutions(string: str):
    """
    Substitute Literals and Variables
    """

    substituted = ""
    nextVarName = None
    for char in string:
        if char == "{":
            nextVarName = ""
            continue
        elif char == "}":
            substituted += GLOBAL_DECLARATIONS[nextVarName]
            nextVarName = None
            continue
        if nextVarName != None:
            nextVarName += char
        else:
            substituted += char
    string = trimLine(substituted)
    slashCount = string.count("/")
    if slashCount == 0:
        return string
    elif slashCount % 2 != 0:
        raise Exception("Unexpected /")

    hexValues = ""
    subMode = False
    for char in string:
        if char == "/":
            subMode = not subMode
            continue
        if subMode:
            hexValues += hex(ord(char))[2:]
        else:
            hexValues += char
    return hexValues


def processDirectives(file: List[str]) -> List[str]:
    """
    Recursively process directives, tags are matched with end tags
    unless explicitly declared as an Unclosed Directive

    1. Find the tag
    2. Find the end tag
    3. Recursively resolve the contents
    4. resolve the tag
    """
    resolved = []

    nestLevel = 0

    current: Directive = None

    for line in file:
        if line == "@end":
            nestLevel -= 1
            if nestLevel == 0:
                # nestlevel of 0 means that we have gone back to the root, aka. resolve recursively
                resolved.append(current.resolve())
                current = None
            if current:
                current.body.append(line)

        elif line.startswith("@") and not current:

            direc = Directive()
            direc.name = line.split(" ")[0][1:].lower()
            direc.args = line.split(" ", 1)[1]
            if not direc.name in DIRECTIVES:
                raise Exception(f"Unknown directive '{direc.name}'")
            if not direc.name in UNCLOSED_DIRECTIVES:
                current = direc
                nestLevel += 1
            else:
                res = direc.resolve()
                if res:
                    resolved.append(res)

        elif current:
            if line.startswith("@"):
                nestLevel += 1
            current.body.append(line)
        else:
            resolved.append(line)

        if nestLevel < 0:
            raise Exception("Unexpected @end")

    return resolved


def processConversions(file: List[str]) -> List[str]:
    """
    Convert Plaintext wrapped in forward slashes into their hex equivalent
    """
    newFile = []
    for line in file:
        newValue = makeSubstitutions(line)
        newFile.append(newValue)
    return newFile


def convBytes(data: List[str]) -> bytearray:
    _bytes: bytearray = []
    for i, l in enumerate("".join(data)):
        # grow the array to prevent indexerror
        if i % 2 == 0:
            _bytes.append(0)
        index = i//2
        shift = (1-(i % 2)) * 4
        value = parseHexChar(l)

        _bytes[index] += value << shift
    return _bytes


def getLines(filepath: str) -> bytearray:
    """
    Resolve the raw byte values of a file
    """
    rawFile = open(filepath, "r")
    fileLines = [i for i in rawFile]
    fileLines = trimLines(fileLines)

    fileLines = processDirectives(fileLines)

    fileLines = processConversions(fileLines)

    return fileLines


target = getAbsPath(sys.argv[1])

_bytes = convBytes(getLines(target))

# write the bytes to the output file

defaultOutPath = "./out.hex"


outAbsPath = getAbsPath(defaultOutPath)

targetWrite = open(outAbsPath, "wb")

targetWrite.write(bytes(_bytes))
