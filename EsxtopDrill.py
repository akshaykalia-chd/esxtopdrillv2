from fault_finder import *
from ploting_ops import *


class EsxtopDrill(wx.Frame):
    c_sel_list = ['Not Set', 'Select Counter Group']
    plt_sel_list = ['Not Set', 'Select Counter']
    cg_list = ['Not Set', 'Load a Csv']
    tmp_df_cg_filtered = pd.DataFrame()
    tmp_df_c_filtered = pd.DataFrame()
    object_filtered_data_frame = pd.DataFrame()
    working_dir = ""

    def __init__(self):

        wx.Frame.__init__(self, None, title="Esxtop Drill", size=(600, 340))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(panel, label='Waiting on user action')
        self.label.SetForegroundColour((0, 0, 255))  # set text color
        vbox.Add(self.label, 2, wx.ALL, 5)

        self.btn_faultfinder = wx.Button(panel, -1, "Fault Finder")
        vbox.Add(self.btn_faultfinder, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.label1 = wx.StaticText(panel, label="OR", style=wx.ALIGN_CENTRE)
        vbox.Add(self.label1, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        chlbl = wx.StaticText(panel, label="Counter Groups", style=wx.ALIGN_CENTRE)
        vbox.Add(chlbl, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.choice = wx.Choice(panel, choices=self.cg_list)
        vbox.Add(self.choice, 1, wx.EXPAND | wx.ALL, 5)

        chlbl_1 = wx.StaticText(panel, label="Counters", style=wx.ALIGN_CENTRE)
        vbox.Add(chlbl_1, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.choice_1 = wx.Choice(panel, choices=self.c_sel_list)
        vbox.Add(self.choice_1, 1, wx.EXPAND | wx.ALL, 5)

        chlbl_2 = wx.StaticText(panel, label="What would you like to plot", style=wx.ALIGN_CENTRE)
        vbox.Add(chlbl_2, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.choice_2 = wx.Choice(panel, choices=self.plt_sel_list)
        vbox.Add(self.choice_2, 1, wx.EXPAND | wx.ALL, 5)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_selwdir = wx.Button(panel, -1, "Select Working Directory")
        hbox.Add(self.btn_selwdir, 0, wx.ALIGN_CENTER)
        self.btn_loadcsv = wx.Button(panel, -1, "Load CSV")
        hbox.Add(self.btn_loadcsv, 0, wx.ALIGN_CENTER)
        self.btn_dropsys = wx.Button(panel, -1, "Drop System objects")
        hbox.Add(self.btn_dropsys, 0, wx.ALIGN_CENTER)
        hbox.AddStretchSpacer()

        vbox.Add(hbox, 1, wx.ALIGN_CENTER)
        vbox.AddStretchSpacer()

        self.choice.Bind(wx.EVT_CHOICE, self.onchoice)
        self.choice_1.Bind(wx.EVT_CHOICE, self.onchoice_1)
        self.choice_2.Bind(wx.EVT_CHOICE, self.onchoice_2)
        self.btn_selwdir.Bind(wx.EVT_BUTTON, self.selwdir_onclick)
        self.btn_loadcsv.Bind(wx.EVT_BUTTON, self.loadcsv_onclick)
        self.btn_faultfinder.Bind(wx.EVT_BUTTON, self.faultfinder_onclick)
        self.btn_dropsys.Bind(wx.EVT_BUTTON, self.dropsys_onclick)

        panel.SetSizer(vbox)
        self.Centre()
        self.Show()

    # -----------------------------------------------------------------------------------

    def selwdir_onclick(self, event):
        self.label.SetForegroundColour((255, 0, 0))
        self.label.SetLabel('Processing')
        self.update_working_dir()
        self.label.SetForegroundColour((0, 0, 255))
        self.label.SetLabel('Waiting on user action')

    def loadcsv_onclick(self, event):
        self.label.SetForegroundColour((255, 0, 0))
        self.label.SetLabel('Processing')
        try:
            self.load_data()
        except:
            print(datetime.now(), 'Error Loading the CSV file')
        self.choice.Clear()
        self.choice.AppendItems(self.cg_list)
        self.choice_1.Clear()
        self.choice_2.Clear()
        self.label.SetForegroundColour((0, 0, 255))
        self.label.SetLabel('Waiting on user action')

    def faultfinder_onclick(self, event):
        self.label.SetForegroundColour((255, 0, 0))
        self.label.SetLabel('Processing')
        if self.working_dir == "":
            error("Working Directory not Set")
        else:
            if self.object_filtered_data_frame.empty:
                error("CVS File not Loaded")
            else:
                fault_finder(self.object_filtered_data_frame, self.working_dir)
        self.label.SetForegroundColour((0, 0, 255))
        self.label.SetLabel('Waiting on user action')

    def dropsys_onclick(self, event):
        self.label.SetForegroundColour((255, 0, 0))
        self.label.SetLabel('Processing')
        if self.working_dir == "":
            error("Working Directory not Set")
        else:
            if self.object_filtered_data_frame.empty:
                error("CVS File not Loaded")
            else:
                self.drop_sys(self.object_filtered_data_frame)
                self.choice.Clear()
                self.choice.AppendItems(self.cg_list)
                self.choice_1.Clear()
                self.choice_2.Clear()
        self.label.SetForegroundColour((0, 0, 255))
        self.label.SetLabel('Waiting on user action')

    def onchoice(self, event):
        self.label.SetForegroundColour((255, 0, 0))
        self.label.SetLabel('Processing')
        if self.working_dir == "":
            error("Working Directory not Set")
        else:
            if self.object_filtered_data_frame.empty:
                error("CVS File not Loaded")
            else:
                cg_selection = self.choice.GetString(self.choice.GetSelection())
                data_frame = filer_counter_group(self.object_filtered_data_frame, cg_selection, self.working_dir)
                self.prep_counter_list(data_frame)
                self.choice_1.Clear()
                self.choice_1.AppendItems(self.c_sel_list)
                self.update_tmp_df(data_frame, 'cg')
        self.label.SetForegroundColour((0, 0, 255))
        self.label.SetLabel('Waiting on user action')

    # -------------------------------------------------------------------------------------

    def onchoice_1(self, event):
        self.label.SetForegroundColour((255, 0, 0))
        self.label.SetLabel('Processing')
        if self.working_dir == "":
            error("Working Directory not Set")
        else:
            if self.object_filtered_data_frame.empty:
                error("CVS File not Loaded")
            else:
                cg_selection = self.choice.GetString(self.choice.GetSelection())
                c_selection = self.choice_1.GetString(self.choice_1.GetSelection())
                data_frame = filer_counter(self.tmp_df_cg_filtered, c_selection, cg_selection, self.working_dir)
                self.prep_plt_list(data_frame)
                self.choice_2.Clear()
                self.choice_2.AppendItems(self.plt_sel_list)
                self.update_tmp_df(data_frame, 'c')
        self.label.SetForegroundColour((0, 0, 255))
        self.label.SetLabel('Waiting on user action')

    # -------------------------------------------------------------------------------------

    def onchoice_2(self, event):
        if self.working_dir == "":
            error("Working Directory not Set")
        else:
            if self.object_filtered_data_frame.empty:
                error("CVS File not Loaded")
            else:
                self.label.SetForegroundColour((255, 0, 0))
                self.label.SetLabel('Processing')
                data_frame = self.tmp_df_c_filtered
                cg_selection = self.choice.GetString(self.choice.GetSelection())
                plt_selection = self.choice_2.GetString(self.choice_2.GetSelection())
                plotit(plt_selection, self.working_dir, data_frame, cg_selection)
                self.label.SetForegroundColour((0, 0, 255))
                self.label.SetLabel('Waiting on user action')

    # -------------------------------------------------------------------------------------

    @classmethod
    def prep_counter_list(cls, cg_filtered_data_frame):
        col_name_df = pd.DataFrame(cg_filtered_data_frame.columns)
        col_name_df = col_name_df.drop([0])
        col_name_df = col_name_df[0].str.split(("\\"), expand=True)
        cls.c_sel_list = list(col_name_df[4].unique())

    # --------------------------------------------------------------------------------------
    @classmethod
    def prep_plt_list(cls, c_filtered_data_frame):
        col_name_df = pd.DataFrame(c_filtered_data_frame.columns)
        col_name_df = col_name_df.drop([0])
        cls.plt_sel_list = list(col_name_df[0].unique())

    # --------------------------------------------------------------------------------------
    @classmethod
    def update_tmp_df(cls, tmp_df, df_type):
        if df_type == 'cg':
            cls.tmp_df_cg_filtered = tmp_df
        if df_type == 'c':
            cls.tmp_df_c_filtered = tmp_df

    @classmethod
    def update_working_dir(cls):
        working_dir = get_dir("Working directory")
        cls.working_dir = working_dir
        if not (cls.cg_list[0] == 'Not Set'):
            prep_working_dir(cls.cg_list, cls.working_dir)

    @classmethod
    def load_data(cls):
        if cls.working_dir == "":
            error("Working Directory not Set")
        else:
            data = load_csv(read_csv_location())
            if data is None:
                raise ValueError('CSV read failure')
            else:
                data = filter_objects(cls.working_dir, data)
                cls.object_filtered_data_frame = data
                cg_selection = prep_cg_selection(data)
                prep_working_dir(cg_selection, cls.working_dir)
                cls.cg_list = cg_selection

    @classmethod
    def drop_sys(cls, data):
        data = drop_sys_obj(data)
        cls.object_filtered_data_frame = data

    # --------------------------------------------------------------------------------------
app = wx.App()
EsxtopDrill()
app.MainLoop()
app.ExitMainLoop()
exit()
