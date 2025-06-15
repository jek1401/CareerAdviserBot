from main import bot

def test_bot_initialized():
    assert bot is not None
    assert hasattr(bot, 'message_handler')