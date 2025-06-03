import platform, os
import asyncio
import ast
import re

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent, executorResult
from sources.tools.C_Interpreter import CInterpreter
from sources.tools.GoInterpreter import GoInterpreter
from sources.tools.PyInterpreter import PyInterpreter
from sources.tools.BashInterpreter import BashInterpreter
from sources.tools.JavaInterpreter import JavaInterpreter
from sources.tools.fileFinder import FileFinder
from sources.logger import Logger
from sources.memory import Memory

class CoderAgent(Agent):
    """
    The code agent is an agent that can write and execute code.
    """
    def __init__(self, name, prompt_path, provider, verbose=False):
        super().__init__(name, prompt_path, provider, verbose, None)
        self.tools = {
            "bash": BashInterpreter(),
            "python": PyInterpreter(),
            "c": CInterpreter(),
            "go": GoInterpreter(),
            "java": JavaInterpreter(),
            "file_finder": FileFinder()
        }
        self.work_dir = self.tools["file_finder"].get_work_dir()
        self.role = "code"
        self.type = "code_agent"
        self.logger = Logger("code_agent.log")
        self.memory = Memory(self.load_prompt(prompt_path),
                        recover_last_session=False, # session recovery in handled by the interaction class
                        memory_compression=False,
                        model_provider=provider.get_model_name())
    
    def add_sys_info_prompt(self, prompt):
        """Add system information to the prompt."""
        info = f"System Info:\n" \
               f"OS: {platform.system()} {platform.release()}\n" \
               f"Python Version: {platform.python_version()}\n" \
               f"\nYou must save file at root directory: {self.work_dir}"
        return f"{prompt}\n\n{info}"

    def analyze_code_quality(self, code: str, language: str = "python") -> dict:
        """
        Analyze code quality and provide feedback.

        Args:
            code: The code to analyze
            language: Programming language (default: python)

        Returns:
            dict: Analysis results with score, issues, and suggestions
        """
        if language.lower() != "python":
            return {
                "score": 70,
                "issues": [f"Quality analysis not yet supported for {language}"],
                "suggestions": ["Manual code review recommended"],
                "functions_found": 0
            }

        try:
            # Parse the code
            tree = ast.parse(code)

            # Analyze various aspects
            issues = []
            suggestions = []

            # Check for missing docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                    issues.append(f"Function '{node.name}' lacks documentation")

            # Check for magic numbers
            if re.search(r'\b\d{3,}\b', code):
                issues.append("Found magic numbers (consider using constants)")
                suggestions.append("Replace magic numbers with named constants")

            # Check line length
            long_lines = [i+1 for i, line in enumerate(code.split('\n')) if len(line) > 100]
            if long_lines:
                issues.append(f"Lines too long: {long_lines[:3]}")
                suggestions.append("Break long lines for better readability")

            # Count functions
            functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])

            # Calculate score
            base_score = 100
            base_score -= len(issues) * 10
            score = max(0, min(100, base_score))

            # Add general suggestions
            if not suggestions:
                suggestions.append("Code looks good! Consider adding type hints for better clarity")

            return {
                "score": score,
                "issues": issues,
                "suggestions": suggestions,
                "functions_found": functions
            }

        except SyntaxError as e:
            return {
                "score": 0,
                "issues": [f"Syntax error: {str(e)}"],
                "suggestions": ["Fix syntax errors before analysis"],
                "functions_found": 0
            }
        except Exception as e:
            self.logger.error(f"Code analysis failed: {str(e)}")
            return {
                "score": 50,
                "issues": [f"Analysis error: {str(e)}"],
                "suggestions": ["Manual code review recommended"],
                "functions_found": 0
            }

    def generate_basic_tests(self, code: str) -> str:
        """
        Generate basic unit tests for the code.

        Args:
            code: The code to generate tests for

        Returns:
            str: Generated test code
        """
        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')]

            if not functions:
                return "# No functions found to test\n"

            test_code = "import unittest\n\n"
            test_code += "class TestGeneratedCode(unittest.TestCase):\n"

            for func_name in functions:
                test_code += f"\n    def test_{func_name}(self):\n"
                test_code += f'        """Test {func_name} function"""\n'
                test_code += f"        # TODO: Add test for {func_name}\n"
                test_code += f"        pass\n"

            test_code += "\nif __name__ == '__main__':\n"
            test_code += "    unittest.main()\n"

            return test_code

        except Exception as e:
            self.logger.error(f"Test generation failed: {str(e)}")
            return f"# Test generation failed: {str(e)}\n"

    async def process(self, prompt, speech_module) -> str:
        answer = ""
        attempt = 0
        max_attempts = 5
        prompt = self.add_sys_info_prompt(prompt)
        self.memory.push('user', prompt)
        clarify_trigger = "REQUEST_CLARIFICATION"

        while attempt < max_attempts and not self.stop:
            print("Stopped?", self.stop)
            animate_thinking("Thinking...", color="status")
            await self.wait_message(speech_module)
            answer, reasoning = await self.llm_request()
            self.last_reasoning = reasoning
            if clarify_trigger in answer:
                self.last_answer = answer
                await asyncio.sleep(0)
                return answer, reasoning
            if not "```" in answer:
                self.last_answer = answer
                await asyncio.sleep(0)
                break
            self.show_answer()
            animate_thinking("Executing code...", color="status")
            self.status_message = "Executing code..."
            self.logger.info(f"Attempt {attempt + 1}:\n{answer}")
            exec_success, feedback = self.execute_modules(answer)
            self.logger.info(f"Execution result: {exec_success}")
            answer = self.remove_blocks(answer)
            self.last_answer = answer
            await asyncio.sleep(0)
            if exec_success and self.get_last_tool_type() != "bash":
                # 代碼執行成功，進行質量分析
                self._analyze_and_provide_feedback(answer)
                break
            pretty_print(f"Execution failure:\n{feedback}", color="failure")
            pretty_print("Correcting code...", color="status")
            self.status_message = "Correcting code..."
            attempt += 1
        self.status_message = "Ready"
        if attempt == max_attempts:
            return "I'm sorry, I couldn't find a solution to your problem. How would you like me to proceed ?", reasoning
        self.last_answer = answer
        return answer, reasoning

    def _analyze_and_provide_feedback(self, answer: str):
        """
        Analyze code blocks in the answer and provide quality feedback.

        Args:
            answer: The agent's answer containing code blocks
        """
        # Extract code blocks from the answer
        code_blocks = re.findall(r'```python\n(.*?)\n```', answer, re.DOTALL)

        for i, code_block in enumerate(code_blocks):
            if len(code_block.strip()) > 20:  # Only analyze substantial code
                pretty_print(f"🔍 Analyzing code quality for block {i+1}...", color="status")

                analysis = self.analyze_code_quality(code_block, "python")

                # Display analysis results
                if analysis["score"] >= 80:
                    color = "success"
                elif analysis["score"] >= 60:
                    color = "warning"
                else:
                    color = "failure"

                pretty_print(f"📊 Code Quality Score: {analysis['score']}/100", color=color)

                if analysis["issues"]:
                    pretty_print("⚠️  Issues found:", color="warning")
                    for issue in analysis["issues"][:3]:  # Show top 3 issues
                        pretty_print(f"   • {issue}", color="warning")

                if analysis["suggestions"]:
                    pretty_print("💡 Suggestions:", color="info")
                    for suggestion in analysis["suggestions"][:2]:  # Show top 2 suggestions
                        pretty_print(f"   • {suggestion}", color="info")

                # Offer to generate tests
                if analysis["functions_found"] > 0:
                    pretty_print(f"🧪 Found {analysis['functions_found']} function(s). Consider adding unit tests.", color="info")

if __name__ == "__main__":
    pass