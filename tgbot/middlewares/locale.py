from pathlib import Path

from aiogram.contrib.middlewares.i18n import I18nMiddleware

I18N_DOMAIN = "exam-bot"

BASE_DIR = Path(__name__).parent
LOCALES_DIR = BASE_DIR / "locales"

# Setup i18n middleware
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)

# Alias for gettext method
t = i18n.gettext
