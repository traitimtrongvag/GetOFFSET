# GetOFFSET

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> **Automatic offset mapping tool for Unity IL2CPP dumps** 🚀

When your Unity game updates and all your precious offsets become invalid... 😿

![Cat Coding Meme](https://media.giphy.com/media/JIX9t2j0ZTN9S/giphy.gif)

*Me trying to manually update hundreds of offsets after game update*

## 🌟 Features

- ✨ **Smart Signature Matching**: Maps old offsets to new ones based on method signatures
- 🧹 **Clean Parsing**: Removes compiler-generated noise from signatures  
- 📊 **Progress Tracking**: Beautiful progress bars powered by Rich
- 🎯 **Batch Processing**: Process entire files with hundreds of offsets at once
- 🔍 **Detailed Results**: Shows exactly what was mapped and what wasn't found

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/traitimtrongvag/GetOFFSET.git
cd GetOFFSET

# Install dependencies
pip install rich
```

## 📋 Requirements

- Python 3.6+
- `rich` library for beautiful console output

## 🚀 Usage

### Quick Start

1. **Prepare your files:**
   - `dump_old.cs` - Your old IL2CPP dump file
   - `dump.cs` - Your new IL2CPP dump file  
   - `INPUT.txt` - File containing your old offsets

2. **Run the tool:**
```bash
python3 Main.py
```

3. **Follow the prompts:**
```
Enter old dump file (default dump_old.cs): 
Enter new dump file (default dump.cs):
```

4. **Get your results in `OUTPUT.txt`** ✨

### File Structure
```
GetOFFSET/
│
├── Dump.cs            # New IL2CPP dump
├── Dump_old.cs        # Old IL2CPP dump
├── INPUT/
│   └── INPUT.txt     # Input file containing old offsets
├── OUTPUT/
│   └── OUTPUT.txt    # Generated output with new offsets
├── Main.py            # Main script
├── LICENSE            # License file
└── README.md          # Project documentation
```

## 📝 Input Format

Your `INPUT.txt` can contain offsets in any format:
```cpp
// Example C++ code
void* someFunction = (void*)0x12345678;
int offset = 0xABCDEF00;
// Mixed with other content...
```

## 📤 Output

The tool will:
- Replace all old offsets with new ones in `OUTPUT.txt`
- Show detailed mapping results in console:

```
=== Mapping result ===
0x12345678 -> 0x87654321   [PlayerController] Update()
0xABCDEF00 -> 0x00FEDCBA   [GameManager] Start()
0x11111111 -> NOT FOUND in dump
```

![Success Cat](https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif)

*When all offsets are successfully mapped* 🎉

## 🔧 How It Works

1. **Parse Old Dump**: Extracts class names, method signatures, and their offsets
2. **Parse New Dump**: Creates a mapping from signatures to new offsets  
3. **Smart Matching**: Uses cleaned signatures to find corresponding methods
4. **Batch Replace**: Updates all offsets in your input file

### Signature Cleaning

The tool automatically cleans compiler-generated patterns:
```cpp
// Before cleaning
public void Update() b__123_456; // 0x12345678

// After cleaning  
public void Update() // 0x12345678
```

## 🎭 Why This Tool Exists

Because manually updating offsets is like trying to teach a cat to code...

![Cat Typing](https://media.giphy.com/media/o0vwzuFwCGAFO/giphy.gif)

*Technically possible, but you'll lose your sanity* 😹

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes. Please respect game developers and their terms of service.

---

**Made with ❤️ and lots of ☕**

*P.S: If this tool saved you hours of manual work, consider giving it a ⭐!*

![Happy Cat](https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy.gif)

*That's you after using GetOFFSET* 😸
