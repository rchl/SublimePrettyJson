import sublime
import sublime_plugin

from .PrettyJson import PrettyJsonBaseCommand

s = sublime.load_settings("Pretty JSON.sublime-settings")


class PrettyJsonLintListener(sublime_plugin.EventListener, PrettyJsonBaseCommand):
    def on_post_save(self, view):
        if not s.get("validate_on_save", True):
            return

        as_json = s.get("as_json", ["JSON"])
        if any(syntax in view.settings().get("syntax") for syntax in as_json):
            self.clear_phantoms()
            json_content = view.substr(sublime.Region(0, view.size()))
            try:
                self.json_loads(json_content)
            except Exception as ex:
                self.show_exception(msg=ex)

    def on_modified_async(self, view: sublime.View) -> None:
        settings = view.settings()
        content_window_id = settings.get("pretty-json-jq-query-window-id")
        jq_path = settings.get("pretty-json-jq-path")
        if not jq_path or content_window_id is not None:
            content_window = next((w for w in sublime.windows() if w.id() == content_window_id), None)
            if content_window:
                query = view.substr(sublime.Region(0, view.size()))
                content_window.run_command("jq_query_update", {"jq_path": jq_path, "query": query})


class PrettyJsonAutoPrettyOnSaveListener(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if not s.get("pretty_on_save", False):
            return

        as_json = s.get("as_json", ["JSON"])
        if any(syntax in view.settings().get("syntax") for syntax in as_json):
            view.run_command("pretty_json")
