import sys
import inspect
import shutil
import os
from antlr4 import *
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "build"))

from build.TyCLexer import TyCLexer
class Tokenizer:
    """Lexer wrapper for testing"""

    def __init__(self, source_code: str):
        self.source_code = source_code

    def get_tokens_as_string(self) -> str:
        """Get tokens as comma-separated string"""
        input_stream = InputStream(self.source_code)
        lexer = TyCLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()

        tokens = []
        for token in token_stream.tokens:
            if token.type != -1:  # EOF
                token_name = lexer.symbolicNames[token.type]
                token_text = token.text if token.text else ""
                tokens.append(f"{token_text}")

        tokens.append("EOF")
        return ",".join(tokens)


from build.TyCParser import TyCParser
from src.utils.error_listener import NewErrorListener
class Parser:
    """Parser wrapper for testing"""

    def __init__(self, source_code: str):
        self.source_code = source_code

    def parse(self) -> str:
        """Parse source code and return result"""
        input_stream = InputStream(self.source_code)
        lexer = TyCLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = TyCParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(NewErrorListener.INSTANCE)

        try:
            tree = parser.program()
            return "success"
        except Exception as e:
            return str(e)
from src.astgen.ast_generation import ASTGeneration
class ASTGenerator:
    """Class to generate AST from TyC source code."""

    def __init__(self, input_string: str):
        self.input_string = input_string
        self.input_stream = InputStream(input_string)
        self.lexer = TyCLexer(self.input_stream)
        self.token_stream = CommonTokenStream(self.lexer)
        self.parser = TyCParser(self.token_stream)
        self.parser.removeErrorListeners()
        self.parser.addErrorListener(NewErrorListener.INSTANCE)
        self.ast_generator = ASTGeneration()

    def generate(self):
        parse_tree = self.parser.program()
        ast = self.ast_generator.visit(parse_tree)
        return ast
    
from src.semantics.static_checker import StaticChecker
from src.semantics.static_error import StaticError
class Checker:
    """Class to perform static checking on the AST."""

    def __init__(self, source=None, ast=None):
        self.source = source
        self.ast = ast
        self.checker = StaticChecker()

    def check_from_ast(self):
        """Perform static checking on the AST."""
        try:
            self.checker.check_program(self.ast)
            return "Static checking passed"
        except Exception as e:
            return str(e)

    def check_from_source(self):
        """Perform static checking on the source code."""
        try:
            ast_gen = ASTGenerator(self.source)
            self.ast = ast_gen.generate()
            if isinstance(self.ast, str):  # If AST generation failed
                return self.ast
            self.checker.check_program(self.ast)
            return "Static checking passed"
        except StaticError as e:
            return str(e)
        
from src.codegen.codegen import CodeGenerator as CodeGen
class CodeGenerator:
    """Class to generate and run code from AST."""

    def __init__(self):
        self.codegen = CodeGen()
        self.runtime_dir = os.path.join("./", "src", "runtime")

    def check_from_ast(self):
        """Perform static checking on the AST."""
        try:
            self.checker.check_program(self.ast)
            return "Static checking passed"
        except Exception as e:
            return str(e)
        
    def _cleanup_generated_files(self):
        """Clean up previously generated .j and .class files (except io.class)."""
        import glob

        # Clean up .j files (except io.j if exists)
        for j_file in glob.glob(os.path.join(self.runtime_dir, "*.j")):
            try:
                os.remove(j_file)
            except OSError:
                pass
        # Clean up .class files (except io.class)
        for class_file in glob.glob(os.path.join(self.runtime_dir, "*.class")):
            if os.path.basename(class_file) != "io.class":
                try:
                    os.remove(class_file)
                except OSError:
                    pass

    def generate_and_run(self, ast, input_data=""):
        """
        Generate code from AST and run it, return output.

        Args:
            ast: AST node (Program)
            input_data: Optional input string for program (for readInt, readFloat, etc.)

        Returns:
            Output string from program execution
        """
        # try:
        # Clean up old generated files first
        self._cleanup_generated_files()

        ast = ASTGenerator(ast)
        ast = ast.generate()


        # Ensure runtime io.class exists when running tests directly via pytest.
        io_java = os.path.join(self.runtime_dir, "io.java")
        io_class = os.path.join(self.runtime_dir, "io.class")
        if os.path.exists(io_java) and not os.path.exists(io_class):
            import subprocess

            compile_result = subprocess.run(
                ["javac", "io.java"],
                cwd=self.runtime_dir,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if compile_result.returncode != 0:
                return f"Runtime compile error: {compile_result.stderr}"

        # Change to runtime directory and generate code from AST
        original_dir = os.getcwd()
        os.chdir(self.runtime_dir)
        try:
            self.codegen.visit(ast)
        finally:
            os.chdir(original_dir)

        # Find all generated .j files
        import glob

        j_files = glob.glob(os.path.join(self.runtime_dir, "*.j"))



        # # =========================
        # # LẤY TÊN TEST
        # # =========================
        # def _get_test_name():
        #     for frame in inspect.stack():
        #         if frame.function.startswith("test_"):
        #             return frame.function
        #     return "unknown"

        # test_name = _get_test_name()

        # # =========================
        # # TẠO THƯ MỤC ĐÍCH
        # # =========================
        # dst_dir = os.path.join(self.runtime_dir, "submitted", test_name)
        # os.makedirs(dst_dir, exist_ok=True)

        # # =========================
        # # COPY TẤT CẢ FILE .j
        # # =========================
        # for j_file in j_files:
        #     file_name = os.path.basename(j_file)
        #     dst_file = os.path.join(dst_dir, file_name)
        #     shutil.copy(j_file, dst_file)




        if not j_files:
            return "Error: No .j files generated"

        # Assemble all .j files to .class
        try:
            import subprocess

            for j_file in j_files:
                result = subprocess.run(
                    ["java", "-jar", "jasmin.jar", os.path.basename(j_file)],
                    cwd=self.runtime_dir,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    return f"Assembly error for {os.path.basename(j_file)}: {result.stderr}"

            # Find the class with main method (TyC class)
            class_files = glob.glob(os.path.join(self.runtime_dir, "TyC.class"))
            if not class_files:
                return "Error: TyC.class not found"

            # Run program
            result = subprocess.run(
                ["java", "-cp", self.runtime_dir, "TyC"],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return f"Runtime error: {result.stderr}"

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            return "Timeout"
        except FileNotFoundError:
            return "Java not found"

        # except Exception as e:
        #     return f"Code generation error: {str(e)}"