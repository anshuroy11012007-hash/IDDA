import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}")

try:
    import vanna
    print(f"✅ Vanna found at: {vanna.__file__}")
except ImportError as e:
    print(f"❌ Vanna not found. Error: {e}")

# Test for specific submodules
modules_to_test = ['vanna.remote', 'vanna.openai', 'vanna.chromadb']
for mod in modules_to_test:
    try:
        __import__(mod)
        print(f"✅ {mod} is working")
    except ImportError as e:
        print(f"⚠️  {mod} FAILED. You are missing dependencies. (Error: {e})")