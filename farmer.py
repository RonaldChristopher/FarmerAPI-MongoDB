__author__ = 'LOKESH KUMAR PM'

import pymongo
from pymongo import MongoClient, GEO2D
from bson.son import SON
from tkinter import *
import tkinter.messagebox

# Creating the Frame and the respective GUI components

root = Tk()  # The Tkinter GUI object
root.geometry('560x250+500+100')
root.title('KISAN-MITRA')

# The Labels in the GUI

one = Label(root, text="THINGS TO REMEMBER & FOLLOW :", fg="red")
one.place(x=0, y=80)

two = Label(root, text="                            Enter the current location/Market Center", bg="white", fg="black")
two.place(x=0, y=0)

three = Label(root, text="                                                          Enter the required price",
              bg="white", fg="black")
three.place(x=0, y=20)

four = Label(root, text="                Enter the offered price at current Market Center", bg="white", fg="black")
four.place(x=0, y=40)

five = Label(root, text="Please Note that all Prices measured in Rs/Quintal", fg="blue")
five.place(x=0, y=100)

six = Label(root, text="Select the commodity only in the end after entering all other details", fg="brown")
six.place(x=0, y=120)

seven = Label(root, text="Click on the find button only after checking whether your commodity is selected", fg="brown")
seven.place(x=0, y=140)

l4 = Label(root, text="select the commodity", bg="green", fg="black")
l4.place(x=430, y=0)

# The Entry Boxes

ent = Entry(root)
ent1 = Entry(root)
ent2 = Entry(root)
ent.place(x=305, y=0)
ent1.place(x=305, y=20)
ent2.place(x=305, y=40)


# List Box for selecting the commodities

lc = Listbox(root)

# Creating the MongoDB client and connecting to the collections

db = MongoClient().project1  # The MongoDB Client object
mkct = db.marktcentre.find()  # The marketcentre collection
coll = db.commodity.find()  # The commodities collection

# adding the commodities list to the Listbox created

for item in coll:
    lc.insert(END, item['Commodity'])

lc.place(x=430, y=20)


def task1():
    com = lc.get(ACTIVE)  #the selected commodity in the ListBox

    locn = ent.get()  # the location entered by the user
    print(locn)

    c1 = 0

    # For retrieving the coordinates of the location if the entry is legitimate
    for it in mkct:
        if locn.lower() == (it['Market Center']).lower():
            loc = it['Market Center']
            coord = it['Loc']
            c1 = 1
            break

    if c1 == 0:
        print("Sorry Market Center Unavailable; check spelling or choose another nearby center")
        tkinter.messagebox.showinfo('oh no!!!',
                                    'Sorry Market Center Unavailable; check spelling or choose another nearby center')
    else:
        print(loc, coord)

        try:

            rp = int(ent1.get())  # Required Price by the farmer

            print(rp)

            op = int(ent2.get())  # The Offered Price for the farmer's commodity

            c = 0  # 'c' is the check varible

            dem = 0

            demdb = db.demand.find()  # the demand collection stored in MongoDB

            # To find the demand of the respective selected commodity
            for i in demdb:
                if i['Commodity'] == com:
                    dem = i['Demand']
                    break

            # Analysing the demand of the commodity

            if dem == 0:
                c = 1
            elif (dem > 0) & (dem < 3):
                c = 1
            elif dem >= 3:
                c = 2
            elif (dem < 0) & (dem > -3):
                c = -1
            elif dem <= -3:
                c = -2


            print(c)

            print(op)

            # The historical data collection of the past prices across all the market centers which is stored in MongoDB
            histdata = db.southindia1.find()

            # a set of temporary variables
            t4 = 0
            t5 = 0
            t6 = 0
            h = 0

            # Analysing the Historical Data and analysing it suitably to find its impact in making the decision
            for i in histdata:
                if i['Commodity'] == com:
                    h = h + 1
                    if i['Modal Price'] >= rp:
                        t4 = t4 + 1
                        t5 = t5 + 1
                    else:
                        t4 = t4 - 1
                        t6 = t6 - 1

            #print(t4, t5, t6, h)

            c2 = t4 / h  # The historical data effect on decision making

            c = c + c2  # The combination of "demand" and "historical data" collections
            #print(c)

            # Creating the Geo Spatial Index of all the marketcenters using MongoDB Geo-Spatial features

            db.curpr.create_index([('Loc', GEO2D)])

            # Based on the value of "c"  the marketcenters are searched in different radius.
            if c >= 2:
                temp = db.curpr.find({"Loc": SON([("$near", coord), ("$maxDistance", 2000)])}).limit(
                    2500)  # Search in 2000 Km radius
            elif (c >= 1) & (c < 2):
                temp = db.curpr.find({"Loc": SON([("$near", coord), ("$maxDistance", 1200)])}).limit(
                    2500)  # Search in 1200 Km radius
            elif (c >= 0) & (c < 1):
                temp = db.curpr.find({"Loc": SON([("$near", coord), ("$maxDistance", 700)])}).limit(
                    2500)  # Search in 700 Km radius
            elif (c >= -1) & (c < 0):
                temp = db.curpr.find({"Loc": SON([("$near", coord), ("$maxDistance", 400)])}).limit(
                    2500)  # Search in 400 Km radius
            elif (c >= -2) & (c < -1):
                temp = db.currntprice.find({"Loc": SON([("$near", coord), ("$maxDistance", 250)])}).limit(
                    2500)  # Search in 250 Km radius
            elif c < -2:
                temp = db.currntprice.find({"Loc": SON([("$near", coord), ("$maxDistance", 150)])}).limit(
                    2500)  # Search in 150 Km radius

            mc = []  # variable to marketcenters
            cm = []  # variable to commodities
            pr = []  # variable to price
            n = 0  # To store number of suitable locations found in search
            k = 0

            # To find all the market centers that are offering the commodity a higher price for purchase

            if rp <= op:
                k = 0
            else:
                k = 1

            for i in temp:
                if i['Commodity'] == com:
                    if i['Modal Price'] > rp:
                        cm.append(i['Commodity'])
                        pr.append(i['Modal Price'])
                        mc.append(i['Market Center'])
                        n = n + 1

            p = 250
            a1 = StringVar()
            ta = StringVar()
            st1 = []

            if n==0:  #  To check whether the number of hits found is non-zero.
                tkinter.messagebox.showinfo('Result',
                                                'The current location is the right location to sell the commodity')
            else:   #    Proceed as per algorithm

                # For Finding the average selling price of the commodity in the search radius
                sum = 0
                for i in range(n):
                    sum += pr[i]

                avg_pr = sum/n


                try:
                    h1 = max(pr)  # To find the highest price in the prices list.
                except ValueError:
                    tkinter.messagebox.showinfo('Result',
                                                'The current location is the right location to sell the commodity')
                    k = 2

                if k == 1:
                    for i in range(n):
                        if h1 == pr[i]:
                            ta = "the best location would be " + mc[i] + " where the current price is " + str(pr[i])+" while the average selling price is "+str(round(avg_pr))
                            print("the best location would be ", mc[i], " where the current price is ", str(pr[i]))
                            tkinter.messagebox.showinfo('Result', ta)
                elif k == 0:
                    if op >= h1:
                        tkinter.messagebox.showinfo('Result',
                                                    'The current location is the right location to sell the commodity')

                    else:
                        k = 1
                        for i in range(n):  # To display the location where maximum price can be fetched
                            if h1 == pr[i]:
                                ta = "the best location would be " + mc[i] + " where the current price is " + str(pr[i])
                                print("the best location would be ", mc[i], " where the current price is ", str(pr[i]))
                                tkinter.messagebox.showinfo('Result', ta)

                if k == 1:
                    status = Label(root, text="Query Performed!!! Thank You!!!", bd=1, relief=SUNKEN, anchor=W)
                    status.pack(side=BOTTOM, fill=X)
                    root1 = Tk()
                    root1.title('Alternative Locations')
                    mlabel1 = Label(root1, text='Alternative locations for the goods could be sold are :', bg='yellow',
                                    fg="black")
                    mlabel1.grid(row=0, column=0)

                    for i in range(n):
                        a1 = cm[i] + ' @' + mc[i] + ' the price is ' + str(pr[i])
                        print(a1)
                        mlabel = Label(root1, text=a1, fg="black")
                        mlabel.grid(row=i + 1, column=0, sticky=W)

                # If the user enters a text in the Required price and offered price entry fields
        except ValueError:
            tkinter.messagebox.showinfo('oh no!!!', 'Please Check and Enter the Proper Details  (Hint: Check the Required Price and Offered Price fields)')


# The button and Statusbar GUI features

button1 = Button(root, text="find", width=10, command=task1)
button1.place(x=125, y=170)
qb = Button(root, text="exit", width=10, command=root.quit)
qb.place(x=230, y=170)
status = Label(root, text="Ready to Help You!!!", bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)
root.mainloop()