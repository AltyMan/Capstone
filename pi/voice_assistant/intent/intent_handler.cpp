#include <string>
#include <vector>
#include <map>
#include <optional>
#include <regex>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <memory>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
namespace fs = std::filesystem;

// Enum for intent actions
enum class IntentAction {
    SET,
    TOGGLE,
    GET,
    UNKNOWN
};

std::string intentActionToString(IntentAction action) {
    switch (action) {
        case IntentAction::SET:
            return "set";
        case IntentAction::TOGGLE:
            return "toggle";
        case IntentAction::GET:
            return "get";
        case IntentAction::UNKNOWN:
            return "unknown";
        default:
            return "unknown";
    }
}

IntentAction stringToIntentAction(const std::string& str) {
    if (str == "set") return IntentAction::SET;
    if (str == "toggle") return IntentAction::TOGGLE;
    if (str == "get") return IntentAction::GET;
    return IntentAction::UNKNOWN;
}

// Struct for structured intent/command
struct Intent {
    IntentAction action;
    std::optional<std::string> device;
    std::optional<std::string> command;
    std::optional<std::string> raw_speech;
    float confidence;

    Intent(IntentAction a, 
           std::optional<std::string> d = std::nullopt,
           std::optional<std::string> c = std::nullopt,
           std::optional<std::string> r = std::nullopt,
           float conf = 1.0f)
        : action(a), device(d), command(c), raw_speech(r), confidence(conf) {}

    std::string toString() const {
        std::string result = "Intent(action=" + intentActionToString(action);
        
        if (device) {
            result += ", device=" + *device;
        } else {
            result += ", device=None";
        }
        
        if (command) {
            result += ", command=" + *command;
        } else {
            result += ", command=None";
        }
        
        char conf_str[10];
        snprintf(conf_str, sizeof(conf_str), "%.2f", confidence);
        result += ", confidence=" + std::string(conf_str) + ")";
        
        return result;
    }
};

// Action pattern structure
struct ActionPattern {
    std::string pattern;
    IntentAction action;
    std::optional<std::string> command;
};

// Intent Parser class
class IntentParser {
private:
    std::map<std::string, std::string> device_aliases;
    std::vector<ActionPattern> action_patterns;

    // Transform string to lowercase
    static std::string toLower(const std::string& str) {
        std::string result = str;
        std::transform(result.begin(), result.end(), result.begin(),
                      [](unsigned char c) { return std::tolower(c); });
        return result;
    }

    // Trim whitespace from both ends
    static std::string trim(const std::string& str) {
        auto start = str.begin();
        while (start != str.end() && std::isspace(*start)) {
            start++;
        }

        auto end = str.end();
        do {
            end--;
        } while (std::distance(start, end) > 0 && std::isspace(*end));

        return std::string(start, end + 1);
    }

    void loadConfig(const fs::path& config_path) {
        try {
            if (!fs::exists(config_path)) {
                std::cerr << "Warning: Config file not found at " << config_path.string()
                          << ". Using minimal defaults.\n";
                setDefaults();
                return;
            }

            std::ifstream config_file(config_path);
            json config = json::parse(config_file);

            // Load device aliases
            if (config.contains("devices")) {
                const auto& devices_config = config["devices"];
                for (auto& [device_key, device_info] : devices_config.items()) {
                    std::string primary = device_info.value("primary", device_key);
                    std::vector<std::string> aliases = device_info.value("aliases", std::vector<std::string>());

                    device_aliases[toLower(device_key)] = primary;
                    for (const auto& alias : aliases) {
                        device_aliases[toLower(alias)] = primary;
                    }
                }
            }

            // Load action patterns
            if (config.contains("actions")) {
                const auto& actions_config = config["actions"];
                for (const auto& action_config : actions_config) {
                    if (!action_config.contains("pattern") || !action_config.contains("action")) {
                        continue;
                    }

                    std::string pattern = action_config["pattern"];
                    std::string action_str = action_config["action"];
                    std::optional<std::string> command = std::nullopt;

                    if (action_config.contains("command") && !action_config["command"].is_null()) {
                        command = action_config["command"].get<std::string>();
                    }

                    IntentAction intent_action = stringToIntentAction(action_str);
                    if (intent_action == IntentAction::UNKNOWN && action_str != "unknown") {
                        std::cerr << "Warning: Unknown action '" << action_str << "' in config. Skipping pattern.\n";
                        continue;
                    }

                    action_patterns.push_back({pattern, intent_action, command});
                }
            }

            if (action_patterns.empty()) {
                std::cerr << "Warning: No valid action patterns loaded from config. Using defaults.\n";
                setDefaults();
            }

        } catch (const json::exception& e) {
            std::cerr << "Error parsing config JSON: " << e.what() << ". Using defaults.\n";
            setDefaults();
        } catch (const std::exception& e) {
            std::cerr << "Error loading config: " << e.what() << ". Using defaults.\n";
            setDefaults();
        }
    }

    void setDefaults() {
        device_aliases = {
            {"living room light", "living_room_light"},
            {"living room", "living_room_light"},
            {"living room lights", "living_room_light"},
            {"living room lamp", "living_room_light"},
            {"bedroom light", "bedroom_light"},
            {"bedroom", "bedroom_light"},
            {"bedroom lights", "bedroom_light"},
            {"bedroom lamp", "bedroom_light"},
            {"kitchen light", "kitchen_light"},
            {"kitchen", "kitchen_light"},
            {"kitchen lights", "kitchen_light"},
            {"kitchen lamp", "kitchen_light"},
            {"plug one", "plug1"},
            {"plug 1", "plug1"},
            {"first plug", "plug1"},
            {"plug two", "plug2"},
            {"plug 2", "plug2"},
            {"second plug", "plug2"},
        };

        action_patterns = {
            {"turn\\s+(?:on|up)\\s+(?:the\\s+)?(.+)", IntentAction::SET, "on"},
            {"turn\\s+off\\s+(?:the\\s+)?(.+)", IntentAction::SET, "off"},
            {"switch\\s+on\\s+(?:the\\s+)?(.+)", IntentAction::SET, "on"},
            {"switch\\s+off\\s+(?:the\\s+)?(.+)", IntentAction::SET, "off"},
            {"switch\\s+(?:the\\s+)?(.+)\\s+on", IntentAction::SET, "on"},
            {"switch\\s+(?:the\\s+)?(.+)\\s+off", IntentAction::SET, "off"},
            {"toggle\\s+(?:the\\s+)?(.+)", IntentAction::TOGGLE, "toggle"},
            {"flip\\s+(?:the\\s+)?(.+)", IntentAction::TOGGLE, "toggle"},
            {"(?:what'?s|get|check)\\s+(?:the\\s+)?(?:status|state)\\s+of\\s+(?:the\\s+)?(.+)", IntentAction::GET, std::nullopt},
            {"is\\s+(?:the\\s+)?(.+)\\s+(?:on|off)\\??", IntentAction::GET, std::nullopt},
        };
    }

    std::optional<std::string> resolveDevice(const std::optional<std::string>& device_name) {
        if (!device_name) {
            return std::nullopt;
        }

        std::string device_name_lower = toLower(trim(*device_name));

        // Exact match first
        auto it = device_aliases.find(device_name_lower);
        if (it != device_aliases.end()) {
            return it->second;
        }

        // Partial match
        for (const auto& [alias, device_id] : device_aliases) {
            if (device_name_lower.find(alias) != std::string::npos ||
                alias.find(device_name_lower) != std::string::npos) {
                return device_id;
            }
        }

        return std::nullopt;
    }

public:
    IntentParser(const std::string& config_path = "") {
        fs::path path;
        if (config_path.empty()) {
            path = fs::path(__FILE__).parent_path() / "config.json";
        } else {
            path = fs::path(config_path);
        }

        loadConfig(path);
    }

    Intent parse(const std::string& speech) {
        if (speech.empty()) {
            return Intent(IntentAction::UNKNOWN, std::nullopt, std::nullopt, speech);
        }

        std::string trimmed = trim(speech);

        // Try to match against action patterns
        for (const auto& pattern_obj : action_patterns) {
            try {
                std::regex pattern(pattern_obj.pattern, std::regex::icase);
                std::smatch match;

                if (std::regex_search(trimmed, match, pattern)) {
                    std::optional<std::string> device_name = std::nullopt;
                    if (match.size() > 1) {
                        device_name = trim(match[1].str());
                    }

                    std::optional<std::string> device_id = resolveDevice(device_name);
                    float confidence = device_id ? 0.9f : 0.6f;

                    return Intent(
                        pattern_obj.action,
                        device_id,
                        pattern_obj.command,
                        trimmed,
                        confidence
                    );
                }
            } catch (const std::regex_error& e) {
                std::cerr << "Regex error: " << e.what() << "\n";
                continue;
            }
        }

        // No pattern matched
        return Intent(IntentAction::UNKNOWN, std::nullopt, std::nullopt, trimmed, 0.0f);
    }

    void addDeviceAlias(const std::string& spoken_name, const std::string& device_id) {
        device_aliases[toLower(spoken_name)] = device_id;
    }
};

// Global parser instance
static std::unique_ptr<IntentParser> g_parser = nullptr;

IntentParser* getParser() {
    if (!g_parser) {
        g_parser = std::make_unique<IntentParser>();
    }
    return g_parser.get();
}

Intent parseIntent(const std::string& speech) {
    return getParser()->parse(speech);
}

// Main test function
int main() {
    IntentParser parser;

    std::vector<std::string> test_cases = {
        "Turn on the bedroom lights",
        "Switch off the living room lamp",
        "Toggle the kitchen light",
        "Turn on plug one",
        "What's the status of the bedroom light?",
        "Is the kitchen light on?",
        "Turn on the bathroom fan",  // Unknown device
        "Play some music",  // Unknown action
    };

    std::cout << "Intent Parser Test Cases:\n\n";
    for (const auto& speech : test_cases) {
        Intent intent = parser.parse(speech);
        std::cout << "Speech: \"" << speech << "\"\n";
        std::cout << "  → " << intent.toString() << "\n\n";
    }

    return 0;
}
