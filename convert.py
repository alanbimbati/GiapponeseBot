import xlwt

filer = open("database.txt").readlines()

book = xlwt.Workbook()
sheet = book.add_sheet("database")

sheet.write(0,0,"Italiano")
sheet.write(0,1,"Romaji")
sheet.write(0,2,"Hiragana")
sheet.write(0,3,"Kanji")
sheet.write(0,4,"Libro")
sheet.write(0,5,"Lezione")
sheet.write(0,6,"Tag")


i=1
for row in filer:
	campi = row.split(", ")
	for campo in campi:
		elemento = campo.split(":")
		print(elemento)
		if elemento[0]=="Italiano":
			sheet.write(i,0,elemento[1])
		elif elemento[0]=="Romaji":
			sheet.write(i,1,elemento[1])
		elif elemento[0]=="Hiragana":
			sheet.write(i,2,elemento[1])
		elif elemento[0]=="Kanji":
			sheet.write(i,3,elemento[1])
		elif elemento[0]=="libro":
			sheet.write(i,4,elemento[1])
		elif elemento[0]=="lezione":
			sheet.write(i,5,elemento[1])
		elif elemento[0]=="tag":
			sheet.write(i,6,elemento[1])
	i=i+1

book.save("database.csv")