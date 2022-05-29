# Hexful
### A Simple Hex Preprocessor written in python

#### I suggest that you do not use this, it is probably full of bugs, and is also slow



## Features
- **Directives**:   
    Directives allow you to perform various tasks automatically, such as importing hex files, or repeating sequences of bytes, etc.
- **Comments**:   
    Yes, you can actually comment your hex now

- **Inline ASCII Support**:   
    No more visiting rapidtables.com while writing hex, you can directly embed plaintext

- **Variables**:   
    Pretty self-explanatory


## Example
```ex
# repeat the content of the statement x times
@repeat 10 

    /Hello, World! / # text surrounded with '/' is replaced with it's hex equivalent

@end # Some directives require to be terminated, others dont


@include ./myepicfile.hxf # Inline other hxf files

# Declare variables using @declare
@declare my_name /John Doe/


# You can use variables by surrounding it's name with braces
/Welcome to Hexful, / {my_name}

# and of course, there is raw hex support (case-insensitive)

01234567890ABCDEF

a1 b2 c3 d4 e5 f6

@repeat 256
    00
@end

```
    