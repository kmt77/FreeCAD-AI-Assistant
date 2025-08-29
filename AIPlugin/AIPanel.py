import FreeCAD, FreeCADGui
from PySide2 import QtWidgets, QtCore
import traceback

# Try importing OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIPanel(QtWidgets.QDockWidget):
    def __init__(self):
        super(AIPanel, self).__init__("AI Code Assistant")
        self.setObjectName("AIPluginDock")

        # Persistent storage for plugin settings
        self.params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/AIPlugin")

        # Load saved API key
        self.api_key = self.params.GetString("OpenAI_API_Key", "")

        # Main widget
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)

        # --- API Key input ---
        self.api_input = QtWidgets.QLineEdit()
        self.api_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_input.setPlaceholderText("Enter your OpenAI API key")
        self.api_input.setText(self.api_key)
        layout.addWidget(self.api_input)

        self.save_key_btn = QtWidgets.QPushButton("Save API Key")
        self.save_key_btn.clicked.connect(self.save_api_key)
        layout.addWidget(self.save_key_btn)

        # --- Prompt input ---
        self.prompt_input = QtWidgets.QTextEdit()
        self.prompt_input.setPlaceholderText("Describe what you want FreeCAD to do...")
        layout.addWidget(self.prompt_input)

        # --- Generate button ---
        self.gen_btn = QtWidgets.QPushButton("Generate Code")
        self.gen_btn.clicked.connect(self.generate_code)
        layout.addWidget(self.gen_btn)

        # --- Code editor ---
        self.code_editor = QtWidgets.QTextEdit()
        self.code_editor.setPlaceholderText("# Generated code will appear here")
        layout.addWidget(self.code_editor)

        # --- Run button ---
        self.run_btn = QtWidgets.QPushButton("Run Code")
        self.run_btn.clicked.connect(self.run_code)
        layout.addWidget(self.run_btn)

        # --- Output console ---
        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setWidget(widget)

    def save_api_key(self):
        self.api_key = self.api_input.text().strip()
        self.params.SetString("OpenAI_API_Key", self.api_key)
        self.output.append("✅ API key saved.")

    def generate_code(self):
        prompt = self.prompt_input.toPlainText().strip()

        if OPENAI_AVAILABLE and self.api_key:
            try:
                openai.api_key = self.api_key
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an assistant that generates Python code for FreeCAD."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300
                )
                code = response["choices"][0]["message"]["content"]
                self.code_editor.setPlainText(code)
                self.output.append("✅ AI generated code.")
            except Exception as e:
                self.output.append(f"❌ AI Error: {e}")
        else:
            # Fallback: demo example code
            self.code_editor.setPlainText(
                f"# Example code for: {prompt}\n"
                "import FreeCAD\n"
                "box = FreeCAD.ActiveDocument.addObject('Part::Box','Box')\n"
                "box.Length=10\nbox.Width=10\nbox.Height=10\n"
                "FreeCAD.ActiveDocument.recompute()"
            )
            self.output.append("ℹ️ AI not available, inserted demo code.")

    def run_code(self):
        code = self.code_editor.toPlainText()
        try:
            exec(code, globals(), locals())
            self.output.append("✅ Code executed successfully.")
        except Exception:
            self.output.append("❌ Error:\n" + traceback.format_exc())


class AIPanelCmd:
    def GetResources(self):
        return {
            "MenuText": "AI Code Assistant",
            "ToolTip": "Open AI-powered code assistant panel"
        }

    def Activated(self):
        self.panel = AIPanel()
        FreeCADGui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, self.panel)
