from file_dir_ops import *
from filters_ops import *


def fault_finder(data_frame, working_dir):
    print(datetime.now(), ' Processing Started')
    c_map_df = pd.DataFrame(pd.read_csv('c_map.csv'))
    cg_selection = list(c_map_df['Counter_Group'].unique())
    prep_working_dir(cg_selection, working_dir)
    object_name = list()
    counter_name = list()
    average = list()
    maximum = list()
    ok_count = list()
    warning_count = list()
    warning_count_low = list()
    warning_count_high = list()
    critical_count = list()
    message = list()
    ok_threshold = list()
    warning_threshold = list()
    critical_threshold = list()
    qdepths = pd.Series(dtype='int64')

    for cg in cg_selection:
        c_index = list()
        counters = list()
        c_index.extend(c_map_df.index[c_map_df['Counter_Group'] == cg].tolist())
        temp_df1 = filer_counter_group(data_frame, cg, working_dir)
        for index in c_index:
            counters.append(c_map_df['Counter'][index])
        for counter in counters:
            temp_df2 = filer_counter(temp_df1, counter, cg, working_dir)
            try:
                temp_df2 = temp_df2.drop(columns=['(PDH-CSV 4.0) (UTC)(0)'])
            except AttributeError:
                print(datetime.now(),
                      ' Missing counter', counter,
                      '.The input csv is not collected using -a switch of esxtop. Moving on')
                continue

            threshold = c_map_df.iloc[np.where(c_map_df.Counter_Group.values == cg)]
            threshold = threshold.iloc[np.where(threshold.Counter.values == counter)]
            counter_type = threshold['Counter_type'].values
            counter_type = counter_type[0]
            counter_scope = threshold['Counter_Scope'].values
            counter_scope = counter_scope[0]
            ok_val = threshold['Ok_val'].values
            warning_val = threshold['Warning_val'].values
            critical_val = threshold['Critical_val'].values
            message_val = threshold['Message'].values
            col_list = pd.DataFrame(temp_df2.columns)
            col_list = list(col_list[0].unique())

            if counter_type != 'Bool' and counter_type != 'Num_cal':
                ok_val = float(ok_val[0])
                warning_val = float(warning_val[0])
                critical_val = float(critical_val[0])
                message_val = message_val[0]
                avg_series = pd.Series(temp_df2.mean())
                max_series = pd.Series(temp_df2.max())
                if counter_scope != 'obj_hig':
                    count_ok_series = pd.Series((temp_df2 <= ok_val).apply(np.count_nonzero))
                    count_critical_series = pd.Series((temp_df2 >= critical_val).apply(np.count_nonzero))
                    count_warning_series = pd.Series((temp_df2 > ok_val).apply(np.count_nonzero))
                    count_warning_low = pd.Series((temp_df2 < warning_val).apply(np.count_nonzero))
                    count_warning_high = pd.Series((temp_df2 >= warning_val).apply(np.count_nonzero))

                else:
                    count_ok_series = pd.Series((temp_df2 >= ok_val).apply(np.count_nonzero))
                    count_warning_series = pd.Series((temp_df2 < ok_val).apply(np.count_nonzero))
                    count_critical_series = pd.Series((temp_df2 <= critical_val).apply(np.count_nonzero))
                    count_warning_low = pd.Series((temp_df2 > warning_val).apply(np.count_nonzero))
                    count_warning_high = pd.Series((temp_df2 <= warning_val).apply(np.count_nonzero))
                count_warning_low = count_warning_low.subtract(count_ok_series, fill_value=0)
                count_warning_high = count_warning_high.subtract(count_critical_series, fill_value=0)

                count_warning_series = count_warning_series.rename('Count_Warning_Critical')
                count_critical_series = count_critical_series.rename('Count_Critical')
                count_warning_low = count_warning_low.rename('Count_Warning_Low')
                count_warning_high = count_warning_high.rename('Count_Warning_High')
                avg_series = avg_series.rename('Average')
                max_series = max_series.rename('Max')
                count_ok_series = count_ok_series.rename('Count_Ok')
                try:
                    max_avg_count_df = pd.DataFrame(
                        [avg_series, max_series, count_ok_series, count_critical_series, count_warning_series,
                         count_warning_low, count_warning_high])
                    max_avg_count_df.loc['Count_Warning'] = max_avg_count_df.loc['Count_Warning_Critical'] - \
                                                            max_avg_count_df.loc['Count_Critical']
                except ValueError:
                    print(datetime.now(),
                          ' Missing counter', counter,
                          '.The input csv is not collected using -a switch of esxtop. Moving on')

                if counter_scope != 'obj_hig':
                    for col in col_list:
                        obj_max_val = max_avg_count_df.at['Max', col]
                        if obj_max_val > ok_val:
                            obj_name = find_obj(col, counter_scope)
                            if counter != '% VmWait':
                                object_name.append(obj_name)
                                counter_name.append(counter)
                                average.append(max_avg_count_df.at['Average', col])
                                maximum.append(obj_max_val)
                                ok_count.append(max_avg_count_df.at['Count_Ok', col])
                                warning_count.append(max_avg_count_df.at['Count_Warning', col])
                                warning_count_low.append(max_avg_count_df.at['Count_Warning_Low', col])
                                warning_count_high.append(max_avg_count_df.at['Count_Warning_High', col])
                                critical_count.append(max_avg_count_df.at['Count_Critical', col])
                                message.append(message_val)
                                ok_threshold.append(ok_val)
                                warning_threshold.append(warning_val)
                                critical_threshold.append(critical_val)
                            else:
                                if 'vmx-vcpu-' in obj_name:
                                    object_name.append(obj_name)
                                    counter_name.append(counter)
                                    average.append(max_avg_count_df.at['Average', col])
                                    maximum.append(obj_max_val)
                                    ok_count.append(max_avg_count_df.at['Count_Ok', col])
                                    warning_count.append(max_avg_count_df.at['Count_Warning', col])
                                    warning_count_low.append(max_avg_count_df.at['Count_Warning_Low', col])
                                    warning_count_high.append(max_avg_count_df.at['Count_Warning_High', col])
                                    critical_count.append(max_avg_count_df.at['Count_Critical', col])
                                    message.append(message_val)
                                    ok_threshold.append(ok_val)
                                    warning_threshold.append(warning_val)
                                    critical_threshold.append(critical_val)
                else:
                    for col in col_list:
                        obj_max_val = max_avg_count_df.at['Max', col]
                        if obj_max_val < ok_val:
                            obj_name = find_obj(col, counter_scope)
                            object_name.append(obj_name)
                            counter_name.append(counter)
                            average.append(max_avg_count_df.at['Average', col])
                            maximum.append(obj_max_val)
                            ok_count.append(max_avg_count_df.at['Count_Ok', col])
                            warning_count.append(max_avg_count_df.at['Count_Warning', col])
                            warning_count_low.append(max_avg_count_df.at['Count_Warning_Low', col])
                            warning_count_high.append(max_avg_count_df.at['Count_Warning_High', col])
                            critical_count.append(max_avg_count_df.at['Count_Critical', col])
                            message.append(message_val)
                            ok_threshold.append(ok_val)
                            warning_threshold.append(warning_val)
                            critical_threshold.append(critical_val)
            else:
                if counter_type == 'Bool':
                    min_series = pd.Series(temp_df2.min())
                    min_series = min_series.rename('Min')
                    for col in col_list:
                        memctl_enabled = min_series[col]
                        if memctl_enabled == 0:
                            ok_val = '1'
                            warning_val = 'NA'
                            critical_val = '0'
                            message_val = 'Memory Ballooning is disabled. System will use swapping in case of contention.'
                            object_name.append(find_obj(col, counter_scope))
                            counter_name.append(counter)
                            average.append('NA')
                            maximum.append('NA')
                            ok_count.append('NA')
                            warning_count.append('NA')
                            warning_count_high.append('NA')
                            warning_count_low.append('NA')
                            critical_count.append('NA')
                            message.append(message_val)
                            ok_threshold.append(ok_val)
                            warning_threshold.append(warning_val)
                            critical_threshold.append(critical_val)
                else:
                    if counter == "Adapter Q Depth":
                        qdepth_series = pd.Series(temp_df2.max())
                        for col in col_list:
                            obj_name = find_obj(col, counter_scope)
                            if not (':' in obj_name):
                                qdepth = qdepth_series[col]
                                obj_name = obj_name.replace("(", " Adapter(")
                                qdepths[obj_name] = qdepth

                    if counter == "Commands/sec":
                        try:
                            commands_series_max = pd.Series(temp_df2.max())
                            commands_series_avg = pd.Series(temp_df2.mean())
                            for col in col_list:
                                obj_name = find_obj(col, counter_scope)
                                if not (':' in obj_name):
                                    ok_val = qdepths[obj_name] * 1.5
                                    warning_val = qdepths[obj_name] * 3
                                    critical_val = qdepths[obj_name] * 4
                                    obj_max_val = commands_series_max[col]
                                    if obj_max_val >= ok_val:
                                        count_ok = (temp_df2[col] <= ok_val).sum()
                                        count_warning = (temp_df2[col] > ok_val).sum()
                                        count_critical = (temp_df2[col] >= critical_val).sum()
                                        count_warning_low = (temp_df2[col] < warning_val).sum()
                                        count_warning_high = (temp_df2[col] >= warning_val).sum()
                                        count_warning_low = count_warning_low - count_ok
                                        count_warning_high = count_warning_high - count_critical
                                        count_warning = count_warning - count_critical
                                        obj_avg_val = commands_series_avg[col]
                                        object_name.append(obj_name)
                                        counter_name.append(counter)
                                        average.append(obj_avg_val)
                                        maximum.append(obj_max_val)
                                        ok_count.append(count_ok)
                                        warning_count.append(count_warning)
                                        warning_count_low.append(count_warning_low)
                                        warning_count_high.append(count_warning_high)
                                        critical_count.append(count_critical)
                                        message.append('Possible HBA overload')
                                        ok_threshold.append(ok_val)
                                        warning_threshold.append(warning_val)
                                        critical_threshold.append(critical_val)
                        except:
                            print(datetime.now(),
                                  ' Missing counter', counter,
                                  '.The input csv is not collected using -a switch of esxtop. Moving on')

    object_name = pd.Series(object_name, name='Object')
    counter_name = pd.Series(counter_name, name='Counter')
    average = pd.Series(average, name='Average')
    maximum = pd.Series(maximum, name='Maximum')
    ok_count = pd.Series(ok_count, name='Ok_Count')
    warning_count = pd.Series(warning_count, name='Warning_Count')
    warning_count_low = pd.Series(warning_count_low, name='Warning_Count_Low')
    warning_count_high = pd.Series(warning_count_high, name='Warning_Count_High')
    critical_count = pd.Series(critical_count, name='Critical_Count')
    message_col = pd.Series(message, name='Message')
    threshold_ok = pd.Series(ok_threshold, name='Threshold OK')
    threshold_warning = pd.Series(warning_threshold, name='Threshold Warning')
    threshold_critical = pd.Series(critical_threshold, name='Threshold Critical')
    out_df = pd.DataFrame(
        [object_name, counter_name, average, maximum, ok_count, warning_count_low, warning_count, warning_count_high,
         critical_count,
         threshold_ok, threshold_warning, threshold_critical, message_col])
    out_df = out_df.transpose()
    outfile = 'anomalies-' + str(int(time.time())) + '.csv'
    outfile = os.path.join(working_dir, outfile)
    out_df.to_csv(outfile, index=False)
    print(datetime.now(), ' Done processing, please review %s' % outfile)
    dialog('Done processing for faults, please review %s' % outfile)
