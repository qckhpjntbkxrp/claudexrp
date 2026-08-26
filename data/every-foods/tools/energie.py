# kcal je 100 g bzw. je Stueck - Einkaufszustand (Trockenware trocken!)
KCAL={'Berglinsen':340,'Rote Linsen':340,'Belugalinsen':340,'Kichererbsen trocken':360,
'Weisse Bohnen':330,'Kidneybohnen':330,'Schwarze Bohnen':340,'Kefen / Erbsen TK':81,
'Haferflocken':370,'Vollkornreis':350,'Hirse':360,'Quinoa':370,'Buchweizen':350,
'Polenta / Maisgriess':360,'Bulgur':350,'Vollkornpasta':350,'Vollkornmehl':340,
'Baumnuesse':654,'Mandeln':579,'Haselnuesse':628,'Cashews':553,'Kuerbiskerne':559,
'Sonnenblumenkerne':584,'Hanfsamen geschaelt':553,'Leinsamen ganz':534,'Sesam / Tahini':595,
'Paranuesse':659,'Tofu natur':120,'Tofu geraeuchert':150,'Tempeh':190,'Seitan':140,
'Huettenkaese / Skyr':70,'Eier':70,'Halloumi / Feta':280,'Sauerkraut roh':20,'Kimchi':30,
'Kefir':55,'Naturjoghurt':60,'Miso hell/dunkel':199,'Rohmilchkaese (Bergkaese, Gruyere)':400,
'Spinat':23,'Federkohl / Gruenkohl':45,'Nuesslisalat':21,'Mangold':19,'Rucola':25,'Petersilie':36,
'Broccoli':34,'Blumenkohl':25,'Rosenkohl':43,'Weiss- / Rotkohl':25,'Wirz':27,'Kohlrabi':27,
'Radieschen':16,'Ruebli':41,'Randen':43,'Pastinaken':75,'Sellerieknolle':42,
'Kartoffeln festkochend':77,'Suesskartoffeln':86,'Kuerbis':40,'Zwiebeln':40,'Knoblauch':45,
'Lauch':61,'Schalotten':72,'Ingwer':80,'Kurkuma frisch':80,'Beeren TK gemischt':40,
'Beeren frisch':45,'Aepfel':52,'Birnen':57,'Zitrusfruechte':45,'Bananen':89,
'Steinobst saisonal':50,'Trauben':69,'Champignons':22,'Austernpilze':33,'Shiitake frisch':34,
'Kraeuterseitlinge':35,'Shiitake getrocknet (UV)':296,'Steinpilze getrocknet':300,
'Olivenoel extra vergine':900,'Rapsoel HOLL':900,'Leinoel':900,'Butter':740,
'Jodiertes Salz':0,'Schwarzer Pfeffer ganz':250,'Kurkuma gemahlen':350,'Kreuzkuemmel':375,
'Koriandersamen':300,'Paprika edelsuess/geraeuchert':280,'Zimt (Ceylon)':250,'Fenchelsamen':345,
'Senfkoerner':508,'Getrocknete Kraeuter (Oregano, Thymian, Rosmarin, Lorbeer)':280,
'Chiliflocken':300,'Tomaten gehackt (Dose)':72,'Tomatenmark':82,'Kokosmilch':788,
'Sojasauce / Tamari':53,'Apfelessig':21,'Balsamico':88,'Senf':100,'Hefeflocken':350,
'Nori-Blaetter':350,'Wakame getrocknet':300,'Dunkle Schokolade 70%+':580,'Gruentee':0,
'Sprossensamen (Alfalfa, Broccoli, Linsen)':350,'Spinat TK':23,'Broccoli TK':34,
'Huelsenfruechte vorgekocht (Eigenproduktion)':0,'Vollkornbrot in Scheiben':230,
'Gemuesebruehe / Pesto in Eiswuerfeln':0,'Algenoel (EPA/DHA)':9,'Vitamin D3 (vegan, Flechte)':0,
'paprika_rot':31,'staerke':350,'sojabohnenkerne':122,'planted_pulled':160,'pak_choi':13,
'wasserkastanien':97,'kandierter_ingwer':350,'zitronengras':99,'kokosflocken':660,'tomatensaft':17}
STK={'Eier':60,'Knoblauch':50,'Tomaten gehackt (Dose)':400,'Kokosmilch':400,
     'Algenoel (EPA/DHA)':1,'Vitamin D3 (vegan, Flechte)':0.5}
def kcal(name,menge,einh):
    k=KCAL.get(name)
    if k is None: return 0.0
    g = menge*STK.get(name,100) if einh in ('Stk','Kaps') else menge
    return k*g/100
