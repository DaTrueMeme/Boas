import os
from boas.scripts.operations import *
from boas.scripts.functions import *
from colorist import ColorRGB

class BoasInterpreter:
    def __init__(self) -> None:
        self.settings = grabData("settings")

        self.force_stop = False
        self.tab_spaces = self.settings["tab_spaces"]
        self.indent = 0

        self.append_function = False
        self.function = None
        self.func_name = None

        self.code_classes = grabData("modules")

        self.colors = {
            "red": ColorRGB(255, 0, 0),
            "green": ColorRGB(0, 255, 0),
            "blue": ColorRGB(0, 0, 255),
            "yellow": ColorRGB(255, 255, 0)
        }

        self.variables = {}
        self.functions = {}
        self.temp_variables = []

        self.file_path = None
        self.code = None

    def checkSyntax(self, correct_string, given_string, message):
        if correct_string != given_string:
            self.throwError(message, self.file_path, self.code, "SyntaxError")
            return False
        return True

    def throwError(self, message: str, error_type: str, target=None):
        RED = self.colors["red"]

        self.sendConsole(f'')
        self.sendConsole(f"{RED}Error found in file: {self.file_path}{RED.OFF}", "ERROR")
        self.sendConsole(f"⤷ {self.line}", "ERROR")

        if target != None:
            output = ""
            word = ""

            for i in self.line:
                if not i.isalpha():
                    if word == target:
                        output = output[0:len(output) - len(target)]
                        for i in target:
                            output += "↑"

                    word = ""
                else:
                    word += i
                output += " "
            self.sendConsole(f"  {output}", "ERROR")

        self.sendConsole(f"{RED}{error_type}: {message}{RED.OFF}", "ERROR")
        self.force_stop = True
        self.clearTempVariables()

    def sendConsole(self, string: str, level="INFO"):
        level_colors = {
            "INFO": ColorRGB(0, 0, 255),
            "ERROR": ColorRGB(255, 0, 0),
            "CODE": ColorRGB(0, 255, 255)
        }
        if level not in level_colors:
            self.throwError(f"Level '{level}' is not valid for sendConsole.")
            return
        
        symbols = grabData("symbols")["emojis" if self.settings["use_emojis"] else "text"]
        symbol = symbols[level]

        color = level_colors[level]
        boas_color = ColorRGB(0, 255, 0)
        print(f'{boas_color}BOAS{boas_color.OFF}   {color}{symbol}{color.OFF} {string}')

    def clearTempVariables(self):
        remove_variables = []
        for variable in self.variables:
            if self.temp_variables.__contains__(variable):
                remove_variables.append(variable)
                
        for variable in remove_variables:
            del self.variables[variable]
        self.temp_variables = []

    def variableCheck(self, value):
        if value[0:2] == 'v"':
            return self.formatVariableString(value)

        if value[0] == '"':
            if self.checkSyntax(value[len(value) - 1], '"', message="String not closed."):
                return value[1:len(value) - 1]
            else:
                return
        elif value.isdigit():
            return value
        else:
            variable = value
            if variable in self.variables:
                return self.variables[variable]
            else:
                self.throwError(f"Variable '{variable}' not defined.", self.file_path, self.code, "NameError", target=variable)
                return

    def formatVariableString(self, string):
        if not string[0:2] == 'v"':
            self.throwError(f"String '{string}' is not a variable string.", None, string, "SyntaxError")
            return
        
        vstring = False
        variable = ""
        output = ""
        for char in string:
            if vstring:
                if char == "}":
                    vstring = False
                    output += self.variables[variable]
                variable += char
                continue

            elif char == "{":
                variable = ""
                vstring = True
                continue
            output += char
        return output[2:-1]

    def fileExecute(self, file_path):
        if not file_path.endswith(".boas"):
            self.throwError(f"File '{file_path}' is not of type .boas", "FileTypeError")
            return
        
        if not os.path.exists(file_path):
            self.throwError(f"File '{file_path}' not found.", "FileExistsError")
            return

        self.functions = {}
        self.variables = {}
        self.temp_variables = []
        self.append_function = False
        self.function = None
        self.func_name = None
        self.indent = 0
        
        with open(file_path, "r") as f:
            for line in f:
                self.execute(line.removesuffix("\n"), file_path)

    def execute(self, code, file_path="None"):
        self.file_path = file_path
        self.code = code
        self.settings = grabData("settings")

        if self.append_function:
            if self.code[0:self.indent] == (" " * self.indent):
                if self.code[self.indent + 1] == " ":
                    return

                if self.code[self.indent:].split(".")[0] == "func":
                    self.throwError(f"Cannot have nested functions.", "SyntaxError", target="func")
                    return

                self.function.append(self.code[self.indent:])
                return
            else:
                self.append_function = False
                self.functions[self.func_name] = self.function
        
        parts = self.code.split('.')
        code_class = parts[0]

        if self.code == "" or self.code[0] == "\\":
            return

        if not self.code_classes.__contains__(code_class):
            self.throwError(f"Module '{code_class}' not defined.", "NameError", target=code_class)
            return

        if code_class == "import":
            func_name = parts[1].split("(")[0]

            if self.functions.__contains__(func_name):
                self.throwError(f"Function '{func_name}' already defined.", "NameError", target=func_name)
                return

            self.file_path = parts[1].removeprefix(f"{func_name}(")[:-1]
        
            if not os.path.exists(f'{self.file_path}.boas'):
                self.throwError(f"File '{self.file_path}.boas' not found.", "FileExistsError", target=self.file_path)
                return

            with open(f'{self.file_path}.boas', 'r') as f:
                add = False
                function = []
                for line in f:
                    if add:
                        if line[0:self.tab_spaces] != " " * self.tab_spaces:
                            break
                        function.append(line[self.tab_spaces:].removesuffix("\n"))

                    if line[0:len(func_name) + 5] == f'func.{func_name}':
                        func_args = line[len(func_name) + 6:-3].split(", ")

                        if func_args[0] == '':
                            func_args.remove('')

                        function.append(func_args)

                        add = True

                if not add:
                    self.throwError(f"Function '{func_name}' not defined.", "NameError", target=func_name)
                    return

            self.functions[func_name] = function

        if code_class == "call":
            func_name = parts[1].split("(")[0]
            arg_seg = parts[1][len(func_name) + 1:-1]
            args = arg_seg.split(", ")
            args = [] if args[0] == '' else args

            if not self.functions.__contains__(func_name):
                self.throwError(f"Function '{func_name}' not defined.", "NameError", target=func_name)
                return

            def_args = True
            for code_line in self.functions[func_name]:
                if def_args:
                    index = 0

                    if len(args) < len(code_line) or len(args) > len(code_line):
                        self.throwError(f"Function '{func_name}' takes {len(code_line)} argument(s), {len(args)} were given", "TypeError", target=arg_seg)
                        return

                    for carg in args:
                        carg = self.variableCheck(carg)
                        self.variables[code_line[index]] = carg
                        self.temp_variables.append(code_line[index])
                        index += 1

                    def_args = False
                    continue
                self.execute(code_line, file_path=self.file_path)
            
            self.clearTempVariables()

        if code_class == "func":
            func_name = parts[1].split("(")[0]
            func_args = parts[1][len(func_name) + 1:-2].split(", ")

            if func_args[0] == '':
                func_args.remove('')
            
            if self.functions.__contains__(func_name):
                self.throwError(f"Function '{func_name}' already defined.", "NameError", target=func_name)
                return

            self.append_function = True
            self.function = [func_args]
            self.func_name = func_name
            self.indent += self.tab_spaces

        if code_class == "var":
            oper_data = parts[1].split(" ")
            operation = oper_data[1]

            length = len(oper_data) if oper_data[len(oper_data)-1] != "" else len(oper_data) - 1
            if not self.checkSyntax("3", str(length), message="Invalid number of arguments."):
                return

            variable_name = oper_data[0]
            variable_value = oper_data[2]

            if operation == "=":
                self.variables[variable_name] = self.variableCheck(variable_value)
            else:
                value = str(math(int(self.variables[variable_name]), int(variable_value), operation, self.throwError, [self.file_path, self.code]))
                self.variables[variable_name] = value

        if code_class == "console":
            sub_parts = parts[1].split('(')

            if not self.code_classes[code_class].__contains__(sub_parts[0]):
                self.throwError(f"Subclass '{sub_parts[0]}' from module '{code_class}' not defined.", "NameError", target=sub_parts[0])
                return

            if sub_parts[0] == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')

            if sub_parts[0] == "send":
                full_msg = sub_parts[1]
                msg_length = len(full_msg)

                message = ""
                message = self.variableCheck(full_msg[:-1])

                self.sendConsole(message, "CODE")

BoasInterpreter = BoasInterpreter()
