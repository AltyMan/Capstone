with open("ding.mp3", "rb") as f:
    data = f.read()

with open("ding_mp3.h", "w") as f:
    f.write("#include <stdint.h>\n\n")
    f.write(f"const unsigned int ding_mp3_len = {len(data)};\n")
    f.write("const uint8_t ding_mp3[] = {\n")
    
    for i, byte in enumerate(data):
        f.write(f"0x{byte:02x}, ")
        if (i + 1) % 12 == 0:
            f.write("\n")
            
    f.write("\n};\n")
print("Successfully created ding_mp3.h!")