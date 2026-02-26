cmake_minimum_required(VERSION 3.10)
project(IntentParser)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set policy for FetchContent
cmake_policy(SET CMP0135 NEW)

# Find or download nlohmann/json
include(FetchContent)
FetchContent_Declare(
    json
    URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
    DOWNLOAD_EXTRACT_TIMESTAMP ON
)
FetchContent_MakeAvailable(json)

# Create the executable
add_executable(intent_handler intent_handler.cpp)

# Link against nlohmann/json
target_link_libraries(intent_handler nlohmann_json::nlohmann_json)

# Enable testing
enable_testing()
add_test(NAME IntentParserTest COMMAND intent_handler)
