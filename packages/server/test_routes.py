import asyncio
import json
import urllib.request

def main():
    try:
        req = urllib.request.Request("http://localhost:8000/openapi.json")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            
            paths = data.get("paths", {})
            for path, methods in paths.items():
                if "pipelines" in path:
                    print(f"{path} : {list(methods.keys())}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
