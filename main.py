import pandas as pd
from datetime import date, datetime, timedelta
import calendar
import numpy as np
import os
import sys

pd.options.mode.chained_assignment = None


class ToDoList:
    def __init__(self):
        self.my_date = date.today()
        self.current_day_of_week = calendar.day_name[self.my_date.weekday()]
        self.now = datetime.now()
        self.add_events()
        self.update_time()
        self.check_update()

    def run(self):
        while True:
            data = pd.read_csv("current_events.txt")
            df = pd.DataFrame(data)
            choice_to = input(
                "\n1 - View current event\n2 - View the upcomming event\n3 - Mark tasks complete\n4 - View todays schedule\n5 - Remove all events from event list\n6 - Exit\n>> "
            )
            self.clear_screen()
            if choice_to == "1":
                self.view_current_event(df)
            elif choice_to == "2":
                index_of_event = self.get_events(df)
                if index_of_event != "Invalid":
                    print("\nUpcomming/current event\n")
                    print(df.iloc[index_of_event])
                    self.delete_line()
                else:
                    print("\nYou have no events left for today!\n")
            elif choice_to == "3":
                self.get_nonstat_event(df)
            elif choice_to == "4":
                print()
                df = df[df["Day Of Week"] == self.current_day_of_week]
                df = df.set_index(np.arange(1, len(df.index) + 1))
                if len(df) > 0:
                    print(df)
                else:
                    print("Nothing on todays schedule")
            elif choice_to == "5":
                print("Clearning all events")
                with open("current_events.txt", "w") as f:
                    f.write("Day Of Week,Start Time,Event Name,Status\n")

            elif choice_to == "6":
                break
            else:
                print("\nInvalid!\n")

    def clear_screen(self):
        os.system("clear")

    def check_update(self):
        if self.current_day_of_week == "Monday":
            with open("last_updated.txt", "r") as f:
                day_last_updated = f.read()
            if day_last_updated == str(self.my_date - timedelta(days=7)):
                with open("last_updated.txt", "w") as f:
                    f.write(str(self.my_date))
                data = pd.read_csv("current_events.txt")
                df = pd.DataFrame(data)
                list1 = []
                for _ in range(len(df)):
                    list1.append(" None")
                df["Status"] = list1
                with open("current_events.txt", "w") as f:
                    f.write("Day Of Week,Start Time,Event Name,Status\n")
                df.to_csv("current_events.txt", mode="a", index=False, header=False)

    def get_events(self, df):
        df = df[df["Day Of Week"] == self.current_day_of_week]
        df["Start Time"] = df["Start Time"].map(lambda x: pd.to_datetime(x.strip()))
        df = df.sort_values("Start Time")
        try:
            index_of_next = df[df["Start Time"].gt(self.now)].index[0]
        except IndexError:
            index_of_next = "Invalid"
        return index_of_next

    def delete_line(self):
        CURSOR_UP_ONE = "\x1b[1A"
        ERASE_LINE = "\x1b[2K"
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)

    def update_time(self):
        data = pd.read_csv("current_events.txt")
        df = pd.DataFrame(data)
        df = df[df["Status"] == " None"]
        df = df.set_index(np.arange(len(df.index)))
        with open("current_events.txt", "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if "None" not in i:
                    f.write(i)
            f.truncate()
        df["Start Time"] = df["Start Time"].map(lambda x: pd.to_datetime(x.strip()))
        df = df.sort_values("Start Time")
        df = df.set_index(np.arange(len(df.index)))
        for i in range(len(df)):
            time_i = str(df["Start Time"].iloc[i])
            timeZ = time_i.split()
            timeZ.pop(0)
            dz = datetime.strptime(timeZ[0], "%H:%M:%S")
            x = dz.strftime("%I:%M %p")
            df["Start Time"].iloc[i] = x
        df.to_csv("current_events.txt", mode="a", index=False, header=False)

    def get_nonstat_event(self, df):
        print("\n")
        df1 = df[df["Day Of Week"] == self.current_day_of_week]
        indexNames = df[df["Day Of Week"] == self.current_day_of_week].index
        df.drop(indexNames, inplace=True)
        df1 = df1[df1["Status"] == " None"]
        df1 = df1.set_index(np.arange(len(df1.index)))
        with open("current_events.txt", "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if "None" not in i:
                    f.write(i)
            f.truncate()
        df1["Start Time"] = df1["Start Time"].map(lambda x: pd.to_datetime(x.strip()))
        df1 = df1.sort_values("Start Time")
        df1 = df1.set_index(np.arange(len(df1.index)))
        for i in range(len(df1)):
            time_i = str(df1["Start Time"].iloc[i])
            timeZ = time_i.split()
            timeZ.pop(0)
            dz = datetime.strptime(timeZ[0], "%H:%M:%S")
            x = dz.strftime("%I:%M %p")
            df1["Start Time"].iloc[i] = x
        if len(df1) > 0:
            print("You have", len(df1), "events unfinished")
            for i in range(len(df1)):
                row_i = df1.iloc[i]
                print(row_i)
                self.delete_line()
                self.delete_line()
                event_done = input(
                    "Has the above event been finished?(Y or N): "
                ).upper()
                if event_done == "Y":
                    print("Marking event as done!")
                    df1["Status"].iloc[i] = " Done"
                elif event_done == "N":
                    print("Don't forget to finish it!")
                print()
        else:
            print("No events left to mark done")
        dataframes = [df, df1]
        df3 = pd.concat(dataframes)
        df3.to_csv("current_events.txt", mode="a", index=False, header=False)

    def add_events(self):
        data = pd.read_csv("add_events.txt")
        if len(data) < 40:
            print("There are no events being added")
        else:
            print("Adding events!")
            data.insert(3, "Status", [" None" for _ in range(len(data))])
            df = pd.DataFrame(data)
            df.to_csv("current_events.txt", mode="a", index=False, header=False)
            with open("add_events.txt", "w") as f:
                f.write("Day Of Week, Start Time, Event Name")

    def view_current_event(self, df):
        df = df[df["Day Of Week"] == self.current_day_of_week]
        df["Start Time"] = df["Start Time"].map(lambda x: pd.to_datetime(x.strip()))
        df = df[df["Start Time"].le(self.now)]
        for i in range(len(df)):
            time_i = str(df["Start Time"].iloc[i])
            timeZ = time_i.split()
            timeZ.pop(0)
            dz = datetime.strptime(timeZ[0], "%H:%M:%S")
            x = dz.strftime("%I:%M %p")
            df["Start Time"].iloc[i] = x
        df = pd.DataFrame(df.tail(1))
        try:
            print(df.iloc[0])
            self.delete_line()
        except IndexError:
            print("No current tasks")


myToDoList = ToDoList()
myToDoList.run()
