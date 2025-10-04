# analysis/__init__.py
import importlib
import os

from analysis.base_analyzer import BaseAnalyzer


def load_analyzers():
    analyzers = []
    for file in os.listdir('analysis'):
        if file.endswith('.py') and file not in ['__init__.py', 'base_analyzer.py']:
            module_name = file[:-3]
            module = importlib.import_module(f'analysis.{module_name}')
            for attr in dir(module):
                cls = getattr(module, attr)
                if isinstance(cls, type) and issubclass(cls, BaseAnalyzer) and cls != BaseAnalyzer:
                    analyzers.append(cls())
    return analyzers