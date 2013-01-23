import sublime, sublime_plugin, os, subprocess

class AutoSlim(sublime_plugin.EventListener):
  def on_post_save(self, view):
    # Get the plugin settings
    self.settings = sublime.load_settings('AutoSlim.sublime-settings')
    if self.settings.get('run_on_save'):
      view.window().run_command("auto_slim", use_file=True)

class AutoSlimCommand(sublime_plugin.TextCommand):
  def run(self, edit, use_file = False):
    # Ensure we are operating on a slim file
    if self.view.file_name()[-5:] != '.slim':
      return False

    # Initialize the pluigin environment location
    self.plugin_path = os.path.join(sublime.packages_path(), 'AutoSlim')

    # Initialize the target file information
    self.target_path = self.view.window().active_view().file_name()
    self.target_dir = os.path.dirname(self.target_path)
    self.target_file = os.path.basename(self.target_path)

    # Initialize the plugin settings
    self.settings = sublime.load_settings('AutoSlim.sublime-settings')

    # Get the content of the current window
    self.active_view = self.view.window().active_view()
    self.buffer_region = sublime.Region(0, self.active_view.size())
    body = self.active_view.substr(self.buffer_region)

    # Execute the slim library
    slim = subprocess.Popen(self.cmd(use_file=use_file), 
      shell=True, cwd=self.target_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Pass the code to parse
    if use_file:
      out = slim.communicate()
    else:
      out = slim.communicate(body)

    if (out[0] == "" and body != ""):
      # Notify of error
      sublime.error_message("Invalid Output: Check your ruby interpreter settings or console")
      print out[1].decode('utf8')
    else:
      print 'Slim Success!'
      sublime.set_clipboard(out[0].decode('utf8'))

  def cmd(self, use_file = False):
    # Get the ruby exec name from either the system, or from the plugin
    ruby = self.view.settings().get('ruby', self.settings.get('ruby'))
    script_path  = os.path.join(self.plugin_path, 'slim', 'bin', "slimrb")
    command = ruby + " '" + script_path + "' " + unicode(self.target_path)
    return command