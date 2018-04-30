#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
import datetime, time, math, matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

from PIL import Image, ImageTk


#%%
def on_closing():
    root.destroy()
    print('Thank you for using our retirement calculator\n')
    exit(0)

def clearAll():
    for element in entryList:
        element.delete(0,END) 
        element.config(bg='white')
    
    resultsFrame.grid_forget()
    detailed.delete(*detailed.get_children())
    status.grid_forget()
    
    
def check():
    success = True

    for element in entryList:        
        try: 
            float(element.get())
            element.config(bg='white')
            
        except ValueError:
            element.config(bg ='IndianRed2')
            success=False
            
    for element in interestList:
        if float(element.get()) > 50 or float(element.get()) <-50:
            element.config(bg ='IndianRed2')
            success=False
    
    try:
        if float(currentAge.get())>float(retirementAge.get()):
            currentAge.config(bg ='IndianRed2')
            retirementAge.config(bg ='IndianRed2')
            success=False
    except: pass
    
    #make sure all ages are positive numbers
    for x in [currentAge, ret_length, retirementAge]:
        
        try:
            if float(x.get())<0:
                x.config(bg ='IndianRed2')
                success=False
        except ValueError:
            x.config(bg ='IndianRed2')
            success=False
            
        
    return success


def saveDefault():
    output = open("rt_defaults.txt", 'w') #overwrite method
    for element in entryList:
        toPrint = element.get()
        toPrint = toPrint.replace(' ','')
        toPrint = toPrint.replace('\n', '')
        output.write(toPrint+'\n')
    output.close()
    status.grid(row=5, column =3)


def setDefault():
    class invalidDefault(Exception):
        pass
    
    clearAll()
    
    #getdefault values
    try: 
        defaultFile = open("rt_defaults.txt", 'r')
        content = defaultFile.readlines()
        for entry in content:
            string = entry.rstrip('\n')
            float(string)
            if string == '':
                raise invalidDefault
    
        defaultFile.seek(0)
        for element in entryList:
            val = next(defaultFile).rstrip('\n')
            element.insert(0, val)    
        defaultFile.close()

    #default values if no default file or error
    except (FileNotFoundError, ValueError, invalidDefault):
        currentAssets.insert(0, 55000)
        currentAge.insert(0, 24)
        salary.insert(0, 80000)
        monthlySvg.insert(0,2000)
        retirementAge.insert(0,45)
        ret_length.insert(0,45)
        interestRate.insert(0,7.0)
        interestRateAfter.insert(0,3.0)
        salRaise.insert(0,1.5)
        expense.insert(0,0.5)
#%%

def createChart(ageArray, assets, yearsWorking):    
    
    font_size = 7
    ratio = 1/1.4
    fig_size = (4*ratio,3*ratio)
    
    #create or clear the current figure:
    if plt.get_fignums()==[]:
        plt.figure(figsize = fig_size)
    else:
        plt.clf()
        
    ax = plt.subplot(111)
    plt.plot(ageArray[0:yearsWorking], assets[0:yearsWorking], label='Before retirement')
    plt.plot(ageArray[yearsWorking-1:len(ageArray)], assets[yearsWorking-1:len(assets)], label='After retirement')
    plt.ylabel('Savings ($)', fontsize = font_size)
    plt.xlabel('Age (yr)', fontsize = font_size)
    plt.legend(fontsize = font_size-2)
    ax.xaxis.set_tick_params(labelsize=font_size-2)
    ax.yaxis.set_tick_params(labelsize=font_size-2)
    axes = plt.gca()
    axes.set_xlim([math.floor(ageArray[0]/5.0)*5, math.ceil(max(ageArray)/5.0)*5])
    axes.set_ylim([0, math.ceil(max(assets)/500000.0)*500000])
    plt.grid(b=True)
    plt.tight_layout()
    
    #converting figure into an image for easy display
    image = plt.savefig('assetChart.png', dpi=200)
    image = Image.open("assetChart.png")
    photo = ImageTk.PhotoImage(image)
    chart.config(image=photo)
    chart.image = photo
    
    #display the figure
    chart.grid(row=1, column=0)
    resultsFrame.grid(row=2)
    
def createDetailed(ageArray, assets, yearsWorking, cashFlow, earnedInterest):
    detailed.delete(*detailed.get_children())
    i = 0
    while ageArray[i]-ageArray[0]< yearsWorking:
        detailed.insert('','end', text = str(ageArray[i]), values = (assets[i], cashFlow[i], earnedInterest[i], assets[i+1]))
        i=i+1
        
    while ageArray[i]< ageArray[len(ageArray)-1]:
        detailed.insert('','end', text = str(ageArray[i]), values = (assets[i], cashFlow[i], earnedInterest[i], assets[i+1]))
        i=i+1

def writeSummary(ageArray, assets, yearsWorking):
    summary.config(text=' ')
    sal = float(salary.get())
    contributions = round(float(monthlySvg.get()),2)
    costs = round(sal/12 - float(monthlySvg.get()),2)
    retYear = str(datetime.datetime.today().year+yearsWorking-1)
    #delete previous summary
    today = 'Today, you are ' + str(ageArray[0]) + ' years old with '+\
            '${:,.2f}'.format(assets[0]) + ' in total savings.\n\n'
     
    if float(salRaise.get())<0: change = 'a salary reduction of ' + str(abs(float(salRaise.get()))) + '%'
    elif float(salRaise.get())>0: change = 'a raise of ' + salRaise.get() + '%'
    else: change = 'no changes in salary '
    current = 'You are making '+ '${:,.2f}'.format(sal) + ' a year with ' +\
              change + ' every year. You contribute ' +'${:,.2f}'.format(contributions) +\
              ' a month to your savings, and have '+ '${:,.2f}'.format(costs) +\
              ' in monthly expenses. ' + 'Your savings appreciate at ' +interestRate.get()+\
              '% a year until you retire.\n\n'
    
    retire = 'You retire at age ' + retirementAge.get() + ' in year ' + retYear +\
             ', with ' + '${:,.2f}'.format(assets[yearsWorking-1]) + ' in total savings. \n'
    
    if float(expense.get())<0: change = 'reduce by ' + str(abs(float(expense.get()))) +'%'
    elif float(expense.get())>0: change = 'increase by ' +expense.get() + '%'
    else: change = 'stay constant'
    
    postRetire= 'After retirement, your savings appreciate at ' +interestRateAfter.get() +\
                '% a year. Your expenses '+change+ ' annually. \n'
                
    finalAgeIndex = next((i for i, asset in enumerate(assets) if asset<0), None)
    
    if finalAgeIndex!=None:
        end = 'Your retirement ends at age ' + str(ageArray[finalAgeIndex-1]) +\
              ' when your assets reach $0.'
    else:
        end = 'You successfully retire until age ' + str(ageArray[len(ageArray)-1]) +\
              ', ending with '+ '${:,.2f}'.format(assets[len(assets)-1]) +\
              ' in total savings.'
    
    string = '\n'+today + current+retire+postRetire+end + '\n'*3
    
    summary.config(text=string)
    summary.pack(fill=BOTH)
    
    
def calculate():
    status.grid_forget()
    if check():
        age = int(float(currentAge.get()))
        year =0
        
        netSal = int(float(monthlySvg.get())*12)
        anRaise = float(salRaise.get())/100.0
        cost = int(float(salary.get()) - netSal)
        inCost = float(expense.get())/100.0
        interest = float(interestRate.get())/100.0
        retAge = int(float(retirementAge.get()))
        finalAge = retAge+int(float(ret_length.get()))
        

        ageArray=[age]
        assets =[int(currentAssets.get())]
        cashFlow=[netSal]
        earnedInterest =[int((assets[0]+netSal)*interest)]
        
        while age< retAge:
            year=year+1
            age=age+1
            netSal= int(netSal*(1+anRaise))
            cashFlow.insert(len(cashFlow), netSal)
            principle = (assets[year-1]+netSal)
            earnedInterest.insert(len(earnedInterest),int(principle*interest))
            total = principle + earnedInterest[year]
            ageArray.insert(len(ageArray), age)
            assets.insert(len(assets), round(total,0))
            
            
        yearsWorking = age- int(float(currentAge.get()))+1
        interest = float(interestRateAfter.get())/100.0
        
        while age< finalAge:
            year=year+1
            age=age+1
            cost=int(cost*(1+inCost))
            cashFlow.insert(len(cashFlow), -cost)
            principle = (assets[year-1]-cost)
            earnedInterest.insert(len(earnedInterest),int(principle*interest))
            total = principle + earnedInterest[year]
            ageArray.insert(len(ageArray), int(age))            
            assets.insert(len(assets), int(total))
        
        createChart(ageArray, assets, yearsWorking)
        createDetailed(ageArray, assets, yearsWorking, cashFlow, earnedInterest)
        writeSummary(ageArray, assets, yearsWorking)        
    else:
        pass
        
        
#%%
entryList = []
interestList = []

root=Tk()
root.title("Retirement Calculator")
root.config(borderwidth=2)

optionsFrame = Frame(root)
optionsFrame.config(borderwidth=7)
optionsFrame.grid(row=0, sticky='w')

textWidth = 8
#Current Assets entry box creation
currentAssets_label = Label(optionsFrame, text='Current Savings ($)')
currentAssets_label.grid(row=0, column=0)
currentAssets = Entry(optionsFrame, width =textWidth)
currentAssets.grid(row=0, column=1)
entryList.insert(len(entryList), currentAssets)

#current age entry box creation
currentAge_label = Label(optionsFrame, text='Current Age')
currentAge_label.grid(row=0, column =2)
currentAge = Entry(optionsFrame, width =textWidth)
currentAge.grid(row=0, column=3)
entryList.insert(len(entryList), currentAge)

#Yearly income
salary_label =Label(optionsFrame, text='Salary ($/yr)')
salary_label.grid(row=1, column=0)
salary=Entry(optionsFrame, width =textWidth)
salary.grid(row=1, column=1)
entryList.insert(len(entryList), salary)

#Monthly Savings
monthlySvg_label = Label(optionsFrame, text='Monthly Savings ($)')
monthlySvg_label.grid(row=1, column=2)
monthlySvg = Entry(optionsFrame, width =textWidth)
monthlySvg.grid(row=1, column=3)
entryList.insert(len(entryList), monthlySvg)

#retirement age box creation
retirementAge_label = Label(optionsFrame, text='Retirement Age (year)')
retirementAge_label.grid(row=2, column=0)
retirementAge = Entry(optionsFrame, width =textWidth)
retirementAge.grid(row=2, column = 1)
entryList.insert(len(entryList), retirementAge)

#retirement length box creation
ret_length_label = Label(optionsFrame, text = 'Retirement Length')
ret_length_label.grid(row=2, column = 2)
ret_length = Entry(optionsFrame, width=textWidth)
ret_length.grid(row=2, column = 3)
entryList.insert(len(entryList), ret_length)

#interest rate before
interestRate_label = Label(optionsFrame, text='Interest rate before\n retirement (%)')
interestRate_label.grid(row=3, column = 0, rowspan=2)
interestRate = Spinbox(optionsFrame, from_=0, to=20, width = textWidth-1, increment =.5)
interestRate.grid(row=3, column=1)
entryList.insert(len(entryList), interestRate)
interestList.insert(len(entryList), interestRate)

#interest rate after
interestRate_after_label = Label(optionsFrame, text='Interest rate after\n retirement (%)')
interestRate_after_label.grid(row=3, column = 2, rowspan=2)
interestRateAfter = Spinbox(optionsFrame, from_=0, to=20, width = textWidth-1, increment =.5)
interestRateAfter.grid(row=3, column=3)
entryList.insert(len(entryList), interestRateAfter)
interestList.insert(len(entryList), interestRateAfter)

#Advanced Options
advOptions = LabelFrame(optionsFrame, text = 'Advanced Options')
advOptions.grid(row=0, column =4, rowspan = 6, sticky='n')

promo = Label(advOptions, text = 'Annual salary change (%)')
promo.grid(row=0, sticky='w')
salRaise = Spinbox(advOptions, from_=-20, to=20, width = 4, increment=.5)
salRaise.grid(row=0, column =1)
entryList.insert(len(entryList), salRaise)
interestList.insert(len(entryList), salRaise)

costAccum = Label(advOptions, text ='Annual post-retirement\nexpense change (%)')
costAccum.grid(row=1, sticky='w')
expense = Spinbox(advOptions, from_=-20, to=20, width = 4, increment =.5)
expense.grid(row=1, column=1,sticky='w')
entryList.insert(len(entryList), expense)
interestList.insert(len(entryList), expense)

#reset button 
dispText = 'Reset Default'
resetButton = Button(optionsFrame, command = setDefault, text = dispText, width = len(dispText))
resetButton.grid(row=5, column=0)
#clear all button 
dispText = 'Clear all'
clearButton = Button(optionsFrame, text = dispText, command = clearAll, width = len(dispText))
clearButton.grid(row = 5, column = 1)

#save options as default
dispText='Save Default'
default = Button(optionsFrame, command = saveDefault, text = dispText, width=len(dispText))
default.grid(row=5, column = 2)
status = Label(optionsFrame, text= 'Default Saved', fg ='red', font=("Times", 12))

#calculate button 
calc = Button(optionsFrame, text ='Calculate', command = calculate, width = 20, height =2)
calc.grid(row = 5, column = 4, columnspan=3)


#creates the results frame for the chart, detailed, and summary
resultsFrame = ttk.Notebook(root)
chartFrame = ttk.Frame(resultsFrame)
detailFrame = ttk.Frame(resultsFrame)
summaryFrame = ttk.Frame(resultsFrame)

resultsFrame.add(chartFrame, text = "Chart")
resultsFrame.add(detailFrame, text = "Detailed")
resultsFrame.add(summaryFrame, text = "Summary")

resultsFrame.grid(row=1, stick='ne', columnspan =2)
resultsFrame.grid_columnconfigure(0,weight=1)

#creates the chart frame
chart = Label(chartFrame)

#creates the detailed frame and headers
detailed = ttk.Treeview(detailFrame, height = 23)
detailed['columns'] = ('start', 'cashflow', 'interest', 'eoy')
detailed.grid(row=0)
setWidth = 127
detailed.heading("#0", text='Year', anchor='w')
detailed.column("#0", anchor="w", width = int(setWidth/2))
detailed.heading('start', text='Opening ($)', anchor='w')
detailed.column('start', anchor='w', width=setWidth)
detailed.heading('cashflow', text='Net Cash Flow ($)', anchor='w')
detailed.column('cashflow', anchor='w', width=setWidth)
detailed.heading('interest', text='Interest Earned ($)', anchor='w')
detailed.column('interest', anchor='w', width=setWidth)
detailed.heading('eoy', text='End of Year ($)', anchor='w')
detailed.column('eoy', anchor='w', width=setWidth)

#creates the summary frame
summary = Message(summaryFrame, font =("Helvetica", 18), aspect=100)

setDefault()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()