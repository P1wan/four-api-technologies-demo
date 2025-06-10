"""Generate gRPC Python code from proto file"""
import subprocess
import sys

def generate_grpc_code():
    try:
        subprocess.run([
            sys.executable, "-m", "grpc_tools.protoc",
            "-I.",
            "--python_out=.",
            "--grpc_python_out=.",
            "streaming.proto"
        ], check=True)
        print("✅ gRPC code generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating gRPC code: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_grpc_code() 