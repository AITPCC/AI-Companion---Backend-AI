from Backend import app
import uvicorn

def main():
    print("Hello from aipc!")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=2333)
