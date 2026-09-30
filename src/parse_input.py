import json
import os
from pydantic import BaseModel, model_validator
from typing_extensions import Self

RED_B = "\033[1;38;5;124m"
RESET = "\033[38;5;7m"


class Function_checks(BaseModel):
    prompt: str


class Definition_checks(BaseModel):
    name: str
    description: str
    parameters: dict
    returns: dict

    @model_validator(mode="after")
    def check_parameter(self) -> Self:

        valid_types = ["number", "string", "integer", "float"]
        for key in self.parameters.keys():
            param_dict = self.parameters[key]
            if (list(param_dict.keys())[0] != "type" or
               list(param_dict.values())[0] not in valid_types):
                raise ValueError()
        return self

    @model_validator(mode="after")
    def check_returns(self) -> Self:
        valid_types = ["string", "number"]
        if (list(self.returns.keys())[0] != "type" or
           list(self.returns.values())[0] not in valid_types):
            raise ValueError()
        return self


class JSON_checks(BaseModel):
    input: str
    functions_definition: str
    output: str

    @model_validator(mode="after")
    def check_input_json(self) -> Self:
        try:
            with open(self.functions_definition, "r"):
                pass
        except Exception as e:
            raise ValueError(f"{RED_B}Can't read {self.functions_definition}."
                             f"{RESET}\nMake sure you named it correctly"
                             f" and granted the neccessary permission ({e})")

        if self.input.endswith(".json") is False:
            raise ValueError(f"{RED_B}Can't read {self.input}."
                             f"{RESET}\nThe file isnt a .json")
        else:
            try:
                with open(self.input, "r") as f:
                    json.load(f)

            except Exception as e:
                raise ValueError(f"{RED_B}Can't read {self.input}."
                                 f"{RESET}\n The file can't be"
                                 f"converted to a JSON ({e})")

        with open(self.functions_definition, "r") as f:
            input_dict: list = json.load(f)
            try:
                for i in range(len(input_dict)):
                    Function_checks(**input_dict[i])
            except Exception:
                raise ValueError(f"{RED_B} Format is not respected in "
                                 f"{self.input}{RESET}\n Must be: key = prompt"
                                 f", value = 'str'")
        return self

    @model_validator(mode="after")
    def check_function_json(self) -> Self:
        try:
            with open(self.functions_definition, "r"):
                pass
        except Exception as e:
            raise ValueError(f"{RED_B}Can't read {self.functions_definition}."
                             f"{RESET}\nMake sure you named it correctly"
                             f" and granted the neccessary permission ({e})")

        if self.functions_definition.endswith(".json") is False:
            raise ValueError(f"{RED_B}Can't read {self.functions_definition}."
                             f"{RESET}\nThe file isnt a .json")
        else:
            try:
                with open(self.functions_definition, "r") as f:
                    json.load(f)

            except Exception as e:
                raise ValueError(f"{RED_B}Can't read "
                                 f"{self.functions_definition}."
                                 f"{RESET}\n The file can't be"
                                 f"converted to a JSON ({e})")

        with open(self.functions_definition, "r") as f:
            input_dict: list = json.load(f)
            try:
                for i in range(len(input_dict)):
                    Function_checks(**input_dict[i])
            except Exception:
                raise ValueError(f"{RED_B} Format is not respected in "
                                 f"{self.functions_definition}{RESET}\n Must "
                                 "be:\n"
                                 "{name: str, \ndescription: str, \n"
                                 "parameters : {a: {type: number | str}, "
                                 "b : {type: number | str}},"
                                 "\nreturns: {type: numer | str}}")
        return self

    @model_validator(mode="after")
    def check_output_json(self) -> Self:
        try:
            with open(self.functions_definition, "r"):
                pass
        except FileNotFoundError:
            try:
                os.mkdir(os.path.join("data/", "output"))
            except FileExistsError:
                pass
        if self.output.endswith(".json") is False:
            raise ValueError(f"{RED_B}{self.functions_definition}."
                             f"{RESET}\nThe file isnt a .json")
        return self
