import openwakeword
from openwakeword.model import Model as WakeModel

openwakeword.utils.download_models(
        model_names=["hey_jarvis"],           # can also list multiple e.g. ["hey_jarvis", "ok_nabu"]
    )