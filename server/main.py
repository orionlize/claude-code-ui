from tasks import tasks_bp
from projects import projects_bp
from health import health_bp
from telegram import telegram_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
app.register_blueprint(health_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(telegram_bp)

@app.errorhandler(404)
def not_found(error):