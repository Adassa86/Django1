from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
import datetime
from datetime import datetime as td
import os
from collections import defaultdict

def home(request):
#upload file and save it in media folder
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        uploaded_file2 = request.FILES['document2']

        if uploaded_file.name.endswith('.xls'):

            savefile = FileSystemStorage()
#save files
            name = savefile.save(uploaded_file.name, uploaded_file)
            name2 = savefile.save(uploaded_file2.name, uploaded_file2)

            d = os.getcwd()
            file_directory = d+'\\media\\'+name
            file_directory2 = d+'\\media\\'+name2

            results,output_df,new =results1(file_directory,file_directory2)
            return render(request,"results.html",{"results":results,"output_df":output_df,"new":new})

    return render(request, "index.html")
#read file
def readfile(uploaded_file):

    data = pd.read_excel(uploaded_file, index_col=None)
    return data


def results1(file1,file2):

    results_list = defaultdict(list)
    names_loc = file2
    listing_file = pd.read_excel(file1, index_col=None)
    headers = ['Vector Name', 'Date and Time', 'Test ID', 'PCR POS/Neg']
    output_df = pd.DataFrame(columns=headers)


    with open(names_loc, "r") as fp:
        for line in fp.readlines():
            line = line.rstrip("\\\n")
            full_name = line.split(',')
            sample_name = full_name[0].split('_mean')
            try:
                if len(sample_name[0].split('SCO_')) > 1:
                    sample_id = int(sample_name[0].split('SCO_')[1])
                else:
                    sample_id = int(sample_name[0].split('SCO')[1])
            except:
                sample_id = sample_name[0]

            try:
                if listing_file['Test ID'].isin([sample_id]).any():
                    line_data = listing_file.loc[listing_file['Test ID'].isin([sample_id])]
 # The name of the file as it is shown in the folder
                    vector_name = line
 # The data and the time of the taken sample
                    d_t = full_name[1].split('us_')[1].split('_')
                    date_time = td(int(d_t[0]), int(d_t[1]), int(d_t[2]), int(d_t[3]), int(d_t[4]), int(d_t[5]))
# Calculating the time frame from the swap to test of samples
                    date_index = list(line_data['Collecting  Date from the subject'].iteritems())

                    for x in date_index:
                        if type(x[1]) is str():
                            date_time_obj = td.strptime(x[1], '%Y.%m.%d.  %H:%M')
                        elif type(x[1]) is pd.Timestamp:
                            date_time_obj = x[1]
                        elif type(x[1]) is datetime.datetime:
                            date_time_obj = x[1]

                    frame_time = str(date_time - date_time_obj)

                    if date_time - date_time_obj > datetime.timedelta(hours=48):
                        results_list["List of samples with  time frame  over 48 "].append(sample_id)
 # The Test ID as it writen in the listing file
                    test_id = sample_id
# The PCR answer as it was written in the listing file
                    pcr_index = list(line_data['PCR Pos/Neg'].iteritems())
                    if len(pcr_index) > 1:

                        results_list["List of Samples with more than one attribute in the listing file:"].append(sample_id)

                    for x in pcr_index:
                        pcr_ans = x[1].strip()

                    values_to_add = {'Vector Name': vector_name,
                                     'Date and Time': date_time,
                                     'Test ID': test_id,
                                     'PCR POS/Neg': pcr_ans,
                                     'Time Frame': frame_time
                                     }

                    row_to_add = pd.Series(values_to_add)
                    output_df = output_df.append(row_to_add, ignore_index=True)
                else:

                    results_list["List of Samples not in the listing file"].append(sample_name[0])
            except:
                print('The template name isnt good: {}'.format(sample_id))

    output_df['Date and Time'] = pd.to_datetime(output_df['Date and Time'])
    new = output_df.groupby([output_df['Date and Time'].dt.date, 'PCR POS/Neg']).size().unstack(fill_value=0)
    new.sort_values(by=['Date and Time'], ascending=True)
    new['Total per date'] = output_df.groupby([output_df['Date and Time'].dt.date])['PCR POS/Neg'].count()
    new.loc['Total', :] = new.sum(axis=0)

    return dict(results_list), output_df.to_html(), new.to_html()

