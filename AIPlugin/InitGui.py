import FreeCADGui
from AIPanel import AIPanelCmd

class AIWorkbench:
    def __init__(self):
        self.__class__.MenuText = "AI Code Assistant"
        self.__class__.ToolTip = "AI-powered FreeCAD Python code generator"

    def Initialize(self):
        FreeCADGui.addCommand("OpenAIPanel", AIPanelCmd())

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(AIWorkbench())
