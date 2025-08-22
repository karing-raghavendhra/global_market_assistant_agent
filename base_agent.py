import os
import streamlit as st

class BaseAgent:
    def __init__(self, required_api_keys=None):
        """
        required_api_keys: list of dicts, e.g. [{"name": "GOOGLE_API_KEY", "label": "Google API Key"}]
        """
        self.api_keys = {}
        if required_api_keys is None:
            required_api_keys = []
        self.required_api_keys = required_api_keys
        self._check_and_prompt_api_keys()

    def _check_and_prompt_api_keys(self):
        """Check for required API keys in env, prompt user if missing, and set for session."""
        for key_info in self.required_api_keys:
            key_name = key_info["name"]
            key_label = key_info.get("label", key_name)
            api_key = os.getenv(key_name)
            # Special case: prefill Tavily key if user provided
            if key_name == "TAVILY_API_KEY" and not api_key:
                api_key = "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"
                os.environ[key_name] = api_key
            # Special case: prefill Google key if user provided
            if key_name == "GOOGLE_API_KEY" and not api_key:
                api_key = "AIzaSyACH1JbfEgg44OQINH77UQHIJShYhP8dJ8"
                os.environ[key_name] = api_key
            # Only prompt if not Google API Key
            if not api_key and key_name != "GOOGLE_API_KEY":
                api_key = st.sidebar.text_input(f"Enter {key_label}", type="password", key=key_name)
                if api_key:
                    os.environ[key_name] = api_key
            self.api_keys[key_name] = api_key

    def get_api_key(self, key_name):
        return self.api_keys.get(key_name) or os.getenv(key_name)

    def analyze(self, *args, **kwargs):
        raise NotImplementedError("Each agent must implement its own analyze method.") 