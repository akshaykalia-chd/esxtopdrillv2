import wx


# simple dialog
def dialog(message):
    wx.MessageBox(message, 'Information', wx.OK)
    return


# --------------------------------------------------------------
# warning dialog
def warning(message):
    wx.MessageBox(message, 'Warning', wx.OK | wx.ICON_WARNING)
    return


# --------------------------------------------------------------
# error dialog
def error(message):
    wx.MessageBox(message, 'Error', wx.OK | wx.ICON_ERROR)
    return


# ----------------------------------------------------------------
# Question dialog
def question(message):
    u_sel = wx.MessageBox(message, 'Question?', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
    return u_sel


# ----------------------------------------------------------------
# Get File dialog
def get_file(what):
    frame = wx.Frame(None, -1, 'win.py')
    frame.SetSize(0, 0, 200, 50)
    open_file_dialog = wx.FileDialog(frame, what, "", "", "CSV (*.csv)|*.csv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
    open_file_dialog.ShowModal()
    return open_file_dialog.GetPath()


# -------------------------------------------------------------------------
# Get Dir dialog
def get_dir(what):
    frame = wx.Frame(None, -1, 'win.py')
    frame.SetSize(0, 0, 200, 50)
    open_file_dialog = wx.DirDialog(frame, what, "", style=wx.DD_DEFAULT_STYLE)
    open_file_dialog.ShowModal()
    return open_file_dialog.GetPath()


# -------------------------------------------------------------------------
# Get list dialog
def get_list(what, title):
    frame = wx.Frame(None, -1, 'win.py')
    frame.SetSize(0, 0, 200, 50)
    open_file_dialog = wx.TextEntryDialog(frame, what, title)
    open_file_dialog.ShowModal()
    out_list = open_file_dialog.GetValue()
    if out_list != '':
        out_list = list(out_list.split(','))
    else:
        out_list = list(out_list)
    return out_list
