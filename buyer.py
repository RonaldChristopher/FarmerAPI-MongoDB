__author__ = 'LOKESH KUMAR PM'

from pymongo import MongoClient, GEO2D
from tkinter import *
import tkinter.messagebox


# Creating the Frame and its components

root3 = Tk() # The Tkinter GUI object
root3.geometry('560x225+500+100')
root3.title('KISAN-MITRA')

one = Label(root3, text="THINGS TO REMEMBER & FOLLOW :", fg="red")
one.place(x=0, y=80)

two = Label(root3, text="Enter Your current location/Market Center", fg="black")
two.place(x=0, y=0)

three = Label(root3,
              text="Enter the quantity of commodity you require", fg="black")
three.place(x=0, y=20)

four = Label(root3, text="Enter the price you are willing to offer",fg="black")
four.place(x=0, y=40)

five = Label(root3, text="Please Note that all Prices measured in Rs/Quintal", fg="blue")
five.place(x=0, y=100)

six = Label(root3, text="Select the commodity only in the end after entering all other details", fg="brown")
six.place(x=0, y=120)

seven = Label(root3, text="Click on the find button only after checking whether your commodity is selected", fg="brown")
seven.place(x=0, y=140)

# The Entry Boxes

ent3 = Entry(root3, width=50)
ent3.place(x=250, y=0)

ent4 = Entry(root3, width=50)
ent4.place(x=250, y=20)

ent5 = Entry(root3, width=50)
ent5.place(x=250, y=40)

l4 = Label(root3, text="select the commodity", bg="green", fg="black")
l4.place(x=430, y=0)

# List Box for selecting the commodities

lc = Listbox(root3)

# Creating the MongoDB client and connecting to the collections

db = MongoClient().project1  # The MongoDB Client object
mkct = db.marktcentre.find() # The marketcentre collection
coll = db.commodity.find()   # The commodities collection

# adding the commodities list to the Listbox created

for item in coll:
    lc.insert(END, item['Commodity'])

lc.place(x=430, y=20)



# The function that will perform the necessary buyer related operations

def buyer_task():

    com = lc.get(ACTIVE) #the selected commodity in the ListBox

    locn = ent3.get()   # the location entered by the user
    print(locn)

    c1 = 0
    state = StringVar()

    # For retrieving the coordinates of the location if the entry is legitimate
    for it in mkct:
        if locn.lower() == (it['Market Center']).lower():
            loc = it['Market Center']
            coord = it['Loc']
            state = it['State']
            c1 = 1
            break

    if c1 == 0:
        print("Sorry Market Center Unavailable; check spelling or choose another nearby center")
        tkinter.messagebox.showinfo('oh no!!!',
                                    'Sorry Market Center Unavailable; check spelling or choose another nearby center')
    else:
        print(loc, coord)

        try:
            quant = int(ent4.get()) # quantity needed by the by the buyer

            bp = int(ent5.get()) # the buyers offering price

            print(quant)

            cd = 0

            demdb = db.demand.find()  # the demand collection stored in MongoDB

            dem = 0

            for i in demdb:
                if i['Commodity'] == com:
                    dem = i['Demand']
                    break

            print(dem)

            # Analysing the quantity needed by the buyer and suitably finding its psiible impact on the demand of the commodity

            if quant <= 300:
                cd = 0.05
            elif (quant <= 500) & (quant > 300):
                cd = 0.25
            elif (quant <= 5000) & (quant > 500):
                cd = 0.5
            elif (quant <= 10000) & (quant > 5000):
                cd = .75
            elif (quant > 10000) & (quant <= 20000):
                cd = 1.0
            elif (quant > 20000) & (quant <= 30000):
                cd = 1.25
            elif quant > 30000:
                cd = 1.5

            # Updating the demand of the commodity as per the quantity needed by the Buyer

            db.demand.update_one({'Commodity': com}, {'$inc': {'Demand': cd}})

            demdb = db.demand.find()
            dem = 0
            for i in demdb:
                if i['Commodity'] == com:
                    dem = i['Demand']
                    break

            print(dem)

            temp2 = db.curpr.find() # the Commodities current price collection stored in MongoDB
            k = 0 # Check variable

            # To check whether the Commodity exists in that particular location

            for i in temp2:
                if i['Market Center'] == loc:
                    if com != i['Commodity']:
                        k = 1
            obj = StringVar()
            t1 = dict()

            if k == 1:  # If at at the location the commodity doesn't exist then enter the details in the current database
                t1 = {'Market Center': loc, 'Loc': coord, 'Modal Price': bp, 'Commodity': com, 'State' : state,'Unit of Price' : "Rs/Quintal" }
                db.curpr.insert_one(t1)
            else:
                for i in temp2: # Checking if the price offered by the Buyer is greater than currently being offered price at that location
                    if loc == i['Market Center']:
                        if i['Commodity'] == com:
                            if i['Modal Price'] < bp:
                                obj = i['_id']
                                print(i)
                                t1 = {'Market Center': loc, 'Loc': coord, 'Modal Price': bp, 'Commodity': com, 'State' : state,'Unit of Price' : "Rs/Quintal" }
                                db.curpr.replace_one({'_id': obj}, t1) # Upadating the Users Price as Currently offered price in Mongodb

            dict1 = {'Market Center': loc, "Requirement": quant, "Loc": coord, "Modal Price": bp, "Commodity": com}

            # adding the Buyers entered details in Buyer collection of MongoDB

            db.buyer.insert_one(dict1)
            tkinter.messagebox.showinfo('Details Added!!!',
                                        'Your needs and entered details have been added successfully to the database')


        except ValueError:
            tkinter.messagebox.showinfo('oh no!!!',
                                    'Please Check and Enter the Proper Details  (Hint: Check the Quantity and Offered Price fields)')

# The button and Statusbar GUI features
button1 = Button(root3, text="done", width=10, command=buyer_task)
button1.place(x=125, y=170)
qb1 = Button(root3, text="exit", width=10, command=root3.quit)
qb1.place(x=230, y=170)
status = Label(root3, text="Ready to Help You!!!", bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)

root3.mainloop()