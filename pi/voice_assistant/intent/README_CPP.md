# Intent Parser - C++ Version

This is a C++ port of the intent parser that converts voice-recognized speech into structured commands.

## Building

### Prerequisites
- CMake 3.10+
- C++17 compatible compiler (g++, clang, MSVC)
- macOS, Linux, or Windows

The build system will automatically download `nlohmann/json` library during configuration.

### Build Steps

1. Make the build script executable:
   ```bash
   chmod +x build.sh
   ```

2. Run the build script:
   ```bash
   ./build.sh
   ```

   Or manually:
   ```bash
   mkdir -p build
   cd build
   cmake ..
   cmake --build .
   ```

3. Run tests:
   ```bash
   ./build/intent_handler
   ```

## Usage

### As a Standalone Program

The executable reads from `config.json` in the same directory and parses test cases.

```bash
./build/intent_handler
```

### Including in Your Project

Add to your CMakeLists.txt:

```cmake
add_subdirectory(pi/voice_assistant/intent)

target_link_libraries(your_target intent_handler)
```

Then use in your code:

```cpp
#include "intent_handler.h"

int main() {
    IntentParser parser;
    Intent intent = parser.parse("Turn on the bedroom lights");
    std::cout << intent.toString() << std::endl;
    return 0;
}
```

## API Reference

### IntentAction Enum
- `SET` - Turn on/off a device
- `TOGGLE` - Toggle a device state
- `GET` - Get device status
- `UNKNOWN` - Unknown action

### Intent Struct
```cpp
struct Intent {
    IntentAction action;
    std::optional<std::string> device;
    std::optional<std::string> command;
    std::optional<std::string> raw_speech;
    float confidence;
    
    std::string toString() const;
};
```

### IntentParser Class

#### Constructor
```cpp
IntentParser(const std::string& config_path = "");
```
- `config_path`: Optional path to `config.json`. Defaults to same directory as executable.

#### Methods
```cpp
Intent parse(const std::string& speech);
void addDeviceAlias(const std::string& spoken_name, const std::string& device_id);
```

#### Global Functions
```cpp
IntentParser* getParser();
Intent parseIntent(const std::string& speech);
```

## Configuration

The parser reads from `config.json` (same format as Python version):

```json
{
  "devices": {
    "bedroom light": {
      "primary": "bedroom_light",
      "aliases": ["bedroom", "bedroom lights", "bedroom lamp"]
    }
  },
  "actions": [
    {
      "pattern": "turn\\s+(?:on|up)\\s+(?:the\\s+)?(.+)",
      "action": "set",
      "command": "on",
      "description": "Turn on a device"
    }
  ]
}
```

## Differences from Python Version

1. Uses `std::optional` instead of Python's `Optional`
2. Uses `nlohmann/json` for JSON parsing
3. Pattern matching uses `std::regex`
4. Global parser is a `std::unique_ptr` instead of a module-level variable
5. No type validation on enum conversion (falls back to `UNKNOWN`)

## Build Output

```
build/
├── intent_handler          # Main executable
├── CMakeFiles/             # Build artifacts
└── Makefile                # Or equivalent for your build system
```
