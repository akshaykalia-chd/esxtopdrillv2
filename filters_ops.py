import os
import time
from datetime import datetime

import numpy as np
import pandas as pd

from ui_functions import *


# --------------------------------------------------------------------------
# Function to implement object filtration
def filter_objects(working_dir, esxtop_data_frame):
    val_err = True
    while val_err:
        object_selection = get_list(
            "Do you know a name of object(VM name, Naa ID etc).Blank,In case you do not know the name of object.",
            "Object Filter")
        input_error = 0
        for i in object_selection:
            try:
                int(i)
                input_error = input_error + 1
            except ValueError:
                input_error = input_error
        if input_error > 0:
            error("Input Error String expected. Example Input: TestVM1,naa.123456789")
            val_err = True
        else:
            val_err = False
    cdf = pd.DataFrame(esxtop_data_frame.columns)
    cdf.columns = ['Objects']
    # Processing data based on user input1
    out_df = esxtop_data_frame
    if len(object_selection) != 0:
        column_list = []
        for Object in object_selection:
            column_list.extend(cdf.index[cdf['Objects'].str.contains(Object)].tolist())
            column_list.sort(reverse=False)
        col_name = []
        col_name.insert(0, cdf['Objects'][0])
        i = 1
        for col in column_list:
            col_name.insert(i, cdf['Objects'][col])
            i = i + 1
            out_df = esxtop_data_frame[col_name]

        col_name_df = pd.DataFrame(out_df.columns)
        # Validating data in Object filtered output
        if col_name_df[0].count() <= 1:
            error("Unable to find the objects specified.Program will exit")
            return
        outfile = str(object_selection[0] + str(int(time.time())) + ".csv")
        outfile = os.path.join(working_dir, outfile)
        out_df.to_csv(outfile, index=False)
        print(datetime.now(), " Generated: ", outfile)
    return out_df


# --------------------------------------------------------------------------------------
# Function to implement Counter Group filtration
def filer_counter_group(object_filtered_data_frame, cg_selection, working_dir):
    col_name_df = pd.DataFrame(object_filtered_data_frame.columns)
    c_gn_c_df = col_name_df[0].str.split(("\\"), expand=True)
    cg_df = c_gn_c_df[3].str.split(("\("), expand=True)
    c_gn_c_df[3] = cg_df[0]
    column_list = [0]
    column_list.extend(c_gn_c_df.index[c_gn_c_df[3] == cg_selection].tolist())
    column_list.sort(reverse=False)
    col_name = []
    i = 0
    for col in column_list:
        col_name.insert(i, col_name_df[0][col])
        i = i + 1
    out_df = object_filtered_data_frame[col_name]
    outfile = str(cg_selection + "-" + str(int(time.time())) + ".csv")
    outfile = os.path.join(working_dir, cg_selection, outfile)
    out_df.to_csv(outfile, index=False)
    print(datetime.now(), " Generated: ", outfile)
    return out_df


# ------------------------------------------------------------------------------------------
# Function to implement Counter filtration
def filer_counter(cg_filtered_data_frame, c_selection, cg_selection, working_dir):
    out_df = cg_filtered_data_frame
    col_name_df = pd.DataFrame(cg_filtered_data_frame.columns)
    time_se = str(col_name_df[0][0])
    col_name_df = col_name_df.drop([0])
    c_gn_c_df = col_name_df[0].str.split(("\\"), expand=True)
    column_list = list()
    try:
        column_list.extend(c_gn_c_df.index[c_gn_c_df[4] == c_selection].tolist())
        column_list.sort(reverse=False)
        col_name = list()
        col_name.append(time_se)
        i = 1
        for Col in column_list:
            col_name.insert(i, col_name_df[0][Col])
            i = i + 1
        out_df = out_df[col_name]
        outfile = str(cg_selection + "-" + c_selection + "-" + str(int(time.time())) + ".csv")
        outfile = os.path.join(working_dir, cg_selection, outfile)
        try:
            out_df.to_csv(outfile, index=False)
        except (FileNotFoundError, OSError):
            outfile = str(cg_selection + "-" + c_selection + "-" + str(int(time.time())) + ".csv")
            outfile = outfile.replace("/", "-")
            outfile = outfile.replace("?", " ")
            outfile = os.path.join(working_dir, cg_selection, outfile)
            out_df.to_csv(outfile, index=False)
        print(datetime.now(), " Generated: ", outfile)
        return out_df
    except KeyError:
        return


# ------------------------------------------------------------------------------------
# Function to prepare Counter group selection list
def prep_cg_selection(object_filtered_data_frame):
    col_name_df = pd.DataFrame(object_filtered_data_frame.columns)
    c_gn_c_df = col_name_df[0].str.split(("\\"), expand=True)
    cg_df = c_gn_c_df[3].str.split(("\("), expand=True)
    c_gn_c_df[3] = cg_df[0]
    counter_groups = pd.DataFrame(cg_df[0].unique())
    counter_groups.columns = ['Counter Groups']
    counter_groups = counter_groups.replace(to_replace='None', value=np.nan).dropna()
    selection_list = counter_groups['Counter Groups'].tolist()
    return selection_list


# ------------------------------------------------------------------------------------------
# Function to drop system objects
def drop_sys_obj(data):
    sel = question('Do you want to drop system objects like vpxa workers, hostd workers etc?')
    if sel == 2:
        sys_obj = [
            ':system', ':helper', ':drivers', ':ft', ':vmotion', ':init', ':vmsyslogd', ':sh', ':vobd', ':vmkeventd',
            ':vmkdevmgr', ':net-lacp', ':dhclient-uw', ':vmkiscsid', ':nfsgssd', ':busybox', ':ntpd',
            ':vmware-usbarbitrator', ':ioFilterVPServer', ':swapobjd', ':storageRM', ':hostdCgiServer', ':sensord',
            ':net-lbt', ':hostd', ':rhttpproxy', ':slpd', ':net-cdp', ':nscd', ':smartd', ':lwsmd', ':pktcap-agent',
            ':netcpa', ':vdpi', ':logchannellogger', ':logger', ':dcui', ':vpxa', ':fdm', ':vsfwd', ':sfcbd',
            ':sfcb-sfcb',
            ':sfcb-ProviderMa', ':openwsmand', ':sshd', ':esxtop', ':gzip', ':sdrsInjector', ':timeout']
        c_df = pd.DataFrame(data.columns)
        c_index_list = list()
        for obj in sys_obj:
            c_index_list.extend(c_df.index[c_df[0].str.contains(obj)].tolist())
        c_name_list = list()
        for c_index in c_index_list:
            c_name = c_df.at[c_index, 0]
            c_name_list.append(c_name)
        out_df = data.drop(c_name_list, axis=1)
        print(datetime.now(), ' System objects dropped')
        return out_df
    else:
        return data


# ------------------------------------------------------------------------------------------
# Function to Prepare a Object Name
def find_obj(data, scope):
    obj_id = data.split("\\")
    if scope == 'sys':
        return str(obj_id[4])
    else:
        return str(obj_id[3])
