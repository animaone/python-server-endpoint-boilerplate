import json

testMode = False
if testMode:
	sourceFileName = 'source-sample.json'
else:
	sourceFileName = 'source-2.json'

sourceFile = open(sourceFileName, "r", encoding="utf-8")
sourceData = json.load(sourceFile)

minlon = -46.693419
minlat = -23.568704
maxlon = -46.641146
maxlat = -23.546686
def isInBoundingBox(item):
	lon = item['address']['geoLocation']['location']['lon']
	lat = item['address']['geoLocation']['location']['lat']
	if lon < minlon:
		return False
	if lon > maxlon:
		return False
	if lat < minlat:
		return False
	if lat > maxlat:
		return False
		
	return True
	
def isLatLonNull(item):
	lon = item['address']['geoLocation']['location']['lon']
	lat = item['address']['geoLocation']['location']['lat']
	if lon == 0 and lat == 0:
		return False	

def isZAP(item):
	#Um imóvel não é elegível em NENHUM PORTAL se:
	#Ele tem lat e lon iguais a 0.
	if isLatLonNull(item):
		return False
		
	#Ele apenas é elegível pro portal ZAP:
	#Quando for aluguel e no mínimo o valor for de R$ 3.500,00.
	#Quando for venda e no mínimo o valor for de R$ 600.000,00.
	isSale = item['pricingInfos']['businessType'] == 'SALE'
	isRental = item['pricingInfos']['businessType'] == 'RENTAL'
	price = item['pricingInfos']['price']
	price = float(price)
	if isRental:
		if price < 3500:
			return False
	elif isSale:
		if price < 600000:
			return False
			
		#Caso o imóvel seja para venda, ele é elegível para o portal ZAP se:
		#O valor do metro quadrado (chave usableAreas) não pode ser menor/igual a R$ 3.500,00 - apenas considerando imóveis que tenham usableAreas acima de 0 (imóveis com usableAreas = 0 não são elegíveis).
		#Quando o imóvel estiver dentro do bounding box dos arredores do Grupo ZAP (descrito abaixo) considere a regra de valor mínimo (do imóvel) 10% menor.
		usableAreas = item['usableAreas']
		isInBox = isInBoundingBox(item)
		if(isInBox):
			#valor mínimo 10% menor = 3500 - (3500*0.1)
			if usableAreas <= 3150:
				return False
		else:
			if usableAreas <= 3500:
				return False
					
	#O IMÓVEL É ELEGÍVEL para o portal ZAP
	return True		

def isVIVAREAL(item):
	#Um imóvel não é elegível em NENHUM PORTAL se:
	#Ele tem lat e lon iguais a 0.
	if isLatLonNull(item):
		return False
		
	#Ele apenas é elegível pro portal Viva Real:
	#Quando for aluguel e no máximo o valor for de R$ 4.000,00.
	#Quando for venda e no máximo o valor for de R$ 700.000,00.
	isSale = item['pricingInfos']['businessType'] == 'SALE'
	isRental = item['pricingInfos']['businessType'] == 'RENTAL'
	price = item['pricingInfos']['price']
	price = float(price)
	if isRental:
		#Quando o imóvel estiver dentro do bounding box dos arredores do Grupo ZAP (descrito abaixo) considere a regra de valor máximo (do aluguel do imóvel) 50% maior.
		isInBox = isInBoundingBox(item)
		if(isInBox):
			#4000 + (4000 * 0.5)
			if price > 6000:
				return False
		else:
			if price > 4000:
				return False

		#Caso o imóvel seja para aluguel, ele é elegível para o portal Viva Real se:
		#O valor do condomínio não pode ser maior/igual que 30% do valor do aluguel - apenas aplicado para imóveis que tenham um monthlyCondoFee válido e numérico (imóveis com monthlyCondoFee não numérico ou inválido não são elegíveis).
		if not 'monthlyCondoFee' in item['pricingInfos']:
			return False
				
		rental30Percent = 0.3 * price
		monthlyCondoFee = item['pricingInfos']['monthlyCondoFee']
		monthlyCondoFee = float(monthlyCondoFee)
		
		if monthlyCondoFee >= rental30Percent:
			return False
			
	elif isSale:
		if price > 700000:
			return False	
		
	#O IMÓVEL É ELEGÍVEL para o portal VivaReal
	return True	
	
def getItem(gname):
	items = []
	gname = gname.lower()
	checkFunction = None
	
	if gname == 'zap':
		checkFunction = isZAP	
	elif gname == 'vivareal':
		checkFunction = isVIVAREAL
		
	if checkFunction == None:
		return None
	else:
		for item in sourceData:
			if(checkFunction(item)):
				items.append(item)
	
	return items
						
if __name__ == '__main__':
	print("Testing Zap...")
	items = getItem('zap')
	print('Zap. Number of items:',len(items))
	
	print("\n\n")
	
	print("Testing VivaReal...")
	items = getItem('vivareal')
	print('VivaReal. Number of items:',len(items))

	#print(json.dumps(item, sort_keys=True, indent=4))
