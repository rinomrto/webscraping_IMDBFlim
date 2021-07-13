  
from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find("div",attrs={"lister-list"})
row = table.find_all("div",attrs={"lister-item mode-advanced"})

row_length = len(row)

temp = [] #initiating a list 

for ListMovie in row:
    
    #get movie title
    Title = ListMovie.h3.a.text
        
    #get movie rating
    Rating = ListMovie.find('div', class_ = 'inline-block ratings-imdb-rating').text.replace('\n','') if ListMovie.find('div', class_ = 'inline-block ratings-imdb-rating') else '0' 
    
    #get metascore
    Metascore = ListMovie.find('span', class_= 'metascore').text.replace(' ','') if ListMovie.find('span', class_= 'metascore') else '0'
    
    #get votes 
    Votes = ListMovie.find('span', attrs = {'name': "nv"}).text if ListMovie.find('span', attrs = {'name': "nv"}) else '0'
    
    
    temp.append((Title,Rating,Metascore,Votes))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=('Title','Rating','Metascore','Votes'))

#insert data wrangling here
#menghilangkan tanda baca koma "," pada kolom votes
df["Votes"] = df["Votes"].str.replace(",","")

#Mengubah Type Data Rating menjadi Float '
df["Rating"] = df["Rating"].astype("float64")

#Mengubah Type Data Votes' , 'Metascore' Menjadi Int
df[["Votes","Metascore"]] = df[["Votes","Metascore"]] .astype("int64")
top = df.groupby('Title').sum()[["Rating"]].sort_values(by="Rating",ascending=False)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{top["Rating"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = top.head(10).sort_values(by="Rating",ascending=True).plot(kind="barh",xlabel="Film",ylabel="Value").plot(figsize = (22,10)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)