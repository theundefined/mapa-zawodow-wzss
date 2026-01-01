from fetch_competitions import main as fetch_main
import os

if __name__ == "__main__":
    # Change working directory to the script's directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    fetch_main()
