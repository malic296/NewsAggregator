from web import create_app
import os

env = os.environ.get("FE_ENV", "dev")
app = create_app(env)

if __name__ == "__main__":
    app.run()
