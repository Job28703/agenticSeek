#!/usr/bin/env python3
"""
Configuration Validator for AgenticSeek
Validates environment variables and configuration files at startup
"""

import os
import configparser
import sys
from typing import List, Dict, Any

class ConfigValidator:
    """Validates configuration and environment variables"""
    
    def __init__(self, config_file: str = 'config.ini'):
        self.config_file = config_file
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_config_file(self) -> bool:
        """Validate config.ini file exists and has required sections"""
        if not os.path.exists(self.config_file):
            self.errors.append(f"Configuration file '{self.config_file}' not found")
            return False
            
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            # Required sections
            required_sections = ['MAIN', 'BROWSER', 'LLM']
            for section in required_sections:
                if section not in config:
                    self.errors.append(f"Missing required section '{section}' in config file")
                    
            # Validate MAIN section
            if 'MAIN' in config:
                main_section = config['MAIN']
                required_main_keys = ['languages', 'speak', 'listen', 'jarvis_personality']
                for key in required_main_keys:
                    if key not in main_section:
                        self.errors.append(f"Missing required key '{key}' in MAIN section")
                        
            # Validate BROWSER section
            if 'BROWSER' in config:
                browser_section = config['BROWSER']
                required_browser_keys = ['stealth_mode']
                for key in required_browser_keys:
                    if key not in browser_section:
                        self.errors.append(f"Missing required key '{key}' in BROWSER section")
                        
            # Validate LLM section
            if 'LLM' in config:
                llm_section = config['LLM']
                required_llm_keys = ['provider']
                for key in required_llm_keys:
                    if key not in llm_section:
                        self.errors.append(f"Missing required key '{key}' in LLM section")
                        
        except Exception as e:
            self.errors.append(f"Error reading config file: {str(e)}")
            return False
            
        return len(self.errors) == 0
        
    def validate_directories(self) -> bool:
        """Validate required directories exist"""
        required_dirs = [
            'sources',
            'prompts',
            '.screenshots'
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                if directory == '.screenshots':
                    # This can be created automatically
                    self.warnings.append(f"Directory '{directory}' will be created automatically")
                else:
                    self.errors.append(f"Required directory '{directory}' not found")
                    
        return len(self.errors) == 0
        
    def validate_environment(self) -> bool:
        """Validate environment variables if needed"""
        # Check for common environment variables that might be needed
        env_vars_to_check = {
            'OPENAI_API_KEY': 'OpenAI API key (if using OpenAI provider)',
            'ANTHROPIC_API_KEY': 'Anthropic API key (if using Anthropic provider)',
        }
        
        for var, description in env_vars_to_check.items():
            if var not in os.environ:
                self.warnings.append(f"Environment variable '{var}' not set ({description})")
                
        return True  # Environment variables are optional warnings
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validations and return results"""
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Run all validations
        config_valid = self.validate_config_file()
        dirs_valid = self.validate_directories()
        env_valid = self.validate_environment()
        
        results['valid'] = config_valid and dirs_valid and env_valid
        results['errors'] = self.errors.copy()
        results['warnings'] = self.warnings.copy()
        
        return results
        
    def print_results(self, results: Dict[str, Any]) -> None:
        """Print validation results in a formatted way"""
        print("\n" + "="*50)
        print("🔍 AgenticSeek Configuration Validation")
        print("="*50)
        
        if results['valid']:
            print("✅ Configuration validation PASSED")
        else:
            print("❌ Configuration validation FAILED")
            
        if results['errors']:
            print("\n🚨 ERRORS:")
            for error in results['errors']:
                print(f"  • {error}")
                
        if results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in results['warnings']:
                print(f"  • {warning}")
                
        print("\n" + "="*50)
        
def validate_startup_config() -> bool:
    """Quick validation function for startup"""
    validator = ConfigValidator()
    results = validator.validate_all()
    validator.print_results(results)
    
    if not results['valid']:
        print("\n❌ Cannot start AgenticSeek due to configuration errors.")
        print("Please fix the above errors and try again.")
        return False
        
    if results['warnings']:
        print("\n⚠️  Starting with warnings. Some features may not work properly.")
        
    return True
    
if __name__ == "__main__":
    # Run validation when script is executed directly
    if not validate_startup_config():
        sys.exit(1)
    print("\n✅ Configuration validation completed successfully!")