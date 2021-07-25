from github import Github
import datetime as dt
import requests
import random as r
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import ast
import pathlib

file_location = str(pathlib.Path(__file__).parent.resolve()).replace('\\', '/') + '/'

# Fill option lists on task creator/editor with relevant data
x = 2000
all_numbers_2000_to_2099 = []
while x <= 2099:
    all_numbers_2000_to_2099.append(x)
    x += 1
x = 1
all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
all_numbers_1_to_31 = []
while x <= 31:
    all_numbers_1_to_31.append(x)
    x += 1
x = 0
all_numbers_0_to_23 = []
while x <= 23:
    all_numbers_0_to_23.append(x)
    x += 1
x = 0
all_numbers_0_to_59 = []
while x <= 59:
    all_numbers_0_to_59.append(x)
    x += 1

window = Tk()
window.title('SyncNote')
window.geometry("850x300")
task_number = IntVar()

# Date in format year/month/day/hour/minute
# generic_due_date = [21, 7, 12, 14, 30]


# Task edit code: edited_task = Task(original_task[0], original_task[1].copy(), original_task[2], original_task[4], original_task[5]).create_task()
# Any of the original_task[x] can be replaced with a new value
# When just changing one non-date value, do task[4] = True
class Task:
    # First 3 variables are self explanatory, completed is a boolean that says whether or not a task is completed, input_id for a preset ID, leave blank for randomly generated id
    def __init__(self, title, due_date, details, completed, input_id):
        self.title = title
        self.due_date = due_date
        self.details = details
        self.reminder_times = []
        self.completed = completed
        if input_id != '':
            self.task_id = input_id
        else:
            self.task_id = r.randint(1, 10000000)
        self.output_task = []

    def create_task(self):
        d = self.due_date.copy()
        self.reminder_times.append(self.set_reminder_time(7, 2, d))
        self.reminder_times.append(self.set_reminder_time(3, 2, d))
        self.reminder_times.append(self.set_reminder_time(1, 2, d))
        self.reminder_times.append(self.set_reminder_time(12, 3, d))
        self.output_task = [self.title, self.due_date.copy(), self.details, self.reminder_times.copy(), self.completed, self.task_id]

        return self.output_task

    # Calculates the times for reminders.
    # The d value is usually the base date, but if you want to change multiple values, you can replace the d with a self.set_reminder_time(u, t, d)
    def set_reminder_time(self, unit_change, time_type_affected, d):
        # Saves the input date to an input copy
        temp_reminder_times = d.copy()
        if temp_reminder_times[time_type_affected] > unit_change:
            temp_reminder_times[time_type_affected] -= unit_change
        elif temp_reminder_times[time_type_affected] == unit_change and time_type_affected >= 3:
            temp_reminder_times[time_type_affected] = 0
        else:
            # Years
            if time_type_affected == 0:
                temp_reminder_times[0] = 0
            # Months
            elif time_type_affected == 1:
                temp_reminder_times[0] -= 1
                temp_reminder_times[1] += (12 - unit_change)
            # Days, Hours, and Minutes
            elif time_type_affected >= 2:
                # Minutes
                if time_type_affected == 4:
                    temp_reminder_times[4] += (60 - unit_change)
                    temp_reminder_times[3] -= 1
                    if temp_reminder_times[3] < 0:
                        temp_reminder_times[3] += 24
                        temp_reminder_times[2] -= 1
                # Hours
                elif time_type_affected == 3 and temp_reminder_times[3] <= unit_change:
                    temp_reminder_times[2] -= 1
                    temp_reminder_times[3] += (23 - unit_change)
                if time_type_affected >= 3:
                    unit_change = 1
                if temp_reminder_times[2] - unit_change < 1:
                    temp_reminder_times[1] -= 1
                    # Fixes year if original month was January
                    if temp_reminder_times[1] == 0:
                        temp_reminder_times[0] -= 1
                        temp_reminder_times[1] = 12
                    # Checks 30 day months
                    if temp_reminder_times[1] == 4 or temp_reminder_times[1] == 6 or temp_reminder_times[1] == 9 or temp_reminder_times[1] == 11:
                        temp_reminder_times[2] += (30 - unit_change)
                    # Checks February
                    elif temp_reminder_times[1] == 2:
                        # Normal years
                        if (temp_reminder_times[0] % 4) != 0:
                            temp_reminder_times[2] += (28 - unit_change)
                        # Leap years
                        else:
                            temp_reminder_times[2] += (29 - unit_change)
                    # Other years
                    else:
                        temp_reminder_times[2] += (31 - unit_change)

        return temp_reminder_times


access_token = "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"
g = Github(access_token)

# Gets repo and file from github
repo = g.get_user().get_repo("SyncNote")
file = repo.get_contents("text_file.txt")

# Sets date and time variables
date = dt.datetime.now()
human_readable_date = date.strftime('%X %d/%m/%y')
# Gives number of seconds since 00:00:00 1/1/2000 for comparison against other updates
update_time = int(int(date.strftime('%S')) + 60*(int(date.strftime('%M'))+60*(int(date.strftime('%H'))+24*(int(date.strftime('%j'))+365.25*(int(date.strftime('%y')))))))


def local_file_analysis():
    # Gets text from local syncnote text file or input and adds to variables
    main_file = open((file_location + 'syncnote_local_file.txt'), 'r')
    all_tasks = []
    base_data = ''
    top_two_lines = ''
    # Checks if file is empty
    main_file.seek(0)
    first_character_check = main_file.read(1)
    if not first_character_check:
        messagebox.showinfo(title='SyncNote', message='Local file empty\nSyncing with Github')
        return 'Do Sync', []
    else:
        line_num = 0
        for line in main_file:
            if line_num < 2:
                top_two_lines = top_two_lines + line
            else:
                base_data = base_data + line
            line_num += 1
        top_two_lines = top_two_lines.rstrip('\n')
        all_data = ast.literal_eval(base_data.rstrip('\n'))
        all_tasks = all_data[0]

    task_number.set(len(all_tasks))
    task_list_preview = []
    x = 0
    while x < task_number.get():
        # The function f"{_:02}" converts integers into two digit strings, e.g. 3 -> '03'
        processed_date = f"{all_tasks.copy()[x][1][3]:02}" + ':' + f"{all_tasks.copy()[x][1][4]:02}" + ' | ' + f"{all_tasks.copy()[x][1][2]:02}" + '/' + f"{all_tasks.copy()[x][1][1]:02}" + '/20' + f"{all_tasks.copy()[x][1][0]:02}"
        task_list_preview.append([all_tasks.copy()[x][0], processed_date, all_tasks.copy()[x][4], all_tasks.copy()[x][5]])
        x += 1
    main_file.close()
    return all_data, task_list_preview


# Syncs github data
def sync_github_file(startup):
    # Gets text from local syncnote text file or input and adds to variables
    data_file = open((file_location + 'syncnote_local_file.txt'), 'r')
    changes = 'Synced with local file'
    # Checks if file is empty
    data_file.seek(0)
    first_character = data_file.read(1)
    text_data = ''
    if not first_character:
        stored_update_time = 1
    else:
        data_file.seek(0)
        for line in data_file:
            text_data = text_data + line
        stored_update_time = int(text_data.split('\n')[1])
    data_file.close()

    # Reads github file
    raw_url = 'https://raw.githubusercontent.com/ZeroRelevance/SyncNote/main/text_file.txt'
    read_data = str(requests.get(raw_url).content)
    # Clears any unwanted symbols at the start and end of the read data
    read_data = read_data.lstrip("b'").rstrip("'").lstrip('"').rstrip('"').replace('\\n', '\n')
    github_changes = read_data.split('\n')[0]
    if read_data.count('\n') < 2:
        github_update_time = 1
    else:
        github_update_time = int(read_data.split('\n')[1])
    github_text_data = read_data.replace(github_changes + '\n' + str(github_update_time) + '\n', '')

    # Updates github file if github file date is older than current date
    if github_update_time < stored_update_time:
        repo.update_file("text_file.txt", changes, text_data, file.sha)
        messagebox.showinfo(title='SyncNote', message='Updated github contents')

    elif github_update_time == stored_update_time:
        messagebox.showinfo(title='SyncNote', message='Github and Local Files are already synced')

    # Updates local file if github contents are newer (Does not use else because if the times are the same, then there is no need to update)
    else:
        github_date = dt.datetime.now()
        github_human_readable_date = github_date.strftime('%X %d/%m/%y')
        data_file_e = open((file_location + 'syncnote_local_file.txt'), 'w')
        new_data = 'Updated from Github at ' + github_human_readable_date + '\n' + str(github_update_time) + '\n' + github_text_data
        data_file_e.write(new_data)
        data_file_e.close()

        # Updates task list
        all_data, task_list_preview = local_file_analysis()
        messagebox.showinfo(title='SyncNote', message='Updated local file contents')
        all_tasks = all_data[0]
        settings = all_data[1]
        task_number.set(len(all_tasks))

        if not startup:
            task_list.delete(*task_list.get_children())
            for i in range(len(task_list_preview)):
                task_list.insert(parent='', index=END, iid=i, text='', values=task_list_preview[i])


# Updates local file. _lf signifies local file
def update_local_file(title, due_date, details, completed, input_id, latest_change_lf):
    # Creates a new ID so the next task doesn't share the same ID
    id_box.config(state="normal")
    id_box.delete("1.0", END)
    id_box.insert("1.0", (' ID: ' + str(r.randint(0, 9999999))))
    id_box.config(state="disabled")

    # Updates all_data and task_list_preview so task list can update, and makes list of ids to check against
    all_data, task_list_preview = local_file_analysis()
    all_tasks = all_data[0]
    settings = all_data[1]

    all_ids = []
    for i in range(len(all_tasks)):
        all_ids.append(all_tasks[i][5])

    date_lf = dt.datetime.now()
    human_readable_date_lf = date.strftime('%X %d/%m/%y')
    # Gives number of seconds since 00:00:00 1/1/2000 for comparison against other updates
    update_time_lf = int(int(date_lf.strftime('%S')) + 60*(int(date_lf.strftime('%M'))+60*(int(date_lf.strftime('%H'))+24*(int(date_lf.strftime('%j'))+365.25*(int(date_lf.strftime('%y')))))))

    # Updates file
    data_file_e_lf = open((file_location + 'syncnote_local_file.txt'), 'w')
    created_task = Task(title, due_date.copy(), details, completed, input_id).create_task()

    # Checks if id exists in set and replaces prior task if so
    if created_task[5] in all_ids:
        all_tasks[all_ids.index(created_task[5])] = created_task.copy()
    else:
        all_tasks.append(created_task)

    # Update the file
    new_data_lf = 'Latest Change: ' + latest_change_lf + ' | Change Made At: ' + human_readable_date_lf + '\n' + str(update_time_lf) + '\n' + str(all_data)
    data_file_e_lf.write(new_data_lf)
    data_file_e_lf.close()

    # Updates task list
    task_number.set(len(all_tasks))
    all_data, task_list_preview = local_file_analysis()
    messagebox.showinfo(title='SyncNote', message='Updated local file contents')

    if all_data == 'Do Sync':
        sync_github_file(False)
    else:
        task_list.delete(*task_list.get_children())
        for i in range(len(task_list_preview)):
            task_list.insert(parent='', index=END, iid=i, text='', values=task_list_preview[i])


# Creates task when button is pressed
def create_task_request():
    if date_year.get() != "Year" and (date_month.get() in all_months) and date_day.get() != "Day" and date_hour != "Hour" and date_minute.get() != "Minute":
        task_creation_year = int(date_year.get()) - 2000
        task_creation_month = int(all_months.index(date_month.get())) + 1
        input_id = int(id_box.get("1.5", END))
        is_completed = (completed_box.get("1.12", END).rstrip('\n') == 'True')
        # Makes sure date is possible
        if task_creation_month in {4, 6, 9, 11} and int(date_day.get()) > 30:
            messagebox.showwarning(title='SyncNote', message=(date_month.get() + ' does not have 31 days'))
        elif task_creation_month == 2 and int(date_day.get()) > 29 and task_creation_year % 4 == 0:
            messagebox.showwarning(title='SyncNote', message=('February does not have ' + date_day.get() + ' days in the year ' + date_year.get()))
        elif task_creation_month == 2 and int(date_day.get()) > 28 and task_creation_year % 4 != 0:
            messagebox.showwarning(title='SyncNote', message=('February does not have ' + date_day.get() + ' days in the year ' + date_year.get()))
        else:
            task_creation_date = [task_creation_year, task_creation_month, int(date_day.get()), int(date_hour.get()), int(date_minute.get())].copy()
            update_local_file(title_entry_box.get(), task_creation_date.copy(), details_entry_box.get("1.0", END).rstrip('\n'), is_completed, input_id, 'Created New Task')
    else:
        messagebox.showwarning(title='SyncNote', message="Please select a value for all dates")


all_data, task_list_preview = local_file_analysis()
if all_data != 'Do Sync':
    all_tasks = all_data[0]
    settings = all_data[1]
else:
    sync_github_file(True)
    all_data, task_list_preview = local_file_analysis()
    all_tasks = all_data[0]
    settings = all_data[1]

title = Label(text="SyncNote", font=("Roboto Light", 14))
title.grid(column=0, row=0, padx=10, pady=10, columnspan=3, sticky="w")

sync_button = Button(text="Sync Github", command=lambda: sync_github_file(False))
sync_button.grid(column=3, row=0, padx=15, pady=5, columnspan=2, sticky="e")

title_entry_box = Entry(font=("Roboto Light", 11), width=43)
title_entry_box.grid(column=0, row=1, padx=5, pady=5, columnspan=5)
title_entry_box.insert(0, "Enter Title")

date_year = Combobox(values=all_numbers_2000_to_2099, width=6, state="readonly")
date_month = Combobox(values=all_months, width=10, state="readonly")
date_day = Combobox(values=all_numbers_1_to_31, width=5, state="readonly")
date_hour = Combobox(values=all_numbers_0_to_23, width=5, state="readonly")
date_minute = Combobox(values=all_numbers_0_to_59, width=7, state="readonly")

date_year.grid(column=0, row=2, padx=(8, 1), pady=5)
date_month.grid(column=1, row=2, padx=1, pady=5)
date_day.grid(column=2, row=2, padx=1, pady=5)
date_hour.grid(column=3, row=2, padx=1, pady=5)
date_minute.grid(column=4, row=2, padx=(1, 2), pady=5)

date_year.set("Year")
date_month.set("Month")
date_day.set("Day")
date_hour.set("Hour")
date_minute.set("Minute")

details_entry_box = Text(font=("Roboto Light", 10), width=50, height=6.5)
details_entry_box.grid(column=0, row=3, padx=10, pady=5, columnspan=5)
details_entry_box.insert("1.0", "Enter Description")

id_box = Text(font=("Roboto", 10), width=11, height=1)
id_box.grid(column=0, row=4, padx=10, columnspan=2, sticky='w')
id_box.insert(INSERT, (' ID: ' + str(r.randint(0, 9999999))))
id_box.config(state="disabled")

completed_box = Text(font=(" Roboto", 10), width=16, height=1)
completed_box.grid(column=3, row=4, padx=0, columnspan=3, sticky='w')
completed_box.insert(INSERT, ' Completed: False')
completed_box.config(state="disabled")

enter_button = Button(text="Enter", command=lambda: create_task_request())
enter_button.grid(column=0, row=4, padx=25, pady=5, columnspan=3, sticky='e')

task_list = Treeview(show='headings')
task_list['columns'] = ("Title", "Due Date", "Completed", "ID")


# Selects a task when a task in task_list is double clicked
def select_task(e):
    selected_task_index = task_list.focus()
    print(selected_task_index)
    if selected_task_index != '':
        # Updates all_tasks file
        all_data, task_list_preview = local_file_analysis()
        all_tasks = all_data[0]

        # Sets all values on page to selected task's values
        selected_task = all_tasks[int(selected_task_index)]
        title_entry_box.delete(0, END)
        title_entry_box.insert(INSERT, selected_task[0])

        date_year.set(str(selected_task[1][0]+2000))
        date_month.set(all_months[selected_task[1][1]-1])
        date_day.set(str(selected_task[1][2]))
        date_hour.set(str(selected_task[1][3]))
        date_minute.set(str(selected_task[1][4]))

        details_entry_box.delete("1.0", END)
        details_entry_box.insert(INSERT, selected_task[2])

        completed_box.config(state="normal")
        completed_box.delete("1.0", END)
        completed_box.insert(INSERT, (' Completed: ' + str(selected_task[4])))
        completed_box.config(state="disabled")

        id_box.config(state="normal")
        id_box.delete("1.0", END)
        id_box.insert(INSERT, (' ID: ' + str(selected_task[5])))
        id_box.config(state="disabled")


# Similar to above task, but instead resets everything
def reset_task_editor():
    # Sets all values on page to default values
    title_entry_box.delete(0, END)
    title_entry_box.insert(INSERT, 'Enter Title')

    date_year.set("Year")
    date_month.set("Month")
    date_day.set("Day")
    date_hour.set("Hour")
    date_minute.set("Minute")

    details_entry_box.delete("1.0", END)
    details_entry_box.insert(INSERT, 'Enter Description')

    completed_box.config(state="normal")
    completed_box.delete("1.0", END)
    completed_box.insert(INSERT, ' Completed: False')
    completed_box.config(state="disabled")

    id_box.config(state="normal")
    id_box.delete("1.0", END)
    id_box.insert(INSERT, (' ID: ' + str(r.randint(0, 9999999))))
    id_box.config(state="disabled")


task_list.column('#0', width=0)
task_list.column('Title', width=200, minwidth=200, anchor=W)
task_list.column('Due Date', width=120, minwidth=120, anchor=CENTER)
task_list.column('Completed', width=70, minwidth=70, anchor=W)
task_list.column('ID', width=60, minwidth=60, anchor=CENTER)

task_list.heading('#0', text='Label')
task_list.heading('Title', text='Title', anchor=W)
task_list.heading('Due Date', text='Due Date', anchor=CENTER)
task_list.heading('Completed', text='Completed', anchor=W)
task_list.heading('ID', text='ID', anchor=CENTER)

for i in range(len(task_list_preview)):
    task_list.insert(parent='', index=END, iid=i, text='', values=task_list_preview[i])

task_list.grid(column=5, row=0, padx=10, pady=10, columnspan=8, rowspan=4)

reset_task_button = Button(text="Clear Task", command=lambda: reset_task_editor())
reset_task_button.grid(column=2, row=0, padx=5, pady=5, columnspan=2)

# Activates select_task() on double click on a task
task_list.bind("<Double-1>", select_task)


# Also works when multiple tasks are selected
def delete_complete_tasks(type):
    # Updates all_tasks file
    all_data, task_list_preview = local_file_analysis()
    all_tasks = all_data[0]
    settings = all_data[1]

    # Saves indices of selected task to variable
    selected = task_list.selection()
    # Adds each selected task to a list
    selected_tasks = []
    for i in range(len(selected)):
        selected_tasks.append(all_tasks[int(selected[i])].copy())
    if type == 'delete':
        # Deletes tasks
        for i in range(len(selected_tasks)):
            all_tasks.pop(all_tasks.index(selected_tasks[i]))
    elif type == 'complete':
        # Marks completed
        for i in range(len(selected_tasks)):
            all_tasks[all_tasks.index(selected_tasks[i])][4] = not all_tasks[all_tasks.index(selected_tasks[i])][4]
    elif type == 'delete completed':
        completed_tasks = []
        # Assigns all completed tasks to an array
        for i in range(len(all_tasks)):
            print(len(all_tasks) - (i + 1))
            if all_tasks[len(all_tasks) - (i + 1)][4]:
                completed_tasks.append(all_tasks[len(all_tasks) - (i + 1)])
        # Deletes all completed tasks
        for i in range(len(completed_tasks)):
            all_tasks.pop(all_tasks.index(completed_tasks[i]))

    date_lf = dt.datetime.now()
    human_readable_date_lf = date.strftime('%X %d/%m/%y')
    # Gives number of seconds since 00:00:00 1/1/2000 for comparison against other updates
    update_time_lf = int(int(date_lf.strftime('%S')) + 60*(int(date_lf.strftime('%M'))+60*(int(date_lf.strftime('%H'))+24*(int(date_lf.strftime('%j'))+365.25*(int(date_lf.strftime('%y')))))))

    # Updates file
    data_file_e_lf = open((file_location + 'syncnote_local_file.txt'), 'w')

    all_data = [all_tasks, settings]

    # Update the file
    if len(selected) == 0:
        new_data_lf = 'Latest Change: Altered 1 Task | Change Made At: ' + human_readable_date_lf + '\n' + str(update_time_lf) + '\n' + str(all_data)
    else:
        new_data_lf = 'Latest Change: Altered ' + str(len(selected)) + ' Tasks | Change Made At: ' + human_readable_date_lf + '\n' + str(update_time_lf) + '\n' + str(all_data)
    data_file_e_lf.write(new_data_lf)
    data_file_e_lf.close()

    # Updates task list
    task_number.set(len(all_tasks))
    all_data, task_list_preview = local_file_analysis()
    if type == 'delete':
        messagebox.showinfo(title='SyncNote', message='Deleted selected tasks')
    elif type == 'complete':
        messagebox.showinfo(title='SyncNote', message='Marked selected tasks completed')
    elif type == 'delete completed':
        messagebox.showinfo(title='SyncNote', message='Deleted all completed tasks')

    if all_data == 'Do Sync':
        sync_github_file(False)
    else:
        task_list.delete(*task_list.get_children())
        for i in range(len(task_list_preview)):
            task_list.insert(parent='', index=END, iid=i, text='', values=task_list_preview[i])


delete_button = Button(text='Delete Selected Task', command=lambda: delete_complete_tasks('delete'))
complete_button = Button(text='Mark Selected Task Completed', command=lambda: delete_complete_tasks('complete'))
delete_completed_button = Button(text='Delete All Completed Tasks', command=lambda: delete_complete_tasks('delete completed'))

delete_button.grid(column=8, row=4, columnspan=2, padx=(5, 0))
complete_button.grid(column=10, row=4, columnspan=2, padx=(5, 0))
delete_completed_button.grid(column=12, row=4, columnspan=2, padx=(5, 10))

window.mainloop()
