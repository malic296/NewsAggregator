from web import create_web
import os

env = os.environ.get("FE_ENV", "dev")
web = create_web(env)

if __name__ == "__main__":
    web.run()
