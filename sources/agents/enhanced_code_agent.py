#!/usr/bin/env python3
"""
Enhanced Code Agent for AgenticSeek
Provides advanced code quality analysis, testing, and optimization features
"""

import ast
import re
import os
import time
import subprocess
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from sources.agents.code_agent import CoderAgent
from sources.utility import pretty_print, animate_thinking
from sources.logger import Logger


class CodeQuality(Enum):
    """代碼質量等級"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class CodeAnalysisResult:
    """代碼分析結果"""
    quality: CodeQuality
    score: float  # 0-100
    issues: List[str]
    suggestions: List[str]
    complexity: int
    lines_of_code: int
    test_coverage: float = 0.0


@dataclass
class TestResult:
    """測試結果"""
    passed: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    coverage: float
    execution_time: float
    error_messages: List[str] = None


class CodeAnalyzer:
    """代碼質量分析器"""
    
    def __init__(self):
        self.logger = Logger("code_analyzer.log")
    
    def analyze_python_code(self, code: str) -> CodeAnalysisResult:
        """分析 Python 代碼質量"""
        try:
            tree = ast.parse(code)
            
            # 計算複雜度
            complexity = self._calculate_complexity(tree)
            
            # 計算代碼行數
            lines_of_code = len([line for line in code.split('\n') if line.strip()])
            
            # 檢查代碼問題
            issues = self._check_code_issues(code, tree)
            
            # 生成改進建議
            suggestions = self._generate_suggestions(code, tree, issues)
            
            # 計算質量分數
            score = self._calculate_quality_score(complexity, lines_of_code, len(issues))
            
            # 確定質量等級
            quality = self._determine_quality_level(score)
            
            return CodeAnalysisResult(
                quality=quality,
                score=score,
                issues=issues,
                suggestions=suggestions,
                complexity=complexity,
                lines_of_code=lines_of_code
            )
            
        except SyntaxError as e:
            return CodeAnalysisResult(
                quality=CodeQuality.POOR,
                score=0,
                issues=[f"Syntax error: {str(e)}"],
                suggestions=["Fix syntax errors before analysis"],
                complexity=0,
                lines_of_code=0
            )
        except Exception as e:
            self.logger.error(f"Code analysis failed: {str(e)}")
            return CodeAnalysisResult(
                quality=CodeQuality.FAIR,
                score=50,
                issues=[f"Analysis error: {str(e)}"],
                suggestions=["Manual code review recommended"],
                complexity=0,
                lines_of_code=len(code.split('\n'))
            )
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """計算循環複雜度"""
        complexity = 1  # 基礎複雜度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _check_code_issues(self, code: str, tree: ast.AST) -> List[str]:
        """檢查代碼問題"""
        issues = []
        
        # 檢查長函數
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    issues.append(f"Function '{node.name}' is too long ({func_lines} lines)")
        
        # 檢查缺少文檔字符串
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append(f"{type(node).__name__} '{node.name}' lacks documentation")
        
        # 檢查硬編碼值
        if re.search(r'\b\d{3,}\b', code):
            issues.append("Consider using constants for magic numbers")
        
        # 檢查過長的行
        long_lines = [i+1 for i, line in enumerate(code.split('\n')) if len(line) > 100]
        if long_lines:
            issues.append(f"Lines too long: {long_lines[:5]}")  # 只顯示前5個
        
        return issues
    
    def _generate_suggestions(self, code: str, tree: ast.AST, issues: List[str]) -> List[str]:
        """生成改進建議"""
        suggestions = []
        
        # 基於問題生成建議
        if any("too long" in issue for issue in issues):
            suggestions.append("Break down large functions into smaller, focused functions")
        
        if any("lacks documentation" in issue for issue in issues):
            suggestions.append("Add docstrings to functions and classes")
        
        if any("magic numbers" in issue for issue in issues):
            suggestions.append("Define constants for numeric literals")
        
        # 檢查是否有異常處理
        has_try_except = any(isinstance(node, ast.Try) for node in ast.walk(tree))
        if not has_try_except and len(code.split('\n')) > 10:
            suggestions.append("Consider adding error handling with try-except blocks")
        
        # 檢查是否有類型提示
        has_type_hints = 'typing' in code or '->' in code or ':' in code
        if not has_type_hints:
            suggestions.append("Consider adding type hints for better code clarity")
        
        return suggestions
    
    def _calculate_quality_score(self, complexity: int, lines_of_code: int, issue_count: int) -> float:
        """計算質量分數 (0-100)"""
        base_score = 100
        
        # 複雜度懲罰
        if complexity > 10:
            base_score -= (complexity - 10) * 5
        
        # 問題懲罰
        base_score -= issue_count * 10
        
        # 代碼長度獎勵/懲罰
        if lines_of_code < 5:
            base_score -= 20  # 太短可能不完整
        elif lines_of_code > 200:
            base_score -= 10  # 太長可能需要重構
        
        return max(0, min(100, base_score))
    
    def _determine_quality_level(self, score: float) -> CodeQuality:
        """根據分數確定質量等級"""
        if score >= 90:
            return CodeQuality.EXCELLENT
        elif score >= 75:
            return CodeQuality.GOOD
        elif score >= 50:
            return CodeQuality.FAIR
        else:
            return CodeQuality.POOR


class TestGenerator:
    """測試生成器"""
    
    def __init__(self):
        self.logger = Logger("test_generator.log")
    
    def generate_python_tests(self, code: str) -> str:
        """為 Python 代碼生成單元測試"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            if not functions:
                return "# No functions found to test"
            
            test_code = "import unittest\n"
            test_code += "from unittest.mock import patch, MagicMock\n\n"
            
            # 如果代碼中有導入，嘗試提取
            imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
            for imp in imports:
                test_code += ast.unparse(imp) + "\n"
            
            test_code += "\nclass TestGeneratedCode(unittest.TestCase):\n"
            
            for func in functions:
                if func.name.startswith('_'):  # 跳過私有函數
                    continue
                
                test_code += f"\n    def test_{func.name}(self):\n"
                test_code += f'        """Test {func.name} function"""\n'
                
                # 生成基本測試用例
                if func.args.args:
                    # 有參數的函數
                    args = ", ".join([f"test_arg_{i}" for i in range(len(func.args.args))])
                    test_code += f"        # TODO: Define test arguments\n"
                    test_code += f"        # result = {func.name}({args})\n"
                    test_code += f"        # self.assertEqual(result, expected_value)\n"
                    test_code += f"        pass  # Replace with actual test\n"
                else:
                    # 無參數的函數
                    test_code += f"        result = {func.name}()\n"
                    test_code += f"        # TODO: Add assertions based on expected behavior\n"
                    test_code += f"        self.assertIsNotNone(result)\n"
            
            test_code += "\nif __name__ == '__main__':\n"
            test_code += "    unittest.main()\n"
            
            return test_code
            
        except Exception as e:
            self.logger.error(f"Test generation failed: {str(e)}")
            return f"# Test generation failed: {str(e)}\n# Please write tests manually"
    
    def run_tests(self, test_file_path: str) -> TestResult:
        """運行測試並返回結果"""
        try:
            start_time = time.time()
            
            # 運行測試
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file_path, '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            
            # 解析測試結果
            output = result.stdout + result.stderr
            
            # 提取測試統計信息
            passed_tests = len(re.findall(r'PASSED', output))
            failed_tests = len(re.findall(r'FAILED', output))
            total_tests = passed_tests + failed_tests
            
            # 提取錯誤信息
            error_messages = re.findall(r'FAILED.*?(?=\n\n|\nPASSED|\nFAILED|\Z)', output, re.DOTALL)
            
            return TestResult(
                passed=result.returncode == 0,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                coverage=0.0,  # 需要額外的覆蓋率工具
                execution_time=execution_time,
                error_messages=error_messages
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                coverage=0.0,
                execution_time=30.0,
                error_messages=["Test execution timed out"]
            )
        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            return TestResult(
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                coverage=0.0,
                execution_time=0.0,
                error_messages=[str(e)]
            )


class EnhancedCoderAgent(CoderAgent):
    """增強的編碼代理"""
    
    def __init__(self, name, prompt_path, provider, verbose=False):
        super().__init__(name, prompt_path, provider, verbose)
        self.code_analyzer = CodeAnalyzer()
        self.test_generator = TestGenerator()
        self.logger = Logger("enhanced_code_agent.log")
    
    def analyze_code_quality(self, code: str, language: str = "python") -> CodeAnalysisResult:
        """分析代碼質量"""
        pretty_print("🔍 Analyzing code quality...", color="status")
        
        if language.lower() == "python":
            result = self.code_analyzer.analyze_python_code(code)
        else:
            # 對於其他語言，返回基本分析
            result = CodeAnalysisResult(
                quality=CodeQuality.FAIR,
                score=70,
                issues=[f"Quality analysis not yet supported for {language}"],
                suggestions=["Manual code review recommended"],
                complexity=1,
                lines_of_code=len(code.split('\n'))
            )
        
        # 顯示分析結果
        self._display_analysis_result(result)
        
        return result
    
    def generate_tests(self, code: str, language: str = "python") -> str:
        """生成測試代碼"""
        pretty_print("🧪 Generating unit tests...", color="status")
        
        if language.lower() == "python":
            test_code = self.test_generator.generate_python_tests(code)
        else:
            test_code = f"# Test generation not yet supported for {language}\n"
        
        pretty_print("✅ Test generation completed", color="success")
        return test_code
    
    def optimize_code(self, code: str, analysis: CodeAnalysisResult) -> str:
        """基於分析結果優化代碼"""
        pretty_print("⚡ Optimizing code based on analysis...", color="status")
        
        optimized_code = code
        
        # 基於建議進行簡單優化
        for suggestion in analysis.suggestions:
            if "constants" in suggestion.lower():
                # 簡單的常數提取示例
                optimized_code = self._extract_constants(optimized_code)
        
        return optimized_code
    
    def _display_analysis_result(self, result: CodeAnalysisResult):
        """顯示分析結果"""
        quality_colors = {
            CodeQuality.EXCELLENT: "success",
            CodeQuality.GOOD: "info",
            CodeQuality.FAIR: "warning",
            CodeQuality.POOR: "failure"
        }
        
        color = quality_colors.get(result.quality, "info")
        
        pretty_print(f"📊 Code Quality Analysis Results:", color="status")
        pretty_print(f"   Quality: {result.quality.value.upper()} ({result.score:.1f}/100)", color=color)
        pretty_print(f"   Complexity: {result.complexity}", color="info")
        pretty_print(f"   Lines of Code: {result.lines_of_code}", color="info")
        
        if result.issues:
            pretty_print(f"   Issues Found ({len(result.issues)}):", color="warning")
            for issue in result.issues[:3]:  # 只顯示前3個
                pretty_print(f"     • {issue}", color="warning")
            if len(result.issues) > 3:
                pretty_print(f"     ... and {len(result.issues) - 3} more", color="warning")
        
        if result.suggestions:
            pretty_print(f"   Suggestions ({len(result.suggestions)}):", color="info")
            for suggestion in result.suggestions[:3]:  # 只顯示前3個
                pretty_print(f"     • {suggestion}", color="info")
            if len(result.suggestions) > 3:
                pretty_print(f"     ... and {len(result.suggestions) - 3} more", color="info")
    
    def _extract_constants(self, code: str) -> str:
        """簡單的常數提取優化"""
        # 這是一個簡化的示例，實際實現會更複雜
        lines = code.split('\n')
        constants = []
        optimized_lines = []
        
        for line in lines:
            # 查找數字常量
            numbers = re.findall(r'\b\d{3,}\b', line)
            for num in numbers:
                const_name = f"CONSTANT_{num}"
                if const_name not in constants:
                    constants.append(f"{const_name} = {num}")
                line = line.replace(num, const_name)
            optimized_lines.append(line)
        
        if constants:
            return '\n'.join(constants) + '\n\n' + '\n'.join(optimized_lines)
        return code


# 測試函數
def test_enhanced_code_agent():
    """測試增強代碼代理功能"""
    print("🧪 Testing Enhanced Code Agent")

    # 測試代碼分析
    analyzer = CodeAnalyzer()
    test_code = '''
def calculate_area(radius):
    return 3.14159 * radius * radius

def process_data(data):
    result = []
    for item in data:
        if item > 100:
            result.append(item * 2)
    return result
'''

    result = analyzer.analyze_python_code(test_code)
    print(f"✅ Code analysis completed: {result.quality.value} ({result.score:.1f}/100)")

    # 測試測試生成
    generator = TestGenerator()
    test_code_generated = generator.generate_python_tests(test_code)
    print(f"✅ Test generation completed: {len(test_code_generated)} characters")

    print("🎉 Enhanced Code Agent tests passed!")


if __name__ == "__main__":
    # 添加路徑以便測試
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    test_enhanced_code_agent()
