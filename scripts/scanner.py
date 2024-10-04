from types import ModuleType
import inspect
import os
import sys
import argparse
import importlib


class Scanner:
    scanned = set()
    classes = {}

    BLACKLIST = [
        "has_attribute",
        "__subclasshook__",
        "__class__",
        "__dir__",
        "__doc__",
        "__format__",
        "__getattribute__",
        # "__init__",
        # "__new__",
        "__init_subclass__",
        "__sizeof__",
        "__setattr__",
        "__reduce__",
        "__reduce_ex__",
        "__module__",
        "__getstate__",
        "__delattr__",
        "__ge__",
        "__gt__",
        "__le__",
        "__ne__",
        "__repr__",
        "__str__",
    ]
    WHITELIST = ["__new__", "__init__"]

    def scan_module(self, root_namespace: str, module: ModuleType):
        for element_name in dir(module):
            if element_name.startswith("__"):
                continue

            if root_namespace and root_namespace in module.__name__:
                continue

            if element_name in self.scanned:
                continue

            self.scanned.add(element_name)

            module_root = (
                f"{root_namespace + ('.' if root_namespace else '')}{module.__name__}"
            )
            class_obj = getattr(module, element_name, None)

            if isinstance(class_obj, ModuleType):
                self.scan_module(module_root, class_obj)
                continue

            class_members_all = inspect.getmembers(class_obj)
            dunder_members = [
                m
                for m in class_members_all
                if m[0].startswith("__") and m[0] not in Scanner.BLACKLIST
            ]
            class_members = [
                m
                for m in class_members_all
                if not m[0].startswith("__") and m[0] not in Scanner.BLACKLIST
            ]

            class_methods = []
            class_constants = []
            class_attributes = []
            for m in class_members:
                print(m)
                if callable(m[1]):
                    class_methods.append(m)
                elif inspect.isdatadescriptor(m[1]):
                    class_attributes.append(m)
                else:
                    class_constants.append(m)
            for m in dunder_members:
                class_methods.append(m)

            class_definition = (
                class_obj,
                class_constants,
                class_attributes,
                class_methods,
            )

            self.classes.setdefault(module_root, list())
            self.classes[module_root].append(class_definition)

    def write_pyis(self, file_location):
        for module, classes in reversed(self.classes.items()):
            print(f"Writing pyi for {module}...")
            path = module.replace(".", "/")
            path = os.path.basename(path)
            path = f"{file_location}/{path}.pyi"
            os.makedirs(os.path.dirname(f"{file_location}"), exist_ok=True)
            with open(path, "w") as file:
                file.write("from typing import Final\n\n")
                for (
                    class_obj,
                    class_constants,
                    class_attributes,
                    class_methods,
                ) in classes:
                    print(class_obj.__name__)
                    print(class_methods)
                    print(class_obj.__new__.__text_signature__)
                    print("-----------------------")
                    # init_method = getattr(class_obj, "__new__", None)
                    # try:
                    #     # init_signature = inspect.text(init_method)
                    #     init_signature = init_method.__text_signature__
                    #     print(init_signature)
                    # except ValueError:
                    #     pass

                    # init_method = getattr(class_obj, "__init__", None)
                    # try:
                    #     # init_signature = inspect.text(init_method)
                    #     init_signature = init_method.__text_signature__
                    #     print(init_signature)
                    # except ValueError:
                    #     pass

                    doc = inspect.getdoc(class_obj)

                    file.write(f"class {class_obj.__name__}:\n")
                    if doc:
                        file.write('    """\n')
                        file.write(doc)
                        file.write("\n")
                        file.write('    """\n')

                    for const in class_constants:
                        file.write(
                            f"    {const[0]}: Final[{const[1].__class__.__name__}]\n"
                        )

                    for attr in class_attributes:
                        doc = inspect.getdoc(attr[1])
                        file.write("    @property\n")
                        # file.write(f"    def {attr[0]}(self) -> {attr_type}: ...\n")
                        file.write(f"    def {attr[0]}(self): ...\n")
                        if doc:
                            file.write('    """\n')
                            file.write(doc)
                            file.write('    """\n')

                    # always put new first if present
                    class_methods.sort(
                        reverse=True,
                        key=lambda m: "aaaaa" if m[0] == "__new__" else m[0],
                    )

                    for method in class_methods:
                        if callable(method[1]):
                            try:
                                sig = inspect.signature(method[1])
                                if method[0] == "__new__":
                                    print(sig)

                                if sig.return_annotation is not inspect._empty:
                                    print(f"RETURN  = {sig.return_annotation}")
                                if "self" not in sig.parameters:
                                    file.write("    @staticmethod\n")

                                file.write(
                                    f"    def {method[0]}({', '.join([str(p) for p in sig.parameters.values()])})"
                                )
                            except ValueError:
                                file.write(
                                    f"    def {method[0]}{method[1].__text_signature__}"
                                )
                            if method[0] == "__new__":
                                file.write(f" -> {class_obj.__name__}")
                            file.write(": ...\n")
                            if not method[0].startswith("__"):
                                doc = inspect.getdoc(method[1])
                                if doc:
                                    file.write('    """\n')
                                    file.write(doc)
                                    file.write("\n")
                                    file.write('    """\n')

                    file.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Scan a module and generate .pyi files"
    )
    parser.add_argument(
        "module", help="The name of the module to scan (e.g., zenbt.rs)"
    )
    parser.add_argument("module_dir", help="The directory where the module is located")
    args = parser.parse_args()

    # Add module_dir to sys.path
    sys.path.append(args.module_dir)
    print(args)

    # Dynamically import the module
    try:
        module = importlib.import_module(args.module)
        print(module)
    except ModuleNotFoundError:
        print(f"Module {args.module} not found in {args.module_dir}")
        return

    module_file = module.__file__
    if module_file is None:
        print(
            f"Module {args.module} has no __file__ attribute (might be a built-in or extension module)."
        )
        return

    # Instantiate the scanner and scan the module
    scanner = Scanner()
    scanner.scan_module("", sys.modules[args.module])

    # Write the .pyi file in the same directory as the module
    # module_dir = os.path.dirname(module_file)
    scanner.write_pyis(args.module_dir)


if __name__ == "__main__":
    main()
